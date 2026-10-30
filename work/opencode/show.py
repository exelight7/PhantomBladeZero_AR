"""عرض دفعة بشكل مضغوط للقراءة: python work/claude/show.py 11 [12 ...]  (المفتاح بلا بادئة Dlg_ مع حذف الجزء المشترك مع السطر السابق)"""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
W = Path(__file__).parent
for n in sys.argv[1:]:
    items = json.loads((W / f"batches/batch_{int(n):04d}.json").read_text(encoding="utf8"))
    print(f"##### batch {int(n):04d}")
    prev = []
    for i, it in enumerate(items, 1):
        parts = it["key"].split("_")
        if parts[0] == "Dlg":
            parts = parts[1:]
        c = 0
        while c < len(parts) - 1 and c < len(prev) and parts[c] == prev[c]:
            c += 1
        shown = ("~" * c + "_" if c else "") + "_".join(parts[c:])
        prev = parts
        print(f"{i}\t{shown}\t{it['text']}".replace("\n", "⏎"))
