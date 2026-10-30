import struct,sys,os
from pbzlib import SRC_PAK
base=str(SRC_PAK.with_suffix(""))
t=open(base+".utoc","rb").read(); u=open(base+".ucas","rb").read()
(ver,_,_,_,hs,cnt,bc,bs,cmc,cml,cbs,dis,parts)=struct.unpack_from("<B3BIIIIIIIII",t,16) if False else (None,)*13
ver=t[16]; hs,cnt,bc,bs,cmc,cml,cbs,dis,parts=struct.unpack_from("<9I",t,20)
flags=t[16+4+9*4+4+16:][:1]  # approx
print("ver",ver,"hs",hs,"cnt",cnt,"blocks",bc,"cm",cmc,"cbs",cbs,"dirsize",dis)
print("header tail",t[hs-32:hs].hex())
p=hs
ids=[t[p+i*12:p+i*12+12] for i in range(cnt)]; p+=cnt*12
offs=[]
for i in range(cnt):
    b=t[p+i*10:p+i*10+10]; offs.append((int.from_bytes(b[:5],'big'),int.from_bytes(b[5:],'big')))
p+=cnt*10
blocks=[]
for i in range(bc):
    b=t[p+i*12:p+i*12+12]
    o=int.from_bytes(b[:5],'little'); cs=int.from_bytes(b[5:8],'little'); us=int.from_bytes(b[8:11],'little'); cm=b[11]
    blocks.append((o,cs,us,cm))
p+=bc*12
print("block compression methods",set(b[3] for b in blocks))
p+=cmc*cml
# signatures if flag signed: skip detect later
print("remaining toc bytes",len(t)-p)
open("toc_rest.bin","wb").write(t[p:])
os.makedirs("raw",exist_ok=True)
tot=0
for i,((o,l),cid) in enumerate(zip(offs,ids)):
    first=o//cbs; last=(o+l-1)//cbs
    data=b"".join(u[blocks[k][0]:blocks[k][0]+blocks[k][1]] for k in range(first,last+1))
    s=o-first*cbs
    data=data[s:s+l]
    open(f"raw/{i:03d}_{cid.hex()}.bin","wb").write(data); tot+=l
print("dumped",cnt,tot)
