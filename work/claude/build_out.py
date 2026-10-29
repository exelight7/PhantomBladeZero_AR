"""يبني work/claude/out/batch_NNNN.json للدفعات المنتهية فقط (<= DONE_THROUGH في done_through.txt):
قواعد آلية موثَّقة (تنوين) + تعديلات يدوية من manual_edits.json (تفوز على القواعد). يكتب المفاتيح المتغيرة فقط."""
import json, re, glob, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
W = Path(__file__).parent
L = "ء-يً-ْ"
# كلمات منصوبة منوَّنة نُسي تنوينها (روجع سياق كل منها يدويًا؛ المثنى والأفعال مستثناة عمدًا)
TANWIN = ("قناعا شرابا مهلا بطلا اضطرابا مهيبا رمادا أبطالا كذبا تمثالا مرتبطا طيبا معسكرا مسرعا أرضا فشلا_X").split()
TANWIN = [w for w in TANWIN if not w.endswith("_X")]
TANWIN_EXTRA = {"تبا": "تبًّا", "حيا": "حيًّا", "حيًا": "حيًّا"}
rules = {w: w[:-1] + "ًا" for w in TANWIN}
rules.update(TANWIN_EXTRA)
rx = re.compile(r"(?<![%s])(%s)(?![%s])" % (L, "|".join(map(re.escape, rules)), L))
tag = re.compile(r"(<[^>]*>|\{[^}]*\})")


def auto(t):
    p = tag.split(t)
    for i in range(0, len(p), 2):
        p[i] = rx.sub(lambda m: rules[m.group(1)], p[i])
    return "".join(p)


def main():
    done = int((W / "done_through.txt").read_text().strip() or 0)
    manual = json.loads((W / "manual_edits.json").read_text(encoding="utf8")) if (W / "manual_edits.json").exists() else {}
    used = set(); n_out = 0; n_changed = 0
    (W / "out").mkdir(exist_ok=True)
    for f in sorted(glob.glob(str(W / "batches/batch_*.json"))):
        name = Path(f).name; num = int(name[6:10])
        if num > done: continue
        out = {}
        for it in json.loads(Path(f).read_text(encoding="utf8")):
            k, t = it["key"], it["text"]
            new = manual.get(k, auto(t))
            if k in manual: used.add(k)
            if new != t: out[k] = new
        (W / "out" / name).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf8")
        n_out += 1; n_changed += len(out)
    unknown = set(manual) - used
    print(f"batches written: {n_out} | changed entries: {n_changed} | manual keys not in done batches: {len(unknown)}")


if __name__ == "__main__":
    main()
