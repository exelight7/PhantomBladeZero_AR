"""مكتبة مشتركة: قراءة Game.locres من الـ pak الأصلي، تطبيق تعديلات، وكتابة pak جديد."""
import struct, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # كونسول ويندوز الافتراضي لا يطبع العربية

ROOT = Path(__file__).resolve().parent.parent
SRC_PAK = ROOT / "original_mod/ProjectPBZ/Content/Paks/~mods/3BADIOH_P.pak"
OUT_PAK = ROOT / "release/ProjectPBZ/Content/Paks/~mods/ZZZ_3BADIOH_Fix_P.pak"
LOC_OFFSET = 4077146  # بداية Game.locres داخل الـ pak (بعد ترويسة 53 بايت)
MAGIC = bytes.fromhex("0e14747567" "4a03fc4a15909dc3377f1b")
TAG = re.compile(r"<[^>]*>")
PH = re.compile(r"\{[^}]*\}")


def _fs(b, p):
    n, = struct.unpack_from("<i", b, p); p += 4
    if n < 0:
        n = -n; s = b[p:p + n * 2 - 2].decode("utf-16-le"); p += n * 2
    else:
        s = b[p:p + n - 1].decode("utf-8"); p += n
    return s, p


def _pack(s):
    if all(ord(c) < 128 for c in s):
        e = s.encode() + b"\0"; return struct.pack("<i", len(e)) + e
    e = (s + "\0").encode("utf-16-le"); return struct.pack("<i", -(len(e) // 2)) + e


class Locres:
    """entries: [ns, key, sourceHash, strIndex, posOfIndexField]؛ strs: [[text, refcount]]"""

    def __init__(self, b):
        assert b[:16] == MAGIC and b[16] == 3
        self.b = b
        self.aoff, = struct.unpack_from("<q", b, 17)
        p = 29
        nns, = struct.unpack_from("<I", b, p); p += 4
        self.entries = []
        for _ in range(nns):
            p += 4; ns, p = _fs(b, p)
            kc, = struct.unpack_from("<I", b, p); p += 4
            for _ in range(kc):
                p += 4; k, p = _fs(b, p)
                sh, idx = struct.unpack_from("<Ii", b, p)
                self.entries.append([ns, k, sh, idx, p + 4]); p += 8
        n, = struct.unpack_from("<I", b, self.aoff); p = self.aoff + 4
        self.strs = []
        for _ in range(n):
            s, p = _fs(b, p); rc, = struct.unpack_from("<i", b, p); p += 4
            self.strs.append([s, rc])
        assert p == len(b)

    def texts(self):
        return {e[1]: self.strs[e[3]][0] for e in self.entries}

    def apply(self, patch):
        """patch: {key: نص جديد}. تُلحق النصوص الجديدة بآخر المصفوفة وتُعاد فهرسة المفاتيح فقط."""
        b = bytearray(self.b[:self.aoff]); strs = [list(x) for x in self.strs]; new_idx = {}
        by_key = {e[1]: e for e in self.entries}
        for k, t in patch.items():
            e = by_key[k]
            if t == strs[e[3]][0]:
                continue
            if t not in new_idx:
                new_idx[t] = len(strs); strs.append([t, 0])
            strs[e[3]][1] -= 1; strs[new_idx[t]][1] += 1
            struct.pack_into("<i", b, e[4], new_idx[t])
        return bytes(b) + struct.pack("<I", len(strs)) + b"".join(_pack(s) + struct.pack("<i", max(rc, 0)) for s, rc in strs)


def load_original():
    f = SRC_PAK.read_bytes()
    size, = struct.unpack_from("<Q", f, LOC_OFFSET - 53 + 8)
    return Locres(f[LOC_OFFSET:LOC_OFFSET + size])


def validate(old, new):
    """يعيد (أخطاء مانعة تُرفض بسببها المدخلة، تحذيرات)."""
    err, warn = [], []
    if not isinstance(new, str):
        return ["ليس نصًا"], warn
    if old.strip() and not new.strip():
        err.append("نص فارغ بدل غير فارغ")
    if sorted(TAG.findall(old)) != sorted(TAG.findall(new)):
        err.append("اختلاف الوسوم <...>")
    if sorted(PH.findall(old)) != sorted(PH.findall(new)):
        err.append("اختلاف العناصر {...}")
    if old.count("\n") != new.count("\n"):
        warn.append("اختلاف عدد الأسطر")
    lat = lambda s: set(re.findall(r"[A-Za-z]{3,}", TAG.sub("", PH.sub("", s))))
    if lat(new) - lat(old):
        warn.append("كلمات لاتينية جديدة: %s" % sorted(lat(new) - lat(old)))
    return err, warn


def write_pak(locres_bytes, out=OUT_PAK, extra_files=None):
    from pak import write_pak as write_archive
    path = "ProjectPBZ/Content/Localization/Game/fr/Game.locres"
    files = {path: locres_bytes}
    if extra_files:
        if path in extra_files:
            raise ValueError("Extra files must not replace Game.locres")
        files.update(extra_files)
    return write_archive(files, out)
