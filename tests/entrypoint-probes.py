"""Actual image entrypoint supplies UID and HOME; all data belongs to this test."""
import os,pathlib,json,subprocess
O=pathlib.Path('/out');home=pathlib.Path.home();r={'uid':os.getuid(),'home':str(home),'home_uid':home.stat().st_uid}
assert os.getuid()==1000 and str(home)=='/home/tinkerer' and home.stat().st_uid==1000
for name,script in [('probe','runtime-probe.py'),('entrypoint-scientific','scientific-smoke-continued.py')]:
 p=subprocess.run(['python','/probe/'+script],capture_output=True,text=True,timeout=360,cwd=home)
 (O/(name+'.stdout')).write_text(p.stdout);(O/(name+'.stderr')).write_text(p.stderr);r[name]={'rc':p.returncode}
 if p.returncode==0:r[name]['result']=json.loads(p.stdout)
import matplotlib
cache=pathlib.Path(matplotlib.get_cachedir());r['matplotlib_cache']={'path':str(cache),'uid':cache.stat().st_uid,'writable':os.access(cache,os.W_OK)}
assert str(cache).startswith(str(home)+'/') and cache.stat().st_uid==1000 and os.access(cache,os.W_OK)
(O/'entrypoint-probes.json').write_text(json.dumps(r,indent=2)+'\n')

assert all(r[n]['rc']==0 for n in ['probe','entrypoint-scientific']), r
