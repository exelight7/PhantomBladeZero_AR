"""يدمج كل التصحيحات ويبني الـ pak:  patches/*.json ثم work/*/out/*.json  (كل ملف {key: نص جديد})
أي مدخلة تفشل في التحقق تُرفض وتُسجَّل في release/apply_report.txt ولا يُحقن شيء منها."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pbzlib
from branding import DISPLAY_NAME, menu_override


def main():
    # --dry: تحقق فقط بدون كتابة pak.  --only claude|opencode: افحص مخرجات جلسة واحدة فقط
    dry = "--dry" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    loc = pbzlib.load_original(); orig = loc.texts()
    root = pbzlib.ROOT
    files = [] if only else sorted((root / "patches").glob("*.json"))
    files += sorted((root / "work").glob(f"{only or '*'}/out/*.json"))
    patch, owner, rep = {}, {}, []
    for f in files:
        rel = f.relative_to(root).as_posix()
        for k, t in json.loads(f.read_text(encoding="utf8")).items():
            if k not in orig:
                rep.append(f"REJECT {rel} {k}: مفتاح غير موجود"); continue
            err, warn = pbzlib.validate(orig[k], t)
            if err:
                rep.append(f"REJECT {rel} {k}: {'; '.join(err)}"); continue
            rep += [f"WARN   {rel} {k}: {w}" for w in warn]
            if k in owner and not owner[k].startswith("patches/") and owner[k].split("/")[1] != rel.split("/")[1]:
                rep.append(f"CONFLICT {k}: {owner[k]} و {rel} (يفوز الأخير)")
            patch[k] = t; owner[k] = rel
    data = loc.apply(patch)
    # تحقق: إعادة القراءة؛ المفاتيح المعدَّلة فقط تغيّرت
    new = pbzlib.Locres(data).texts()
    assert set(new) == set(orig)
    bad = [k for k in orig if (new[k] != orig[k]) != (k in patch and patch[k] != orig[k])]
    assert not bad, bad[:5]
    changed = sum(1 for k in patch if patch[k] != orig[k])
    nrej = sum(r.startswith("REJECT") for r in rep); nwarn = sum(r.startswith("WARN") for r in rep)
    extra_files = menu_override()
    if dry:
        print(f"[dry] ملفات: {len(files)} | مقبولة: {changed} | مرفوضة: {nrej} | تحذيرات: {nwarn}")
        print("\n".join(r for r in rep if not r.startswith("WARN")) or "لا رفض ولا تعارض")
        if nwarn:
            print("\n".join([r for r in rep if r.startswith("WARN")][:15]))
        print(f"واجهة الإعدادات: تعريب {DISPLAY_NAME} (تم التحقق من ملف القائمة)")
        return
    out = pbzlib.write_pak(data, extra_files=extra_files)
    head = f"ملفات: {len(files)} | تعديلات مقبولة: {changed} | مرفوضة: {nrej} | تحذيرات: {nwarn} | pak: {out.relative_to(root).as_posix()}"
    (root / "release/apply_report.txt").write_text("\n".join([head, f"واجهة الإعدادات: تعريب {DISPLAY_NAME}"] + rep) + "\n", encoding="utf8")
    print(head)
    print("\n".join([r for r in rep if r.startswith(("REJECT", "CONFLICT"))][:20]))
    print("تفاصيل: release/apply_report.txt")


if __name__ == "__main__":
    main()
