"""عرض مضغوط جدًا: رقم السطر، المتكلم (عند تغيّره فقط)، النص."""
import json, sys, re
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
W = Path(__file__).parent
for n in sys.argv[1:]:
    items = json.loads((W / f"batches/batch_{int(n):04d}.json").read_text(encoding="utf8"))
    print(f"## {int(n)}")
    last = None
    for i, it in enumerate(items, 1):
        parts = re.sub(r"(_\d+)+$", "", it["key"]).split("_")
        spk = parts[-1] if len(parts) > 1 else parts[0]
        tag = f"[{spk}] " if spk != last else ""
        last = spk
        print(f"{i} {tag}{it['text']}".replace("\n", "⏎"))
