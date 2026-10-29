import json, re, glob, sys
sys.stdout.reconfigure(encoding="utf-8")
want = sys.argv[1:]
for f in sorted(glob.glob("work/claude/batches/batch_*.json")):
    for it in json.load(open(f, encoding="utf8")):
        t = it["text"]
        for w in want:
            for m in re.finditer(r"(?<![ء-يً-ْ])%s(?![ء-يً-ْ])" % re.escape(w), t):
                print(w, "|", it["key"], "|", t[max(0, m.start() - 35):m.end() + 25].replace("\n", " "))
