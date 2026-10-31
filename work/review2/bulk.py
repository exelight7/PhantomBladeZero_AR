"""bulk.py REGEX REPLACEMENT [--dry]: استبدال على كل النص النهائي (خارج الوسوم و{}) مع التحقق، يُحفظ في manual_edits.json."""
import json, glob, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import pbzlib
W = Path(__file__).parent
mp = W / "manual_edits.json"
man = json.loads(mp.read_text(encoding="utf8"))
rx, rep, dry = re.compile(sys.argv[1]), sys.argv[2], "--dry" in sys.argv
tag = re.compile(r"(<[^>]*>|\{[^}]*\})")
n = 0
for f in sorted(glob.glob(str(W / "batches/batch_*.json"))):
    for it in json.loads(Path(f).read_text(encoding="utf8")):
        k = it["key"]; cur = man.get(k, it["text"])
        p = tag.split(cur)
        for i in range(0, len(p), 2): p[i] = rx.sub(rep, p[i])
        new = "".join(p)
        if new == cur: continue
        err, _ = pbzlib.validate(it["text"], new)
        if err: print("REJECT", k, err); continue
        n += 1
        if dry or n <= 3: print(k, "|", re.sub(r"\s+", " ", cur)[:90], "→", re.sub(r"\s+", " ", new)[:90])
        if not dry: man[k] = new
if not dry: mp.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf8")
print("changed:", n, "| total manual:", len(man))
