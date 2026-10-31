"""يولّد دفعات المراجعة الثانية من **النص النهائي** (الأصلي + patches/ + work/claude/out + work/opencode/out).
الدفعات 1–4: المدخلات التي لم تشملها أي مراجعة سابقة؛ ثم كل بقية المدخلات بترتيب الملف. كل مفتاح يرد مرة واحدة."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import pbzlib
W = Path(__file__).parent
ROOT = pbzlib.ROOT
SIZE = 100


def final_texts():
    orig = pbzlib.load_original().texts()
    cur = dict(orig)
    files = sorted((ROOT / "patches").glob("*.json"))
    files += [f for s in ("claude", "opencode") for f in sorted((ROOT / "work" / s / "out").glob("*.json"))]
    for f in files:
        cur.update(json.loads(f.read_text(encoding="utf8")))
    return orig, cur


def main():
    orig, cur = final_texts()
    seen = set()
    for s in ("claude", "opencode"):
        for f in (ROOT / "work" / s / "batches").glob("*.json"):
            seen.update(i["key"] for i in json.loads(f.read_text(encoding="utf8")))
    first = [k for k in orig if k not in seen]
    rest = [k for k in orig if k in seen]
    keys = [k for k in first + rest if cur[k].strip()]
    for i in range(0, len(keys), SIZE):
        b = [{"key": k, "text": cur[k]} for k in keys[i:i + SIZE]]
        (W / "batches" / f"batch_{i // SIZE + 1:04d}.json").write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf8")
    print(f"unreviewed: {len(first)} | total: {len(keys)} | batches: {(len(keys) + SIZE - 1) // SIZE}")


if __name__ == "__main__":
    main()
