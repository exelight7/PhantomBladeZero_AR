"""Prepare the offline installer payload and complete manual-install ZIP."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pbzlib import MOD_NAME, OUT_PAK, SRC_PAK  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MODS = Path("ProjectPBZ/Content/Paks/~mods")
NAMES = (f"{MOD_NAME}.pak", f"{MOD_NAME}.utoc", f"{MOD_NAME}.ucas")
# المصدر: الحزمة المبنية للملف الأول، وحاويتا الواجهة والخطوط من المرجع دون تعديل بايت واحد.
SOURCES = {NAMES[0]: OUT_PAK, NAMES[1]: SRC_PAK.with_suffix(".utoc"), NAMES[2]: SRC_PAK.with_suffix(".ucas")}
# أسماء الإصدارات السابقة؛ تُذكر هنا لتعليمات حذفها عند الترقية فقط.
RETIRED = ("3BADIOH_P.pak", "3BADIOH_P.utoc", "3BADIOH_P.ucas", "ZZZ_3BADIOH_Fix_P.pak")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checksums", action="store_true", help="Hash final release assets after building both apps")
    parser.add_argument("--pak-assets", action="store_true", help="Release only the three pak files and the manual ZIP (no EXE/AppImage)")
    args = parser.parse_args()
    version = json.loads((ROOT / "installer/package.json").read_text())["version"]
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    if args.checksums:
        if args.pak_assets:
            names = [*NAMES, f"PhantomBladeZero-AR-{version}-manual.zip"]
        else:
            names = [f"PhantomBladeZero-AR-{version}-manual.zip", f"PhantomBladeZero-AR-{version}-linux-x86_64.AppImage", f"PhantomBladeZero-AR-{version}-win-x64.exe"]
        for name in names:
            if not (dist / name).is_file():
                raise FileNotFoundError(f"Missing release asset: {name}")
        (dist / "SHA256SUMS.txt").write_text("".join(f"{digest(dist / name)}  {name}\n" for name in names), encoding="utf-8")
        print(f"Checksums verified for all {len(names)} release assets")
        return
    subprocess.run([sys.executable, "tools/apply_patches.py"], cwd=ROOT, check=True)
    payload = ROOT / "installer/payload"
    payload.mkdir(exist_ok=True)
    manifest = {"version": version, "files": []}
    for name in NAMES:
        source = SOURCES[name]
        target = payload / name
        shutil.copyfile(source, target)
        manifest["files"].append({"name": name, "size": target.stat().st_size, "sha256": digest(target)})
    (payload / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    instructions = f"""Phantom Blade Zero — التعريب العربي {version}
تحسينات exelight7

التثبيت اليدوي (حزمة واحدة كاملة من ثلاثة ملفات):
1. أغلق اللعبة، ثم فك ضغط هذه الحزمة.
2. من Steam: اضغط على اللعبة بالزر الأيمن > إدارة > تصفّح الملفات المحلية.
3. احذف أي تعريب عربي سابق من ProjectPBZ/Content/Paks/~mods (احتفظ بنسخة احتياطية إن شئت)، فلا يجتمع تعريبان معًا. الأسماء القديمة لهذا المشروع:
{chr(10).join(RETIRED)}
4. انسخ مجلد ProjectPBZ من هذه الحزمة إلى مجلد اللعبة ووافق على دمج المجلدات.
5. شغّل اللعبة. من شاشة البداية: Settings > Text Language > Français.
   الفرنسية هي خانة التعريب العربي. يظهر «تعريب exelight7» بجانب الإعدادات.

إزالة التثبيت اليدوي:
من ProjectPBZ/Content/Paks/~mods احذف الملفات الثلاثة التالية فقط، أو استعد نسختك الاحتياطية:
{chr(10).join(NAMES)}
لا تحذف مجلد ~mods أو ملفات أي مود آخر.

هذا الإصدار ({version}) ملفات pak فقط. تطبيق التثبيت (EXE لـ Windows وAppImage لـ Linux / Steam Deck) متاح في الإصدار 1.0.1:
https://github.com/exelight7/PhantomBladeZero_AR/releases/tag/1.0.1

التحقق: SHA256SUMS.txt يحتوي تجزئات الملفات داخل الحزمة.
اجتازت ملفات التعريب الفحوص الآلية؛ لم تُجرَّب هذه النسخة داخل اللعبة.

تعريب وتحسينات وأداة تثبيت: exelight7.
https://github.com/exelight7/PhantomBladeZero_AR
"""
    notice = (ROOT / "original_mod/README.txt").read_text(encoding="utf-8-sig")
    (payload / "NOTICE.txt").write_text("تعريب وتحسينات: exelight7.\n\n" + notice, encoding="utf-8")
    if args.pak_assets:
        for name in NAMES:
            shutil.copyfile(payload / name, dist / name)
    archive = dist / f"PhantomBladeZero-AR-{version}-manual.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for item in manifest["files"]:
            z.write(payload / item["name"], (MODS / item["name"]).as_posix())
        z.writestr("اقرأني - التثبيت.txt", instructions.encode("utf-8-sig"))
        z.writestr("SHA256SUMS.txt", "".join(f"{item['sha256']}  {(MODS / item['name']).as_posix()}\n" for item in manifest["files"]))
        z.write(payload / "NOTICE.txt", "NOTICE.txt")
        z.write(ROOT / "LICENSE", "LICENSE")
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("Manual ZIP integrity check failed")
        for item in manifest["files"]:
            assert hashlib.sha256(z.read((MODS / item["name"]).as_posix())).hexdigest() == item["sha256"]
    print(f"Prepared and verified: {archive.name} ({archive.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
