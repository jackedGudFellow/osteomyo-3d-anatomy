import json,subprocess,os,time
M=json.load(open('map.json'))
need=sorted({f for v in M.values() for f in v},key=int)
sha={l.split()[1].split('/')[-1][:-4]:l.split()[0] for l in open('/tmp/bp3d/meta/stl_shas.txt')}
os.makedirs('/tmp/bp3d/stl',exist_ok=True)
todo=[f for f in need if not (os.path.exists(f'/tmp/bp3d/stl/FMA{f}.stl') and os.path.getsize(f'/tmp/bp3d/stl/FMA{f}.stl')>100)]
print(len(todo),'to fetch')
ok=0
for f in todo:
    for attempt in range(3):
        r=subprocess.run(['git','-C','/tmp/bp3d/bp','cat-file','blob',sha['FMA'+f]],capture_output=True,timeout=170)
        if r.returncode==0 and len(r.stdout)>100:
            open(f'/tmp/bp3d/stl/FMA{f}.stl','wb').write(r.stdout); ok+=1; break
        time.sleep(2)
    else: print('FAILED',f)
print('fetched',ok)
