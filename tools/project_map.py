"""Generate a complete, linked map of localization keys and current merged texts."""
import collections
import html
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def main():
    rows = json.loads((ROOT / 'data/Game_locres_ar.json').read_text(encoding='utf-8'))
    batches = {}
    for p in sorted((ROOT / 'work').glob('*/batches/*.json')):
        for r in json.loads(p.read_text(encoding='utf-8')):
            batches[r['key']] = p.relative_to(ROOT).as_posix()
    edits = {}
    for p in sorted((ROOT / 'patches').glob('*.json')) + sorted((ROOT / 'work').glob('*/out/*.json')):
        for k, text in json.loads(p.read_text(encoding='utf-8')).items():
            edits[k] = (text, p.relative_to(ROOT).as_posix())
    groups = collections.defaultdict(list)
    for r in rows:
        groups[r['key'].split('_')[0]].append(r)
    out = ROOT / 'docs/text-index'
    out.mkdir(exist_ok=True)
    index = ['# الفهرس الكامل للنصوص', '', f'يشمل جميع المدخلات: **{len(rows):,}**، بما فيها النصوص الفارغة. النص المعروض هو النص الحالي بعد دمج التصحيحات ومخرجات المراجعة، وليس ترجمة جديدة. روابط المصدر تفتح الملف الذي يحتوي المفتاح؛ استخدم البحث داخل الملف للوصول إليه.', '', '[العودة لخريطة المشروع](../PROJECT_MAP.md)', '', '| الفئة | عدد المدخلات |', '| --- | ---: |']
    for family, items in sorted(groups.items()):
        index.append(f'| [{family}]({family}.md) | {len(items)} |')
        sections = collections.defaultdict(list)
        for r in items:
            parts = r['key'].split('_')
            section = '_'.join(parts[:2]) if len(parts) > 2 else family
            sections[section].append(r)
        lines = [f'# {family} — {len(items):,} مدخلة', '', '[كل الفئات](README.md) · [خريطة المشروع](../PROJECT_MAP.md)', '', '## الأقسام', '']
        for section, entries in sorted(sections.items()):
            lines.append(f'- [{section}](#{section.lower()}) — {len(entries)}')
        for section, entries in sorted(sections.items()):
            lines.extend(['', f'## {section}', '', '| المفتاح | النص الحالي | مكان المراجعة | مصدر التعديل |', '| --- | --- | --- | --- |'])
            for r in sorted(entries, key=lambda r: r['key']):
                key = r['key']; text, edit = edits.get(key, (r['text'], None))
                text = html.escape(text).replace('|', '&#124;').replace('\n', '<br>') or '*(فارغ)*'
                batch = f'[الدفعة](../../{batches[key]})' if key in batches else 'لا توجد دفعة'
                source = f'[التصحيح](../../{edit})' if edit else '[الأصل](../../data/Game_locres_ar.json)'
                lines.append(f'| `{key}` | {text} | {batch} | {source} |')
        (out / f'{family}.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (out / 'README.md').write_text('\n'.join(index) + '\n', encoding='utf-8')
    print(f'Indexed {len(rows)} entries across {len(groups)} categories')
if __name__ == '__main__':
    main()
