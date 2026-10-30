import struct,re,hashlib,json,sys
from pbzlib import SRC_PAK
SRC=str(SRC_PAK)
OUT=sys.argv[1]
f=open(SRC,"rb").read()
LOC=4077146
orig=f[LOC:LOC+2073062]
assert orig[:16].hex()=="0e14747567 4a03fc4a15909dc3377f1b".replace(" ","")
aoff,=struct.unpack_from("<q",orig,17)
def fs(b,p):
    n,=struct.unpack_from("<i",b,p); p+=4
    if n<0: n=-n; s=b[p:p+n*2-2].decode("utf-16-le"); p+=n*2
    else: s=b[p:p+n-1].decode("utf-8"); p+=n
    return s,p
def pack(s):
    if all(ord(c)<128 for c in s): e=s.encode()+b"\0"; return struct.pack("<i",len(e))+e
    e=(s+"\0").encode("utf-16-le"); return struct.pack("<i",-(len(e)//2))+e
n,=struct.unpack_from("<I",orig,aoff); p=aoff+4; strs=[]
for _ in range(n):
    s,p=fs(orig,p); rc,=struct.unpack_from("<i",orig,p); p+=4; strs.append([s,rc])
assert p==len(orig)
# ---- fixes
EXPL={"ساحة المزار ancestral":"ساحة مزار الأجداد",
      "شبحيا grotesque":"شبحيًّا بشعًا",
      "العالم العالم القديم":"العالم القديم"}
TW="حقا أبدا تماما أيضا جدا مجددا طويلا شكرا حاليا أولا بعيدا جزءا شيئا بدلا بعضا".split()
L="\u0621-\u064a\u064b-\u0652"
twre=re.compile(r"(?<![%s])(%s)(?![%s])"%(L,"|".join(TW),L))
tag=re.compile(r"(<[^>]*>)")
def fix(s):
    parts=tag.split(s)
    for i in range(0,len(parts),2):
        t=parts[i]
        for a,b in EXPL.items(): t=t.replace(a,b)
        parts[i]=twre.sub(lambda m:m.group(1)+"\u064b"+"ا",twre.sub(lambda m:m.group(1)[:-1],t) if False else t) if False else twre.sub(lambda m:m.group(1)[:-1]+"\u064bا",t)
    return "".join(parts)
log=[]
for i,(s,rc) in enumerate(strs):
    t=fix(s)
    if t!=s:
        assert sorted(tag.findall(s))==sorted(tag.findall(t))
        log.append((i,s,t)); strs[i][0]=t
new=orig[:aoff]+struct.pack("<I",len(strs))+b"".join(pack(s)+struct.pack("<i",rc) for s,rc in strs)
json.dump([{"idx":i,"before":a,"after":b} for i,a,b in log],open("changes.json","w",encoding="utf8"),ensure_ascii=False,indent=1)
print("changed strings:",len(log),"new locres size",len(new))
# ---- pak v11 single file
PATH="ProjectPBZ/Content/Localization/Game/fr/Game.locres"
sha=lambda b:hashlib.sha1(b).digest()
hdr=struct.pack("<QQQI",0,len(new),len(new),0)+sha(new)+b"\0"+struct.pack("<I",0)
assert len(hdr)==53
data=hdr+new
FS=lambda s:struct.pack("<i",len(s)+1)+s.encode()+b"\0"
enc=struct.pack("<III",0xe0000000,0,len(new))
dirs=["/","ProjectPBZ/","ProjectPBZ/Content/","ProjectPBZ/Content/Localization/","ProjectPBZ/Content/Localization/Game/","ProjectPBZ/Content/Localization/Game/fr/"]
fd=struct.pack("<I",len(dirs))
for d in dirs:
    fd+=FS(d)
    if d==dirs[-1]: fd+=struct.pack("<I",1)+FS("Game.locres")+struct.pack("<i",0)
    else: fd+=struct.pack("<I",0)
M=(1<<64)-1
x=0xcbf29ce484222325
for b in PATH.lower().encode("utf-16-le"): x=((x^b)*0x100000001b3)&M
ph=struct.pack("<I",1)+struct.pack("<Qi",x,0)+struct.pack("<I",0)
base=len(data)
# primary index size: mount(4+10)+count4+seed8+4+(8+8+20)+4+(8+8+20)+4+len(enc)+4
mount=FS("../../../")
psize=len(mount)+4+8+4+36+4+36+4+len(enc)+4
ph_off=base+psize; fd_off=ph_off+len(ph)
pri=mount+struct.pack("<IQ",1,0)+struct.pack("<IQQ",1,ph_off,len(ph))+sha(ph)+struct.pack("<IQQ",1,fd_off,len(fd))+sha(fd)+struct.pack("<I",len(enc))+enc+struct.pack("<I",0)
assert len(pri)==psize
foot=b"\0"*16+b"\0"+struct.pack("<II",0x5A6F12E1,11)+struct.pack("<QQ",base,len(pri))+sha(pri)+b"\0"*160
assert len(foot)==221
open(OUT,"wb").write(data+pri+ph+fd+foot)
print("pak bytes",len(data+pri+ph+fd+foot))
