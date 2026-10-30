# خريطة المشروع — أين أجد الحوارات والقوائم؟

[الفهرس الكامل لكل النصوص](text-index/README.md) يعرض كل مفتاح ونصه الحالي ورابط الدفعة التي تحتويه وملف التصحيح، إن وجد.

## الوصول السريع

| المطلوب | الفهرس الكامل | مكان العمل |
| --- | --- | --- |
| الحوارات، بحسب المنطقة والمشهد | [Dlg](text-index/Dlg.md) | [دفعات الحوارات](../work/claude/batches/) |
| كل القوائم والواجهة | [UI](text-index/UI.md) | [دفعات الواجهة](../work/opencode/batches/) |
| الإعدادات | [UI_Setting](text-index/UI.md#ui_setting) | نفس دفعات الواجهة |
| القائمة الرئيسية | [UI_StartMenu](text-index/UI.md#ui_startmenu) | نفس دفعات الواجهة |
| الحفظ والتحميل | [UI_SaveGame](text-index/UI.md#ui_savegame) · [UI_LoadGame](text-index/UI.md#ui_loadgame) | نفس دفعات الواجهة |
| الخريطة والمخزون | [UI_Map](text-index/UI.md#ui_map) · [UI_Inventory](text-index/UI.md#ui_inventory) | نفس دفعات الواجهة |
| نصوص القراءة وأوصافها | [Reading](text-index/Reading.md) · [ReadingDes](text-index/ReadingDes.md) | دفعات الحوارات |
| تعليمات اللعب | [Tutorial](text-index/Tutorial.md) | دفعات الواجهة |
| الأغراض والأسلحة | [Item](text-index/Item.md) · [Weapon](text-index/Weapon.md) · [WeaponDes](text-index/WeaponDes.md) | دفعات الواجهة |
| الشخصيات والأماكن | [Character](text-index/Character.md) · [Bell](text-index/Bell.md) | دفعات الواجهة |
| الأعداء والزعماء | [EnemyName](text-index/EnemyName.md) · [EnemyDesc](text-index/EnemyDesc.md) · [BossName](text-index/BossName.md) · [BossNameDes](text-index/BossNameDes.md) | دفعات الواجهة |
| المهارات | [PhantomEdges](text-index/PhantomEdges.md) · [PhantomEdgesDes](text-index/PhantomEdgesDes.md) | دفعات الواجهة |
| المهمات والشائعات والمتاهات | [كل فئات Quest في الفهرس](text-index/README.md) | دفعات الحوارات |

## خريطة المجلدات

```text
PhantomBladeZero_AR/
├── data/Game_locres_ar.json     النصوص الأصلية المستخرجة؛ ابحث باسم المفتاح
├── glossary/GLOSSARY.md        المصطلحات المعتمدة
├── patches/                   التصحيحات المعتمدة التي تدخل البناء
├── work/
│   ├── claude/batches/         الحوارات والقراءات والمهمات
│   ├── claude/out/             تصحيحات مراجعة الحوارات
│   ├── opencode/batches/       الواجهة والقوائم والأغراض والمهارات
│   └── opencode/out/           تصحيحات مراجعة الواجهة
├── tools/
│   ├── apply_patches.py        دمج التصحيحات وبناء الحزمة
│   ├── branding.py             اسم exelight7 بجانب زر الإعدادات
│   ├── project_map.py          تحديث هذا الفهرس الكامل
│   └── prepare_release.py      تجهيز الحزمة اليدوية وملفات التطبيق
├── installer/src/
│   ├── index.html             واجهة تطبيق التثبيت، وليست قوائم اللعبة
│   ├── style.css              تصميم التطبيق وألوانه
│   ├── renderer.js            تفاعل أزرار التطبيق
│   ├── main.cjs               اختيار المجلد والتواصل مع النظام
│   └── engine.cjs             التثبيت والنسخ الاحتياطي والاستعادة
├── original_mod/              المود الأساسي المرجعي
├── release/                   حزمة التصحيح المبنية وملاحظات الإصدار
└── docs/text-index/            الفهرس الكامل، ملف مستقل لكل فئة
```

## كيف تصل إلى حوار أو قائمة وتعدّلها؟

1. افتح فهرس الفئة أعلاه وابحث عن العبارة أو اسم المفتاح. يتكوّن مفتاح الحوار عادة من `Dlg_منطقة_مشهد_متكلم_رقم`.
2. افتح رابط «الدفعة» بجوار النص لقراءة السياق. راجع تعليمات المهمة والمسرد قبل التعديل.
3. اكتب التصحيح في ملف المخرجات المقابل داخل `work/<الجلسة>/out/`، أو في ملف تصحيحات معتمد داخل `patches/` عند دمج مراجعة نهائية. لا تعدّل المدخلات الأصلية أو تعِد توليد الدفعات أثناء المراجعة.
4. حافظ على الوسوم `<...>` والمتغيرات `{...}` وعدد الأسطر، ثم شغّل `python3 tools/apply_patches.py --dry`.
5. لتحديث الفهرس بعد تغيير التصحيحات: `python3 tools/project_map.py`.

دمج النصوص يتم بالترتيب: ملفات `patches/*.json` ثم ملفات `work/*/out/*.json` مرتبة؛ آخر تعديل للمفتاح هو المعروض في الفهرس. بناء ملف اللعبة يتم بأداة `apply_patches.py`.

## مكان اسم صاحب النسخة

عبارة «تعريب exelight7» بجانب زر الإعدادات تأتي من تعديل `StartMenu.js` المضمّن في حزمة اللعبة بواسطة [branding.py](../tools/branding.py)، وليست مفتاح حوار في JSON. أما عنوان الإعدادات نفسه فهو `UI_Setting_01`.

المسار داخل اللعبة للنصوص: `ProjectPBZ/Content/Localization/Game/fr/Game.locres`. لذلك يُختار **Français** لتفعيل العربية.
