"""يقسّم النصوص إلى دفعات صغيرة قابلة للاستئناف لكل جلسة: work/<claude|opencode>/batches/batch_NNNN.json"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pbzlib

CLAUDE = {"Dlg", "Reading", "ReadingDes", "Loading", "Chapter"}  # + كل مفتاح يبدأ بـ Quest
MAX_ENTRIES, MAX_CHARS = 100, 12000


def owner(key):
    f = key.split("_")[0]
    return "claude" if f in CLAUDE or f.startswith("Quest") else "opencode"


def main():
    texts = pbzlib.load_original().texts()
    for f in sorted((pbzlib.ROOT / "patches").glob("*.json")):  # الجلسات تراجع النص بعد التصحيحات الآلية
        texts.update(json.loads(f.read_text(encoding="utf8")))
    groups = {"claude": [], "opencode": []}
    for k, t in texts.items():
        if t.strip():
            groups[owner(k)].append({"key": k, "text": t})
    nat = lambda it: re.sub(r"\d+", lambda m: m.group().zfill(6), it["key"])
    for who, items in groups.items():
        items.sort(key=nat)  # الأسطر المتجاورة في المشهد/الفئة تقع في الدفعة نفسها (سياق أفضل)
        d = pbzlib.ROOT / "work" / who / "batches"; d.mkdir(parents=True, exist_ok=True)
        (d.parent / "out").mkdir(exist_ok=True)
        for f in d.glob("batch_*.json"):
            f.unlink()
        batch, chars, n = [], 0, 0
        for it in items + [None]:
            if batch and (it is None or len(batch) >= MAX_ENTRIES or chars + len(it["text"]) > MAX_CHARS):
                n += 1
                (d / f"batch_{n:04d}.json").write_text(json.dumps(batch, ensure_ascii=False, indent=1), encoding="utf8")
                batch, chars = [], 0
            if it:
                batch.append(it); chars += len(it["text"])
        print(who, len(items), "مدخلة،", n, "دفعة")


if __name__ == "__main__":
    main()
