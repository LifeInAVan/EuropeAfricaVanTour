import json, os, time, urllib.request, urllib.error
CACHE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'cache')
plan=json.load(open(os.path.join(CACHE,'plan.json'), encoding='utf-8')); info=json.load(open(os.path.join(CACHE,'hl_info.json'), encoding='utf-8'))
def q(chunk):
    url=("https://router.project-osrm.org/route/v1/driving/"+";".join(f"{x},{y}" for x,y in chunk)+"?overview=false&continue_straight=false")
    for k in range(5):
        try:
            with urllib.request.urlopen(url,timeout=60) as r:
                j=json.load(r)["routes"][0]; return j["distance"], j["duration"]
        except urllib.error.HTTPError as e:
            if e.code==400: return None
            time.sleep(3*(k+1))
        except Exception: time.sleep(3*(k+1))
    return None
def dist(pts):
    D=T=0
    for s in range(0,len(pts)-1,24):
        ch=pts[s:s+25]; r=q(ch); time.sleep(0.4)
        if r is None:
            last=ch[0]
            for c in ch[1:]:
                rr=q([last,c]); time.sleep(0.4)
                if rr: D+=rr[0]; T+=rr[1]; last=c
                else: print("skip",c,flush=True)
        else: D+=r[0]; T+=r[1]
    return D,T
out=[]
for s in plan:
    D=T=0
    for p in s['parts']:
        if p['mode']!='road': continue
        g=p['geom']; pts=[tuple(g[0])]+[tuple(info[t]['coords']) for t in p['hl']]+[tuple(g[-1])]
        d,t=dist(pts); D+=d; T+=t
    out.append({"from":s['from'],"to":s['to'],"km":D/1000,"hours":T/3600}); print(s['from'],s['to'],round(D/1000),round(T/3600,1),flush=True)
json.dump(out,open(os.path.join(CACHE,'osrm_dist.json'),'w', encoding='utf-8', newline='\n'),indent=1)
