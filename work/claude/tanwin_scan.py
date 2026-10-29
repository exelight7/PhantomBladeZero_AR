"""كلمات تنتهي بألف بلا تنوين فتح في مدخلات claude: مرشحات أخطاء التنوين (تُراجع يدويًا قبل الإصلاح)."""
import json, re, glob, sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")
L = "ء-ي"
cnt = Counter(); ex = defaultdict(list)
for f in sorted(glob.glob("work/claude/batches/batch_*.json")):
    for it in json.load(open(f, encoding="utf8")):
        t = re.sub(r"<[^>]*>|\{[^}]*\}", " ", it["text"])
        for w in re.findall(r"(?<![%sً-ْ])([%sً-ْ]{3,})(?![%sً-ْ])" % (L, L, L), t):
            if w.endswith("ا") and not w.endswith(("ًا", "اً")):
                cnt[w] += 1; ex[w].append(it["key"])
skip_end = ("ها", "نا", "وا", "ما", "ذا")
rows = [(w, c) for w, c in cnt.most_common() if not w.endswith(skip_end)]
print(len(rows), "كلمة")
print(" ".join(f"{w}:{c}" for w, c in rows))
json.dump({w: ex[w][:3] for w, _ in rows}, open("work/claude/tanwin_candidates.json", "w", encoding="utf8"), ensure_ascii=False)
