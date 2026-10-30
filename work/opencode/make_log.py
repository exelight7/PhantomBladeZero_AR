"""يولّد fixes/ui-items.md: سجل قبل/بعد لكل مدخلة عدّلتها مراجعة الواجهة والأغراض والأسلحة.
يعرض الأجزاء المتغيّرة فقط (مع كلمات من السياق) حتى تبقى الأوصاف الطويلة مقروءة."""
import difflib, glob, json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(__file__).parent
ROOT = W.parents[1]
CTX = 4  # كلمات سياق على جانبي كل تغيير


def hunks(a, b):
    wa, wb = a.replace("\n", " ⏎ ").split(" "), b.replace("\n", " ⏎ ").split(" ")
    sm = difflib.SequenceMatcher(None, wa, wb, autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    merged = []
    for o in ops:
        if merged and o[1] - merged[-1][2] <= 2 * CTX:
            merged[-1] = (merged[-1][0], merged[-1][1], o[2], merged[-1][3], o[4])
        else:
            merged.append(o)
    out = []
    for _, i1, i2, j1, j2 in merged:
        lo, hi = max(0, i1 - CTX), min(len(wa), i2 + CTX)
        lo2, hi2 = max(0, j1 - CTX), min(len(wb), j2 + CTX)
        pre = "… " if lo > 0 else ""
        post = " …" if hi < len(wa) else ""
        out.append((pre + " ".join(wa[lo:hi]) + post, ("… " if lo2 > 0 else "") + " ".join(wb[lo2:hi2]) + (" …" if hi2 < len(wb) else "")))
    return [(x.replace(" ⏎ ", "⏎"), y.replace(" ⏎ ", "⏎")) for x, y in out]


def main():
    rows = []
    for f in sorted(glob.glob(str(W / "batches/batch_*.json"))):
        name = Path(f).name
        base = json.loads(Path(f).read_text(encoding="utf8"))
        out = json.loads((W / "out" / name).read_text(encoding="utf8"))
        num = int(name[6:10])
        for it in base:
            new = out.get(it["key"], it["text"])
            if new != it["text"]:
                rows.append((num, it["key"], it["text"], new))
    lines = [
        "# سجل مراجعة الواجهة والأغراض والأسلحة",
        "",
        "قراءة كاملة سطرًا سطرًا لنصوص الواجهة والأغراض والأسلحة والأسلحة الطيفية والحُلي والأدوية والوصف والأعداء والزعماء والدروس والإنجازات والمظهر وبقية ما يخص اللعبة (59 دفعة، 4,819 مدخلة). لم يُمسّ أي وسم أو `{}` أو عدد أسطر؛ يتحقق `tools/apply_patches.py` من ذلك قبل الحقن. يُعرض هنا الجزء المتغيّر فقط مع كلماته المجاورة.",
        "",
        f"المجموع: **{len(rows)}** مدخلة معدَّلة.",
        "",
        "## أنواع التعديل",
        "",
        "- **حرف دخيل**: حرف صيني داخل «كالنمر» في وصف زعيم (`BossNameDes_039`)، وتطويل زائد في «تركيز قبضة» بوصف سلاح.",
        "- **تنوين الفتح المنسي**: «طازجًا»، «ملكًا»، «محدقًا»، «عاجزًا»، «مرهقًا»، «أرضًا»، «حيًّا»، «رقيقًا»، «ملتوٍ».",
        "- **مطابقة النوع والعدد**: «محطمتين»، «انطلق سهمٌ»، «يجرؤ الرماد»، «هذا الرتابة←هذه»، «هذا النصل←ذلك»، «بضع جثث»، «الإخوة»، «لهجماتهن»، «تستطيع إنانيس»، «أجبرت الحداد»، «ذي الرداء الأرجواني».",
        "- **مدد زمنية**: «2 ثانية←ثانيتين» و«1 ثانية←ثانية واحدة» وتوحيد «أكثر من ضربتين متتاليتين» في وصف الحُلي والأدوية ومهارات الأسلحة.",
        "- **أسماء الأغراض**: توحيد الفاصل « · » في 21 اسمًا محسَّنًا/مصقولًا، وتوحيد «أسطرلاب» و«الفأس المروّع» و«الحقل» و«دار الثعبان الحمراء» و«الشق الطيفي الثلاثي».",
        "- **ترجمة خاطئة لمعنى**: «تأثيرات سلبية»←«تأثيرات تلقائية» (الأصل: سلبي بمعنى Passive لا Negative) في وصف الرموز السحرية، و«يميز اللهب←ينفث اللهب».",
        "- **ترقيم ومسافات**: مسافة بين وسمين متجاورين، ومسافات زائدة قبل الأسطر وبعد الفقرات، وتوحيد «لا تأثير له على الدمى» ومسار إعدادات ويندوز.",
        "",
        "## التفاصيل",
        "",
    ]
    for num, key, old, new in rows:
        lines.append(f"- `{key}` (دفعة {num:04d})  ")
        hs = hunks(old, new)
        for i, (x, y) in enumerate(hs):
            lines.append(f"  قبل: {x}  ")
            lines.append(f"  بعد: {y}" + ("  " if i < len(hs) - 1 else ""))
    (ROOT / "fixes/ui-items.md").write_text("\n".join(lines) + "\n", encoding="utf8")
    print("entries:", len(rows))


if __name__ == "__main__":
    main()
