# دليل الملفات — من أين أبدأ؟

مستودع لتحسين تعريب **Phantom Blade Zero** (مودّ 3BADIOH): تصحيح الإملاء والصياغة والاتساق في 11,135 نصًا.

## أنا ... ماذا أفعل؟
| أنا | افعل |
|---|---|
| **لاعب** أريد التعريب فقط | ثبّت المودّ الأصلي من `original_mod/` (تعليمات صاحبه في `original_mod/README_3BADIOH.txt`)، ثم انسخ `release/ProjectPBZ/Content/Paks/~mods/ZZZ_3BADIOH_Fix_P.pak` إلى المجلد نفسه في اللعبة. للتراجع احذفه. |
| **مراجع** أريد المساهمة بالمراجعة | اقرأ `tasks/COMMON_RULES.md` ثم ملف مهمتك في `tasks/`. اعمل داخل `work/<اسمك>/` فقط. |
| **مطوّر** أريد إعادة البناء | `python tools/apply_patches.py` يدمج كل التصحيحات ويبني الـ pak في `release/`. |

يحتاج Python 3.10+ فقط (لا مكتبات خارجية).

## خريطة المجلدات
```
PhantomBladeZero_AR/
├── README.md               نظرة عامة سريعة
├── GUIDE.md                هذا الدليل
├── LICENSE                 MIT
│
├── original_mod/           المودّ الأصلي كما نُزّل (للمقارنة والتراجع). لا يُعدَّل
│   ├── ProjectPBZ/Content/Paks/~mods/3BADIOH_P.{pak,ucas,utoc}
│   └── README_3BADIOH.txt  تعليمات صاحب التعريب وروابطه
│
├── data/                   مستخرجات للقراءة (لا تُعدَّل)
│   ├── Game_locres_ar.json     كل النصوص: ns/key/hash/text (11,135)
│   ├── audit_report.txt        تقرير الفحص الآلي الأول
│   └── ucas_file_index.txt     فهرس 177 ملف واجهة داخل الحاوية (لا نصوص)
│
├── patches/                تصحيحات مقبولة نهائيًا { المفتاح: النص الجديد }
│   └── 00_auto_fixes.json      32 تصحيحًا آليًا (تنوين، كلمات إنجليزية، تكرار)
│
├── fixes/changes.txt       سجل بشري مقروء لتصحيحات 00_auto_fixes (قبل/بعد)
│
├── glossary/GLOSSARY.md    مسرد المصطلحات: مصدر الحقيقة الوحيد
│
├── tasks/                  تعليمات المراجعة للجلسات
│   ├── COMMON_RULES.md         القواعد المشتركة (اقرأها أولًا)
│   ├── TASK_CLAUDE.md          الحوارات والقراءات والمهمات (5,950 مدخلة)
│   └── TASK_OPENCODE.md        الواجهة والعناصر والأوصاف (4,819 مدخلة)
│
├── work/                   مساحة عمل الجلسات (لكل جلسة مجلد حصري)
│   ├── claude/   batches/ (مدخلات مولَّدة) · out/ (مخرجاتها) · STATE.md …
│   └── opencode/ batches/ · out/ · STATE.md …
│
├── tools/                  السكربتات
│   ├── pbzlib.py           المكتبة: قراءة locres، تطبيق تعديلات، كتابة pak
│   ├── split_tasks.py      يولّد work/*/batches من النص الحالي + patches
│   ├── apply_patches.py    يتحقق من التصحيحات ويدمجها ويبني الـ pak
│   ├── utoc.py, dirs.py    فك حاوية .utoc/.ucas (فحص فقط)
│   ├── locres.py, audit.py تحليل النص وفحصه آليًا (الجولة الأولى)
│   └── build.py            أول أداة بناء (استُبدلت بـ apply_patches)
│
└── release/                المخرجات المبنية
    ├── ProjectPBZ/Content/Paks/~mods/ZZZ_3BADIOH_Fix_P.pak
    └── apply_report.txt    تقرير آخر دمج (المقبول/المرفوض/التحذيرات)
```

## كيف يعمل المودّ (باختصار)
- النصوص في `Game.locres` داخل `3BADIOH_P.pak` (مسار اللغة الفرنسية؛ لذلك تُختار Français من إعدادات اللعبة).
- `.ucas/.utoc` فيهما 177 ملف واجهة وخط، ولا نصوص. لا تشفير في أي ملف.
- `ZZZ_3BADIOH_Fix_P.pak` يحمل `Game.locres` المعدَّل فقط، ويُحمَّل بعد الأصلي (الاسم يبدأ بـ ZZZ) فيتغلب عليه دون المساس بملفات المودّ.

## سير العمل الكامل
```
data/ + patches/  ──split_tasks.py──►  work/*/batches/   (مدخلات الجلسات)
                                            │  (الجلسة تحسّن وتكتب)
                                            ▼
                                       work/*/out/*.json   { key: نص محسَّن }
                                            │
patches/*.json + work/*/out/*.json ──apply_patches.py──► release/…/ZZZ_3BADIOH_Fix_P.pak
```
1. **تحقق دون بناء** (أي وقت): `python tools/apply_patches.py --dry [--only claude|opencode]`
2. **بناء**: `python tools/apply_patches.py` ← `release/apply_report.txt` يعدّد المقبول والمرفوض والتحذيرات.
3. المدخلة تُرفض آليًا إن تغيّرت الوسوم `<…>` أو العناصر `{…}` أو صارت فارغة أو لم يوجد مفتاحها؛ لا يُحقن شيء منها.
4. إعادة توليد الدفعات (تمسح `batches/` فقط، لا `out/`): `python tools/split_tasks.py`.
   ⚠️ إن أُعيد التوليد بعد بدء العمل تغيّرت أرقام الدفعات؛ لا تفعل ذلك أثناء المراجعة.

## ما الذي لم يُجرَّب
- الـ pak المبني **لم يُختبر داخل اللعبة بعد** (التحقق آلي بنيويًا فقط: تجزئات الفهرس، تطابق النصوص، تطابق باقي المدخلات بايت ببايت). جرّبه ببطء وأبلغ بأي مشكلة.

## حقوق
التعريب الأصلي لـ **3BADIOH** (روابطه في `original_mod/README_3BADIOH.txt`). هذا المستودع تصحيحات وأدوات فقط.
