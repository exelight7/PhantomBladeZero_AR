"""ctx.py REGEX [عدد]: يعرض السياق لكل تطابق في النص النهائي مع المفتاح ورقم الدفعة:السطر."""
import json, glob, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
W = Path(__file__).parent
man = json.loads((W / "manual_edits.json").read_text(encoding="utf8"))
rx = re.compile(sys.argv[1]); lim = int(sys.argv[2]) if len(sys.argv) > 2 else 40; n = 0
for f in sorted(glob.glob(str(W / "batches/batch_*.json"))):
    b = int(Path(f).name[6:10])
    for i, it in enumerate(json.loads(Path(f).read_text(encoding="utf8")), 1):
        t = man.get(it["key"], it["text"]).replace("\n", "⏎")
        for m in rx.finditer(t):
            n += 1
            if n <= lim: print(f"{b}:{i} {it['key']} | …{t[max(0,m.start()-35):m.end()+35]}…")
print("total", n)
