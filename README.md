<img width="648" height="646" alt="cat nigga" src="https://github.com/user-attachments/assets/636f220f-b08c-4a2a-9ca3-e4b50758fc87" />
# PhantomBladeZero_AR

أدوات وتصحيحات لتحسين تعريب Phantom Blade Zero (مودّ 3BADIOH).

## كيف يعمل المودّ
- النصوص العربية في `Game.locres` داخل `3BADIOH_P.pak` (مسار اللغة الفرنسية، لذا تُختار Français من الإعدادات).
- ملفا `.ucas` و`.utoc` فيهما 177 ملف واجهة (Widgets) وخط. لا نصوص فيهما.
- لا تشفير في أي منها.

## الهيكل
| المسار | المحتوى |
|---|---|
| `tools/` | سكربتات Python: `utoc.py` ثم `dirs.py` (فك الحاوية)، `locres.py` (تحليل النص)، `audit.py` (فحص آلي)، `build.py` (بناء pak التصحيحات) |
| `fixes/changes.txt` | سجل كل تعديل (قبل/بعد) |
| `data/` | مستخرجات: JSON للنصوص، تقرير الفحص، فهرس الملفات |
| `release/` | الـ pak الناتج `ZZZ_3BADIOH_Fix_P.pak` |
| `original_mod/` | المودّ الأصلي كما نُزّل (للمقارنة) مع ملف قراءة صاحبه |

## التركيب
انسخ `release/ProjectPBZ/Content/Paks/~mods/ZZZ_3BADIOH_Fix_P.pak` إلى مجلد `~mods` بجانب ملفات المودّ الأصلي. للتراجع احذفه.

## ملاحظات
- `build.py` يضيف pak يُحمَّل بعد الأصلي؛ لا يعدّل ملفات المودّ.
- السكربتات تحتوي مسارات ثابتة لمجلد التنزيلات، عدّلها قبل التشغيل.

## حقوق
التعريب الأصلي من إنتاج 3BADIOH (انظر `original_mod/README_3BADIOH.txt`). هذا المستودع يضيف تصحيحات وأدوات فقط، والنص المشتق يعود فضله لصاحبه.
