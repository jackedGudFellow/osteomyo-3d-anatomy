import json,re,hashlib,base64,os,shutil,sys
REPO='/home/claude/osteomyo-3d-anatomy'; A=REPO+'/assets'
L=json.load(open('/tmp/work/layout.json')); G=L['G']
(SX,BX),(SY,BY),(SZ,BZ)=G
fmt=lambda v:repr(round(v,5))
def h(s): return base64.urlsafe_b64encode(hashlib.sha256(s.encode()).digest())[:8].decode().replace('-','_')
old={'data':'anatomyData-Cqk5KDrX.js','org':'organsNervousData-D8Vb_utx.js','idx':'index-eK-aaN5l.js'}
src={k:open(f'{A}/{v}').read() for k,v in old.items()}
# --- anatomyData: real-proportion layout for bones with meshes, affine for the rest
layout={k:v for k,v in L['layout'].items()}
inj=("{const __L="+json.dumps(layout,separators=(',',':'))+";for(const e of f){const l=__L[e.id];"
     "if(l){e.pos=l.p;l.s&&(e.size=l.s,e.rot=[0,0,0])}else{e.pos=[e.pos[0]*%s+%s,e.pos[1]*%s+%s,e.pos[2]*%s+%s]}}}"%(fmt(SX),fmt(BX),fmt(SY),fmt(BY),fmt(SZ),fmt(BZ)))
tgt='return{bones:f,boneMap:m,muscles:_}}export{y as R,C as b};'
assert src['data'].count(tgt)==1
data=src['data'].replace(tgt,inj+tgt)
# --- organs/nerves data: affine on pos/path/paths
o=src['org'].rstrip(); assert o.count('function a(){return{organs:')==1 and o.endswith('}}export{a as b};')
o=o.replace('function a(){return{organs:','function __orig(){return{organs:')
BT=json.dumps(L['BT'],separators=(',',':'))
o=o[:-len('export{a as b};')]+("function a(){const d=__orig(),B=%s,T=p=>[p[0]*%s+%s,p[1]*%s+%s,p[2]*%s+%s],"
  "W=p=>{const g=T(p);let x=0,y=0,z=0,s=0;for(const b of B){const u=p[0]-b[0],v=p[1]-b[1],w=p[2]-b[2],k=Math.exp(-(u*u+v*v+w*w)/.0288);s+=k;x+=k*b[3];y+=k*b[4];z+=k*b[5]}"
  "return s>1e-12?[g[0]+x/s,g[1]+y/s,g[2]+z/s]:g};"
  "for(const e of d.organs)e.pos=W(e.pos);for(const n of d.nerves){n.pos=W(n.pos);n.path&&(n.path=n.path.map(W));n.paths&&(n.paths=n.paths.map(q=>q.map(W)))}return d}export{a as b};"%(BT,fmt(SX),fmt(BX),fmt(SY),fmt(BY),fmt(SZ),fmt(BZ)))
# --- index bundle: scale organ/brain groups and body shell to the wider, true-proportion skeleton
x=src['idx']
P_FUNC=("function __P(n,d){if(n==='full'||!d)return d;const t=n==='ossicles'?[-.095,2.758,-.0126]:__W([d.target.x,d.target.y,d.target.z]);"
  "return{target:new b(t[0],t[1],t[2]),pos:new b(d.pos.x+t[0]-d.target.x,d.pos.y+t[1]-d.target.y,d.pos.z+t[2]-d.target.z)}}"
  "const __BT=%s;function __W(p){const g=[p[0]*%s+%s,p[1]*%s+%s,p[2]*%s+%s];let x=0,y=0,z=0,s=0;for(const q of __BT){const u=p[0]-q[0],v=p[1]-q[1],w=p[2]-q[2],k=Math.exp(-(u*u+v*v+w*w)/.0288);s+=k;x+=k*q[3];y+=k*q[4];z+=k*q[5]}return s>1e-12?[g[0]+x/s,g[1]+y/s,g[2]+z/s]:g}"%(json.dumps(L['BT'],separators=(',',':')),fmt(SX),fmt(BX),fmt(SY),fmt(BY),fmt(SZ),fmt(BZ)))
for a,b in [('function Co(n){','%s function Co(n){'%'\x00P\x00'),('},d=o[n]||o.full;let a=d.pos.clone();','},d=__P(n,o[n]||o.full);let a=d.pos.clone();'),
            ('o.position.copy(u),Fe.add(o)','o.position.copy(u),o.scale.set(%s,1,%s),Fe.add(o)'%(fmt(SX),fmt(SZ))),
            ('o.position.set(...n.pos)}else if(n.nerveType==="brain_stem")','o.position.set(...n.pos),o.scale.set(%s,1,%s)}else if(n.nerveType==="brain_stem")'%(fmt(SX),fmt(SZ))),
            ('o.position.set(...n.pos)}else if(n.nerveType==="spinal_cord")','o.position.set(...n.pos),o.scale.set(%s,1,%s)}else if(n.nerveType==="spinal_cord")'%(fmt(SX),fmt(SZ))),
            ('F.add(Lt,Fe,it,It,He,_e,kt);','F.add(Lt,Fe,it,It,He,_e,kt),kt.scale.set(%s,%s,%s),kt.position.set(0,%s,%s);'%(fmt(L['SHELL_SX']),fmt(SY),fmt(SZ),fmt(BY),fmt(BZ)))]:
    assert x.count(a)==1,a; x=x.replace(a,b.replace('\x00P\x00',P_FUNC))
new={'data':'anatomyData-%s.js'%h(data),'org':'organsNervousData-%s.js'%h(o)}
x=x.replace(old['data'],new['data']).replace(old['org'],new['org'])
new['idx']='index-%s.js'%h(x)
# other chunks may import these too
for f in os.listdir(A):
    if f.endswith('.js') and f not in old.values():
        t=open(f'{A}/{f}').read()
        if old['data'] in t or old['org'] in t or old['idx'] in t: print('NOTE: also references old chunk:',f)
for k,v in new.items(): open(f'{A}/{v}','w').write({'data':data,'org':o,'idx':x}[k])
for v in old.values(): os.remove(f'{A}/{v}')
# html + sw references
for p in ['index.html','sw.js']:
    t=open(f'{REPO}/{p}').read()
    for k in old: t=t.replace(old[k],new[k])
    open(f'{REPO}/{p}','w').write(t)
print(new)
