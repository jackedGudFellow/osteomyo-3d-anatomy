import json,struct,gzip,os,sys,numpy as np,trimesh,fast_simplification
M=json.load(open('/tmp/work/map.json'))
names={}
for i,l in enumerate(open('/tmp/bp3d/meta/parts_list_e.txt',encoding='utf-8')):
    if i==0: continue
    p=l.rstrip('\n').split('\t')
    if len(p)>=2: names[p[0].strip('"').replace('FMA','')]=p[1].strip('"')
OUT=sys.argv[1]; os.makedirs(OUT,exist_ok=True)
def load_stl(f):
    d=open(f'/tmp/bp3d/stl/FMA{f}.stl','rb').read()
    n=struct.unpack('<I',d[80:84])[0]; assert 84+n*50==len(d),(f,n,len(d))
    a=np.frombuffer(d[84:84+n*50],dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]))
    return a['v'].reshape(-1,3).astype(np.float64)
layout={}; manifest={}; tot=0; ntri=0
for bid,fmas in M.items():
    parts=[]
    for f in fmas:
        v=load_stl(f)
        v=np.stack([v[:,0],v[:,2],-v[:,1]],1)/1000.0   # z-up mm -> y-up m
        m=trimesh.Trimesh(vertices=v,faces=np.arange(len(v)).reshape(-1,3),process=False); m.merge_vertices(); m.update_faces(m.nondegenerate_faces())
        parts.append(m)
    mesh=trimesh.util.concatenate(parts) if len(parts)>1 else parts[0]
    mesh.remove_unreferenced_vertices()
    lo,hi=mesh.bounds; dims=hi-lo; maxdim=float(dims.max())
    target=int(np.clip(3400*(maxdim/0.45)**0.55,500,4500)); orig=len(mesh.faces)
    if orig>target:
        red=1-target/orig
        pts,faces=fast_simplification.simplify(mesh.vertices.astype(np.float32),mesh.faces.astype(np.int32),target_reduction=red,agg=5)
        mesh=trimesh.Trimesh(vertices=pts.astype(np.float64),faces=faces,process=True)
    mesh.remove_unreferenced_vertices()
    lo,hi=mesh.bounds; center=(lo+hi)/2; dims=hi-lo
    mesh.vertices=mesh.vertices-center
    # outward-facing check
    if mesh.volume<0: mesh.invert()
    vn=mesh.vertex_normals.astype(np.float32); P=mesh.vertices.astype(np.float32); F=mesh.faces
    idx=F.astype(np.uint16 if len(P)<65536 else np.uint32).ravel()
    body=struct.pack('<4sIII',b'O3DB',len(P),len(idx),idx.itemsize)+P.tobytes()+vn.tobytes()+idx.tobytes()
    gz=gzip.compress(body,9,mtime=0); open(f'{OUT}/{bid}.bin','wb').write(gz)
    manifest[bid]=dict(fma='+'.join('FMA'+f for f in fmas),name=' + '.join(names[f] for f in fmas),vertexCount=int(len(P)),triangleCount=int(len(F)),sizeBytes=len(gz),worldCenter=[float(x) for x in center],bounds=[float(x) for x in dims])
    tot+=len(gz); ntri+=len(F)
json.dump(manifest,open(f'{OUT}/_manifest_bones.json','w'),indent=1)
print(len(manifest),'bones',ntri,'triangles',round(tot/1e6,2),'MB gz total')
