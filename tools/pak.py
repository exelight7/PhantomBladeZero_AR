"""Read/write the unencrypted, uncompressed Unreal PAK v11 format used by this mod."""
import hashlib
import struct
from pathlib import Path, PurePosixPath

MAGIC = 0x5A6F12E1
FOOTER_SIZE = 221
ENTRY_SIZE = 53
ENCODED_FLAGS = 0xE0000000


def _sha(data):
    return hashlib.sha1(data).digest()


def _string(value):
    data = value.encode("ascii") + b"\0"
    return struct.pack("<i", len(data)) + data


def _read_string(data, offset):
    size, = struct.unpack_from("<i", data, offset)
    offset += 4
    if size <= 0 or offset + size > len(data) or data[offset + size - 1] != 0:
        raise ValueError("Invalid PAK index string")
    return data[offset:offset + size - 1].decode("ascii"), offset + size


def _checked_slice(data, offset, size, digest):
    if offset < 0 or size < 0 or offset + size > len(data):
        raise ValueError("PAK section is outside the file")
    section = data[offset:offset + size]
    if _sha(section) != digest:
        raise ValueError("PAK checksum mismatch")
    return section


def read_pak(path):
    """Return all files after verifying the payloads and three indexes.

    Deliberately reject other PAK variants rather than guessing their layout.
    """
    data = Path(path).read_bytes()
    if len(data) < FOOTER_SIZE:
        raise ValueError("Truncated PAK")
    footer = data[-FOOTER_SIZE:]
    magic, version, offset, size = struct.unpack_from("<IIQQ", footer, 17)
    if magic != MAGIC or version != 11 or any(footer[:17]):
        raise ValueError("Expected an unencrypted PAK v11")
    primary = _checked_slice(data, offset, size, footer[41:61])
    mount, cursor = _read_string(primary, 0)
    if mount != "../../../":
        raise ValueError("Unexpected PAK mount point")
    count, seed = struct.unpack_from("<IQ", primary, cursor)
    cursor += 12
    if seed != 0:
        raise ValueError("Unsupported PAK path hash seed")
    indexes = []
    for _ in range(2):
        present, offset, size = struct.unpack_from("<IQQ", primary, cursor)
        if present != 1:
            raise ValueError("Missing PAK secondary index")
        indexes.append(_checked_slice(data, offset, size, primary[cursor + 20:cursor + 40]))
        cursor += 40
    encoded_size, = struct.unpack_from("<I", primary, cursor)
    cursor += 4
    encoded = primary[cursor:cursor + encoded_size]
    if encoded_size != count * 12 or primary[cursor + encoded_size:] != b"\0" * 4:
        raise ValueError("Unsupported PAK encoded entry layout")
    directory = indexes[1]
    directory_count, = struct.unpack_from("<I", directory)
    cursor = 4
    files = {}
    for _ in range(directory_count):
        parent, cursor = _read_string(directory, cursor)
        file_count, = struct.unpack_from("<I", directory, cursor)
        cursor += 4
        for _ in range(file_count):
            name, cursor = _read_string(directory, cursor)
            entry, = struct.unpack_from("<i", directory, cursor)
            cursor += 4
            if entry < 0 or entry % 12 or entry + 12 > len(encoded):
                raise ValueError("Invalid PAK entry reference")
            flags, offset, size = struct.unpack_from("<III", encoded, entry)
            if flags != ENCODED_FLAGS:
                raise ValueError("Compressed or large PAK entries are unsupported")
            header = data[offset:offset + ENTRY_SIZE]
            if len(header) != ENTRY_SIZE or struct.unpack_from("<QQQI", header) != (0, size, size, 0) or any(header[48:]):
                raise ValueError("Unexpected PAK entry header")
            key = ("" if parent == "/" else parent) + name
            if key in files:
                raise ValueError("Duplicate PAK file")
            files[key] = _checked_slice(data, offset + ENTRY_SIZE, size, header[28:48])
    if cursor != len(directory) or len(files) != count:
        raise ValueError("PAK directory count mismatch")
    return files


def write_pak(files, out):
    """Build a deterministic PAK with one or more relative file paths."""
    if not files:
        raise ValueError("Cannot write an empty PAK")
    payload = bytearray()
    encoded = bytearray()
    directories = {"/": []}
    hashes = []
    for path, content in files.items():
        pure = PurePosixPath(path)
        if pure.is_absolute() or ".." in pure.parts or str(pure) != path or "\\" in path or "\0" in path or path == ".":
            raise ValueError("PAK paths must be normalized relative paths")
        path.encode("ascii")
        if len(payload) >= 2**32 or len(content) >= 2**32:
            raise ValueError("PAK entry exceeds the supported 32-bit size")
        entry = len(encoded)
        encoded += struct.pack("<III", ENCODED_FLAGS, len(payload), len(content))
        payload += struct.pack("<QQQI", 0, len(content), len(content), 0) + _sha(content) + b"\0" * 5 + content
        for i in range(1, len(pure.parts)):
            directories.setdefault("/".join(pure.parts[:i]) + "/", [])
        parent = "/".join(pure.parts[:-1]) + "/" if len(pure.parts) > 1 else "/"
        directories[parent].append((pure.name, entry))
        value = 0xCBF29CE484222325
        for byte in path.lower().encode("utf-16-le"):
            value = ((value ^ byte) * 0x100000001B3) & ((1 << 64) - 1)
        if value in [h for h, _ in hashes]:
            raise ValueError("PAK path hash collision")
        hashes.append((value, entry))
    directory = struct.pack("<I", len(directories))
    for parent, entries in directories.items():
        directory += _string(parent) + struct.pack("<I", len(entries))
        for name, entry in entries:
            directory += _string(name) + struct.pack("<i", entry)
    path_hash = struct.pack("<I", len(hashes)) + b"".join(struct.pack("<Qi", h, e) for h, e in hashes) + b"\0" * 4
    mount = _string("../../../")
    primary_size = len(mount) + 12 + 80 + 4 + len(encoded) + 4
    path_offset = len(payload) + primary_size
    directory_offset = path_offset + len(path_hash)
    primary = (mount + struct.pack("<IQ", len(files), 0)
               + struct.pack("<IQQ", 1, path_offset, len(path_hash)) + _sha(path_hash)
               + struct.pack("<IQQ", 1, directory_offset, len(directory)) + _sha(directory)
               + struct.pack("<I", len(encoded)) + encoded + b"\0" * 4)
    footer = b"\0" * 17 + struct.pack("<IIQQ", MAGIC, 11, len(payload), len(primary)) + _sha(primary) + b"\0" * 160
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(payload + primary + path_hash + directory + footer)
    return out
