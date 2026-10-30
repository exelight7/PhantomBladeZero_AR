"""تعديلات يدوية مضغوطة تُضاف إلى manual_edits.json.
الإدخال (stdin): سطر لكل تعديل:  المفتاح ||| النص القديم ||| النص الجديد
النص القديم يجب أن يرد مرة واحدة في النص الحالي للمفتاح؛ تُطبَّق التعديلات المتتالية على المفتاح نفسه بالترتيب.
يُرفض أي تعديل يغيّر الوسوم أو {} أو عدد الأسطر. يتجاهل السطور الفارغة وما يبدأ بـ #."""
import json, sys, glob
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import pbzlib
W = Path(__file__).parent
base = {}
for f in sorted(glob.glob(str(W / "batches/batch_*.json"))):
    for it in json.loads(Path(f).read_text(encoding="utf8")):
        base[it["key"]] = it["text"]
mp = W / "manual_edits.json"
manual = json.loads(mp.read_text(encoding="utf8")) if mp.exists() else {}
bad = 0
for line in sys.stdin.read().splitlines():
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    key, old, new = [x.strip(" ") if i < 1 else x for i, x in enumerate(line.split("|||"))] if line.count("|||") == 2 else (None, None, None)
    if key is None:
        print("BAD LINE:", line[:80]); bad += 1; continue
    key = key.strip()
    if ":" in key and key.split(":")[0].isdigit():  # «رقم الدفعة:رقم السطر» كما يعرضه show.py
        bn, ln = key.split(":")
        key = json.loads((W / f"batches/batch_{int(bn):04d}.json").read_text(encoding="utf8"))[int(ln) - 1]["key"]
    old = old.strip() if not old.startswith(" ") and not old.endswith(" ") else old
    cur = manual.get(key, base.get(key))
    if cur is None:
        print("NO KEY:", key); bad += 1; continue
    old = old.strip().replace("\\n", "\n"); new = (new.strip() if new.strip() else new).replace("\\n", "\n")
    if cur.count(old) != 1:
        print(f"OLD x{cur.count(old)}: {key} | {old}"); bad += 1; continue
    upd = cur.replace(old, new.strip())
    err, warn = pbzlib.validate(base[key], upd)
    if err:
        print("REJECT", key, err); bad += 1; continue
    manual[key] = upd
    print(f"ok {key}\n   - {old}\n   + {new.strip()}")
mp.write_text(json.dumps(manual, ensure_ascii=False, indent=1), encoding="utf8")
print("total manual edits:", len(manual), "| problems:", bad)
