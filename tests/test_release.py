"""Regression checks for the translation and the standalone exelight7 PAK."""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import branding
import pak
import pbzlib
import prepare_release
from locres import parse

LOCRES_PATH = pbzlib.LOCRES_PATH


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / "overlay.pak"

    def test_multi_file_paths_match_original_game_hashes(self):
        files = {LOCRES_PATH: "النص العربي".encode("utf-16-le"), branding.MENU_PATH: b"// menu"}
        pak.write_pak(files, self.out)
        self.assertEqual(pak.read_pak(self.out), files)
        data = self.out.read_bytes()
        index_offset, index_size = struct.unpack_from("<QQ", data, len(data) - 196)
        primary = data[index_offset:index_offset + index_size]
        mount_size, = struct.unpack_from("<i", primary)
        present, offset, size = struct.unpack_from("<IQQ", primary, 4 + mount_size + 12)
        self.assertEqual(present, 1)
        self.assertEqual(size, 32)
        self.assertEqual(struct.unpack_from("<I", data, offset)[0], 2)
        # Golden path hashes extracted from the original mod, not from our writer.
        self.assertEqual(struct.unpack_from("<Qi", data, offset + 4), (0x9174C2E86E937273, 0))
        self.assertEqual(struct.unpack_from("<Qi", data, offset + 16), (0xE92244B36C03A1E1, 12))

    def test_corrupt_payload_and_index_are_rejected(self):
        pak.write_pak({LOCRES_PATH: b"localization", branding.MENU_PATH: b"menu"}, self.out)
        clean = self.out.read_bytes()
        index_offset, = struct.unpack_from("<Q", clean, len(clean) - 196)
        for offset in (53, index_offset + 5):
            with self.subTest(offset=offset):
                damaged = bytearray(clean)
                damaged[offset] ^= 1
                self.out.write_bytes(damaged)
                with self.assertRaisesRegex(ValueError, "checksum"):
                    pak.read_pak(self.out)

    def test_unsupported_or_truncated_archives_are_rejected(self):
        self.out.write_bytes(b"short")
        with self.assertRaisesRegex(ValueError, "Truncated"):
            pak.read_pak(self.out)
        pak.write_pak({"file": b"data"}, self.out)
        data = bytearray(self.out.read_bytes())
        data[-221 + 16] = 1
        self.out.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "unencrypted"):
            pak.read_pak(self.out)

    def test_unsafe_paths_are_rejected(self):
        for path in ("../outside", "/absolute", "a/../b", "a//b", "a\\b", "a\0b", "."):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    pak.write_pak({path: b"data"}, self.out)

    def test_branding_changes_only_the_existing_credit(self):
        original = pak.read_pak(pbzlib.SRC_PAK)[branding.MENU_PATH].decode("utf-8")
        result = branding.menu_override()[branding.MENU_PATH].decode("utf-8")
        self.assertEqual(original.count("عباديوه"), 2)
        self.assertEqual(result, original.replace("عباديوه", "exelight7"))
        self.assertIn('String(CurrentLanguage).startsWith("fr")', result)
        self.assertIn(' + " - تعريب exelight7"', result)

    def test_unexpected_upstream_credit_requires_review(self):
        with patch.object(branding, "read_pak", return_value={branding.MENU_PATH: b"changed upstream"}):
            with self.assertRaisesRegex(ValueError, "Original settings credit changed"):
                branding.menu_override()

    def test_merged_translation_and_menu_survive_build(self):
        original = pbzlib.load_original()
        before = original.texts()
        expected = dict(before)
        inputs = sorted((ROOT / "patches").glob("*.json")) + sorted((ROOT / "work").glob("*/out/*.json"))
        self.assertTrue(inputs)
        for path in inputs:
            for key, text in json.loads(path.read_text(encoding="utf-8")).items():
                errors, warnings = pbzlib.validate(before[key], text)
                self.assertEqual(errors, [], (path, key))
                self.assertEqual(warnings, [], (path, key))
                self.assertEqual(text.count("\n"), before[key].count("\n"), key)
                expected[key] = text
        menu = branding.menu_override()
        pbzlib.write_pak(original.apply(expected), self.out, extra_files=menu)
        files = pak.read_pak(self.out)
        base = pak.read_pak(pbzlib.SRC_PAK)
        # حزمة واحدة كاملة: كل ملفات المرجع موجودة، وملفان فقط تغيّرا.
        self.assertEqual(list(files), list(base))
        self.assertEqual({p for p in files if files[p] != base[p]}, {LOCRES_PATH, branding.MENU_PATH})
        self.assertEqual(files[branding.MENU_PATH], menu[branding.MENU_PATH])
        entries, strings, consumed = parse(files[LOCRES_PATH])
        self.assertEqual(consumed, len(files[LOCRES_PATH]))
        self.assertEqual({e[1]: strings[e[3]] for e in entries}, expected)
        self.assertEqual([e[:3] for e in entries], [e[:3] for e in original.entries])
        # لا أثر لاسم المودّ المرجعي داخل أي ملف من الحزمة المبنية.
        for name, content in files.items():
            for needle in ("عباديوه".encode(), b"3BADIOH", b"3badioh"):
                self.assertNotIn(needle, content, name)

    def test_extra_files_must_already_exist_in_base_package(self):
        with self.assertRaisesRegex(ValueError, "not part of the base package"):
            pbzlib.write_pak(b"locres", self.out, extra_files={"new/file.js": b"x"}, base_files={LOCRES_PATH: b"old"})
        with self.assertRaisesRegex(ValueError, "must not replace"):
            pbzlib.write_pak(b"locres", self.out, extra_files={LOCRES_PATH: b"x"}, base_files={LOCRES_PATH: b"old"})

    def test_release_files_use_the_exelight7_name(self):
        self.assertEqual(pbzlib.OUT_PAK.name, "exelight7_P.pak")
        self.assertEqual(prepare_release.NAMES, ("exelight7_P.pak", "exelight7_P.utoc", "exelight7_P.ucas"))
        self.assertEqual({p.suffix for p in prepare_release.SOURCES.values()}, {".pak", ".utoc", ".ucas"})
        for name, source in prepare_release.SOURCES.items():
            if name != prepare_release.NAMES[0]:
                self.assertTrue(source.is_file(), source)


if __name__ == "__main__":
    unittest.main()
