"""lint.py [فئة] [حد]: مسح نحوي/إملائي على النص النهائي كاملًا. بلا وسيط: عدد الإصابات لكل فئة."""
import json, glob, re, sys
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
W = Path(__file__).parent
man = json.loads((W / "manual_edits.json").read_text(encoding="utf8"))
T = {}
for f in sorted(glob.glob(str(W / "batches/batch_*.json"))):
    b = int(Path(f).name[6:10])
    for i, it in enumerate(json.loads(Path(f).read_text(encoding="utf8")), 1):
        T[it["key"]] = (f"{b}:{i}", man.get(it["key"], it["text"]))
A = "ء-يً-ْ"
B, E = f"(?<![{A}])", f"(?![{A}])"
def plain(t): return re.sub(r"<[^>]*>|\{[^}]*\}", " ", t)
NUM_F = "ثلاثة|أربعة|خمسة|ستة|سبعة|ثمانية|تسعة|عشرة"
NUM_M = "ثلاث|أربع|خمس|ست|سبع|ثماني|تسع|عشر"
# كلمات تُكتب في النص أحيانًا بتنوين «ًا» وأحيانًا بلا تنوين
words = Counter(w for _, t in T.values() for w in re.findall(f"[{A}]+", plain(t)))
bare = {w for w in words if w.endswith("ا") and len(w) > 3 and words.get(w[:-1] + "ًا", 0) >= 2}
R = {
 "tanwin": re.compile(B + "(" + "|".join(sorted(map(re.escape, bare), key=len, reverse=True)) + ")" + E) if bare else None,
 "num_f_ات": re.compile(B + f"({NUM_F}) [{A}]+ات" + E),
 "num_m_masc": re.compile(B + f"({NUM_M}) (أيام|أعوام|أشهر|رجال|إخوة|أطفال|أبناء|أسابيع|قرون|أجيال|فصول|مرافقين|جنود|أصدقاء|أقدام|أمتار|أشخاص|آلاف|ملايين)" + E),
 "bid3a": re.compile(B + f"بضعة [{A}]+ات" + E + "|" + B + "بضع (أيام|أعوام|أشهر|رجال|أسابيع|سنين|خطوات)" + E),
 "dhu_gen": re.compile(B + f"(في|من|إلى|على|عن|مع|لدى|ب[{A}]+|ل[{A}]+) [{A}]+ ذو" + E),
 "five_verbs": re.compile(B + f"(لم|لن|أن|كي|لكي|ولم|ولن|فلن|فلم|حتى|لئلا|ألا) (ي|ت)[{A}]+(ون|ين)" + E),
 "lam_hollow": re.compile(B + "(لم|ولم|فلم) (ي|ت|أ|ن)(كون|قول|عود|زال|صير|نام|خاف|بقى|نسى|مشي|بكي|جري|رى|بقي)" + E),
 "ya_alif": re.compile(B + "(التى|الذى|فى|حتي|لاكن|لاكنه|ذالك|هاذا|هاذه|هاكذا|إنشاء الله|مسئول|شيئ|شئ)" + E),
 "punct": re.compile(r" [،؛؟!.:](?!\.)|،،|؟؟؟+|\.\.\.\.+|(?<![.])\.\.(?!\.)|\( | \)|«\s|\s»"),
 "al_split": re.compile(B + "ال " ),
 "latin_cjk": re.compile(r"[　-鿿＀-￯]|ـ(?![<A-Za-z0-9{ ])"),
 "repeat": re.compile(B + f"([{A}]{{2,}}) \\1" + E),
 "hamza_wasl": re.compile(B + "(إستـ|إنتـ|إنفـ|إستخدام|إستعادة|إنتظار|إنتقام|إنتهاء|إنطلاق|إختيار|إتخاذ|إجتياز|إحتفاظ|إرتفاع|إقتراب|إمتلاك|إستيقاظ|إبن|إسم|إمرأة|إثنان|إثنين|الإثنين)"),
 "anna_waw": re.compile(B + "(إذا ما|كلا من|ك?لما كان)" + E),
}
mode = sys.argv[1] if len(sys.argv) > 1 else None
lim = int(sys.argv[2]) if len(sys.argv) > 2 else 60
for name, rx in R.items():
    if rx is None or (mode and name != mode): continue
    hits = []
    for k, (loc, t) in T.items():
        p = plain(t).replace("\n", "⏎")
        for m in rx.finditer(p):
            hits.append(f"{loc} {k} | …{p[max(0, m.start()-30):m.end()+25]}…")
    print(f"== {name}: {len(hits)}")
    if mode:
        print("\n".join(hits[:lim]))
