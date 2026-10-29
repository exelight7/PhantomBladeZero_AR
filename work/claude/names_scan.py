"""مسح أسماء الأعلام المحتملة: الكلمات التي تلي ألقابًا (السيد، المعلم، الآنسة، يا ...) مع تواترها وصيغها."""
import json, re, glob, sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")
TITLES = "السيد|السيدة|المعلم|المعلمة|الآنسة|آنسة|الشيخ|العم|الأخ|الأخت|الجد|العجوز|القائد|الزعيم|الطبيب|سيد|معلم|يا|أخي|أخت|الشاب|الفتى|الملك|الأمير|حاكم|سيدي|سيدتي"
pat = re.compile(r"(?<![ء-ي])(?:%s)\s+([ء-ي][ء-يً-ْ]+(?:\s+[ء-ي][ء-يً-ْ]+)?)" % TITLES)
STOP = set("الذي التي هذا هذه ذلك الذين أنت أنا نحن هل ما من إلى على في لا لم لن قد أن إن كان كل بعد قبل مع عن".split())
cnt = Counter(); where = defaultdict(set)
for f in sorted(glob.glob("work/claude/batches/batch_*.json")):
    for it in json.load(open(f, encoding="utf8")):
        t = re.sub(r"<[^>]*>", "", it["text"])
        for m in pat.finditer(t):
            w = re.sub(r"[ً-ْ]", "", m.group(1)).split()
            if w[0] in STOP or w[0].startswith("ال") and len(w[0]) < 6: continue
            cnt[w[0]] += 1; where[w[0]].add(it["key"])
print("الاسم\tتواتر\tمثال مفتاح")
for w, c in cnt.most_common(80):
    print(f"{w}\t{c}\t{sorted(where[w])[0]}")
