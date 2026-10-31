"""مسح اتساق الأسماء والمصطلحات على النص النهائي كاملًا (دفعات review2 بعد تعديلاتها اليدوية).
أ) كلمات تختلف في الهمزة/التاء المربوطة/الألف المقصورة فقط.  ب) اسم مكتوب متصلًا ومنفصلًا (شياوكوي/شياو كوي)."""
import json, glob, re, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
W = Path(__file__).parent
man = json.loads((W / "manual_edits.json").read_text(encoding="utf8"))
texts = {}
for f in sorted(glob.glob(str(W / "batches/batch_*.json"))):
    for it in json.loads(Path(f).read_text(encoding="utf8")):
        texts[it["key"]] = man.get(it["key"], it["text"])
HAR = re.compile("[ً-ْـ]")
def clean(t): return re.sub(r"<[^>]*>|\{[^}]*\}", " ", t)
words = Counter()
for t in texts.values():
    for w in re.findall(r"[ء-يً-ْـ]+", clean(t)):
        words[HAR.sub("", w)] += 1
def norm(w): return w.translate(str.maketrans("أإآة ى", "ااهه ي")).replace(" ", "")
g = defaultdict(list)
for w, c in words.items(): g[norm(w)].append((c, w))
mode = sys.argv[1] if len(sys.argv) > 1 else "a"
if mode == "a":
    for k, v in sorted(g.items(), key=lambda x: -sum(c for c, _ in x[1])):
        if len(v) > 1:
            v.sort(reverse=True)
            if v[1][0] >= 1 and v[0][0] >= 2:
                print(" | ".join(f"{w}:{c}" for c, w in v))
else:
    pairs = Counter()
    for t in texts.values():
        ws = [HAR.sub("", w) for w in re.findall(r"[ء-يً-ْـ]+", clean(t))]
        for a, b in zip(ws, ws[1:]): pairs[(a, b)] += 1
    for (a, b), c in pairs.most_common():
        j = a + b
        if words.get(j, 0) and len(a) > 1 and len(b) > 1:
            print(f"{a} {b}:{c} | {j}:{words[j]}")
