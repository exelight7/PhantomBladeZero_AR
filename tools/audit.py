import json,re,collections
d=json.load(open("fr_locres.json",encoding="utf8"))
ar=lambda s:re.search('[؀-ۿ]',s)
lat=lambda s:re.search('[A-Za-z]',s)
strip=lambda s:re.sub(r'<[^>]*>|\{[^}]*\}','',s)
out=open("audit.txt","w",encoding="utf8")
def sec(t): out.write(f"\n=== {t} ===\n")
def w(e,extra=""): out.write(f'{e["key"]}\t{e["text"][:200]!r}\t{extra}\n')
sec("EMPTY"); n=[e for e in d if not e["text"].strip()]; out.write(f"count {len(n)}\n")
for e in n[:15]: w(e)
sec("NO ARABIC but has latin (untranslated)"); n=[e for e in d if e["text"].strip() and not ar(strip(e["text"])) and lat(strip(e["text"]))]; out.write(f"count {len(n)}\n")
for e in n[:80]: w(e)
sec("ARABIC with latin words"); n=[(e,re.findall(r'[A-Za-z][A-Za-z\'\-]+',strip(e["text"]))) for e in d if ar(e["text"])]; n=[(e,l) for e,l in n if l]; out.write(f"count {len(n)}\n")
for e,l in n[:60]: w(e,str(l))
checks={
 "latin comma/?/; in arabic":r'[؀-ۿ][ ]?[,;?]',
 "double space":r'[؀-ۿ]  +[؀-ۿ]',
 "space before punct":r'[؀-ۿ] [،؟!.:؛]',
 "no space after punct":r'[؀-ۿ][،؛؟][؀-ۿ]',
 "tatweel":'ـ',
 "repeat word":r'(?<![؀-ۿ])([؀-ۿ]{2,}) \1(?![؀-ۿ])',
 "ending ه after ة-likely? (no)":r'(?<![؀-ۿ])(?:اذا|ان|اي|الى|انت|انا|اخر|او|الا|الاخ|اخي|لان|انه|انها|انهم|اكثر|اكبر|افضل|اهل|امر|اسم|اول|اولئك|الاول|الاخرين)(?![؀-ۿ])',
 "ى/ي end confusion (علي/الي/حتي/متي/اللتي/الذي ok)":r'(?<![؀-ۿ])(?:الي|حتي|متي|علي|الاعلي|الاقصي|اقصي|مستشفي|مسعي|اخري|كبري|صغري|عليا)(?![؀-ۿ])',
 "هاذا/لاكن/هذة/ذالك":r'(?<![؀-ۿ])(?:هاذا|هاذه|لاكن|لكنه?ا?(?=ة)|هذة|ذالك|اولائك|اؤلئك|إنشاء الله|انشاء الله)(?![؀-ۿ])',
 "western digits in arabic text":r'[؀-ۿ][^<{]{0,3}[0-9]',
 "diacritics":r'[ً-ْ]',
 "ة followed by letter within word (ex مفطّرة ok)":r'ة[ء-ي]',
 "ه end of word candidate for ة? skip":r'^$',
}
for name,pat in checks.items():
    if pat=='^$':continue
    n=[e for e in d if re.search(pat,strip(e["text"]) if 'digits' not in name else e["text"])]
    sec(f"{name}: {len(n)}")
    for e in n[:8]:
        m=re.search(pat,strip(e["text"]) if 'digits' not in name else e["text"]); out.write(f'{e["key"]}\t...{e["text"][max(0,m.start()-30):m.end()+30]!r}\n')
# tag sets by key family
sec("tag shapes")
c=collections.Counter(t for e in d for t in re.findall(r'<(/?\w+)',e["text"])); out.write(str(c.most_common(40))+"\n")
sec("unbalanced tags"); 
for e in d:
    o=len(re.findall(r'<(?!/|InputAction|img|\w+[^>]*/>)\w+[^>]*>',e["text"])); cl=len(re.findall(r'</>',e["text"]))
    if o!=cl: w(e,f"open{o} close{cl}")
sec("key prefixes"); c=collections.Counter(re.split(r'_',e["key"])[0] for e in d); out.write(str(c.most_common(30))+"\n")
sec("duplicate source texts (same Arabic diff keys) count"); c=collections.Counter(e["text"] for e in d if len(e["text"])>10); out.write(str(sum(1 for v in c.values() if v>1))+"\n")
