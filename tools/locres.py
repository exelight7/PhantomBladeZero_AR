import struct,json,sys
def parse(b,start=0):
    p=start+16
    ver=b[p]; p+=1
    aoff,=struct.unpack_from("<q",b,p); p+=8
    def fs(p):
        n,=struct.unpack_from("<i",b,p); p+=4
        if n<0: n=-n; s=b[p:p+n*2-2].decode("utf-16-le"); p+=n*2
        else: s=b[p:p+n-1].decode("utf-8"); p+=n
        return s,p
    total,=struct.unpack_from("<I",b,p); p+=4
    nns,=struct.unpack_from("<I",b,p); p+=4
    ents=[]
    for _ in range(nns):
        p+=4; ns,p=fs(p)
        kc,=struct.unpack_from("<I",b,p); p+=4
        for _ in range(kc):
            p+=4; k,p=fs(p)
            sh,idx=struct.unpack_from("<Ii",b,p); p+=8
            ents.append([ns,k,sh,idx])
    q=start+aoff
    n,=struct.unpack_from("<I",b,q); q+=4
    strs=[]
    for _ in range(n):
        s,q=fs(q); q+=4; strs.append(s)
    return ents,strs,q-start
if __name__=="__main__":
    f=open(r"C:\Users\npxf1\Downloads\New folder\ProjectPBZ\Content\Paks\~mods\3BADIOH_P.pak","rb").read()
    ents,strs,length=parse(f,4077146)
    print(len(ents),len(strs),length)
    out=[{"ns":e[0],"key":e[1],"hash":e[2],"text":strs[e[3]]} for e in ents]
    json.dump(out,open("fr_locres.json","w",encoding="utf8"),ensure_ascii=False,indent=0)
    print(sum(1 for o in out if any('\u0600'<=c<='\u06ff' for c in o["text"])),"arabic entries")
    for o in out[:15]: print(o)
