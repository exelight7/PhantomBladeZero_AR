import struct,os,glob
r=open("toc_rest.bin","rb").read()
p=0
def u32():
    global p; v=struct.unpack_from("<I",r,p)[0]; p+=4; return v
def fstr():
    global p
    n=struct.unpack_from("<i",r,p)[0]; p+=4
    s=r[p:p+n-1].decode(); p+=n; return s
mount=fstr()
nd=u32(); dirs=[struct.unpack_from("<4I",r,p+i*16) for i in range(nd)]; p+=nd*16
nf=u32(); files=[struct.unpack_from("<3I",r,p+i*12) for i in range(nf)]; p+=nf*12
ns=u32(); strs=[fstr() for _ in range(ns)]
NONE=0xffffffff
out={}
def walk(d,path):
    name,fc,ns_,ff=dirs[d]
    cur=path+([strs[name]] if name!=NONE else [])
    f=ff
    while f!=NONE:
        fn,nf_,ud=files[f]; out[ud]="/".join(cur+[strs[fn]]); f=nf_
    c=fc
    while c!=NONE:
        walk(c,cur); c=dirs[c][2]
walk(0,[])
raws=sorted(glob.glob("raw/*.bin"))
with open("index.txt","w",encoding="utf8") as o:
    for ud,pa in sorted(out.items()):
        sz=os.path.getsize(raws[ud]); o.write(f"{ud}\t{sz}\t{pa}\n")
print(len(out))
