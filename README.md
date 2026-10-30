<div align="center">

<img width="420" alt="بسة المشروع 🐈" src="https://github.com/user-attachments/assets/636f220f-b08c-4a2a-9ca3-e4b50758fc87" />

# Phantom Blade Zero · العربية

**صياغة أوضح، مصطلحات متسقة، وتجربة عربية أفضل.**

تحسينات التعريب بإشراف **exelight7**

[تحميل حزمة التصحيح](release/ProjectPBZ/Content/Paks/~mods/ZZZ_3BADIOH_Fix_P.pak?raw=true) · [دليل المشروع](GUIDE.md) · [سجل التحسينات](fixes/exelight7.md)

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Language](https://img.shields.io/badge/اللغة-العربية-168B67)
![Maintainer](https://img.shields.io/badge/المشرف-exelight7-8B5CF6)

</div>

---

## ✨ ما الجديد؟

- تحسين صياغة القوائم ورسائل الحفظ وشروحات إعدادات الرسوميات والصوت.
- تصحيح أخطاء نحوية في أوصاف الأغراض، مع الحفاظ على المعنى.
- إظهار **«تعريب exelight7»** بجانب زر الإعدادات عند استخدام التعريب العربي.
- حزمة تصحيح قابلة لإعادة البناء، مع فحص النصوص وسلامة ملفات الحزمة.

تضم هذه المراجعة **30 تصحيحًا نصيًا جديدًا** إلى جانب التصحيحات السابقة. التفاصيل قبل التعديل وبعده في [سجل التحسينات](fixes/exelight7.md).

## 🎮 التركيب

1. من Steam، افتح **إدارة ← تصفّح الملفات المحلية** للعبة.
2. انسخ مجلد `ProjectPBZ` من [original_mod](original_mod/) إلى مجلد اللعبة لتثبيت المود الأساسي.
3. انسخ [حزمة التصحيح](release/ProjectPBZ/Content/Paks/~mods/ZZZ_3BADIOH_Fix_P.pak?raw=true) إلى المجلد نفسه بجانب ملفات المود:

   ```text
   ProjectPBZ/Content/Paks/~mods/
   ├── 3BADIOH_P.pak
   ├── 3BADIOH_P.utoc
   ├── 3BADIOH_P.ucas
   └── ZZZ_3BADIOH_Fix_P.pak
   ```

4. من **شاشة البداية**، افتح **Settings → Text Language** واختر **Français**. التعريب يستخدم خانة اللغة الفرنسية.

**للتراجع عن التصحيحات:** احذف `ZZZ_3BADIOH_Fix_P.pak` فقط. ولإزالة التعريب كاملًا، احذف الملفات الأربعة الموضحة أعلاه.

> الحزمة اجتازت الفحص البنيوي والآلي. ظهورها وسلوكها داخل اللعبة يحتاجان تجربة فعلية.

## 🛠️ التحقق وإعادة البناء

تحتاج إلى **Python 3.10 أو أحدث** فقط؛ دون مكتبات خارجية. نفّذ الأوامر من جذر المستودع:

```bash
# التحقق من التصحيحات وملف القائمة دون كتابة الحزمة
python3 tools/apply_patches.py --dry

# تشغيل اختبارات الحزمة وتغيير الاسم
python3 -m unittest discover -s tests -v

# دمج التصحيحات وبناء حزمة الإصدار
python3 tools/apply_patches.py
```

تظهر الحزمة في `release/ProjectPBZ/Content/Paks/~mods/`، ويُحفظ تقرير البناء في [release/apply_report.txt](release/apply_report.txt).

يحتوي ملف التصحيح على النصوص العربية المحدّثة وملف القائمة الذي يعرض اسم **exelight7**. وتبقى ملفات المود الأساسي محفوظة لإعادة البناء والمقارنة.

## 📂 ملفات المشروع

| المسار | المحتوى |
| :--- | :--- |
| [patches/](patches/) | التصحيحات النصية المعتمدة |
| [fixes/](fixes/) | سجلات التغييرات قبل التعديل وبعده |
| [glossary/GLOSSARY.md](glossary/GLOSSARY.md) | المصطلحات المعتمدة للمراجعة |
| [work/](work/) | دفعات المراجعة ومخرجاتها |
| [tools/](tools/) | أدوات فحص النصوص وبناء الحزمة وتخصيص اسم القائمة |
| [tests/](tests/) | اختبارات سلامة الحزمة والتعديلات |
| [data/](data/) | النصوص الأصلية المستخرجة وتقارير الفحص |
| [release/](release/) | حزمة التصحيح الجاهزة للتركيب |
| [original_mod/](original_mod/) | ملفات المود الأساسي |

## 🤝 المساهمة

ابدأ بـ [دليل المشروع](GUIDE.md)، ثم [قواعد المراجعة](tasks/COMMON_RULES.md) و[المسرد](glossary/GLOSSARY.md). حافظ على الوسوم مثل `<...>` والمتغيرات مثل `{0}`، وتحقق من التعديلات قبل دمجها.

## المصدر

تطوير هذه النسخة وتحسيناتها: **exelight7**. التعريب الأساسي من **3BADIOH**؛ تفاصيله في [ملف المود الأصلي](original_mod/README_3BADIOH.txt). ترخيص أدوات المستودع في [LICENSE](LICENSE).
