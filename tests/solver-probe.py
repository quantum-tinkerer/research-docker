import subprocess,tempfile,os,json,importlib.metadata as m,pathlib
r={'versions':{n:m.version(n) for n in ['conda','py-rattler','conda-rattler-solver']},'solvers':{}}
# Each operation uses only a new owned cache/prefix; no shared/user environment is read.
with tempfile.TemporaryDirectory() as tmp:
 env=dict(os.environ,HOME=tmp,CONDA_PKGS_DIRS=tmp+'/pkgs',CONDA_ENVS_PATH=tmp+'/envs',XDG_CACHE_HOME=tmp+'/cache')
 r['default_solver']=json.loads(subprocess.check_output(['conda','config','--show','solver','--json'],text=True,env=env))
 for solver in ['libmamba','rattler']:
  p=subprocess.run(['conda','create','--dry-run','--json','--solver='+solver,'--override-channels','-c','conda-forge','-p',tmp+'/'+solver,'python=3.13','numpy=2.5.1'],capture_output=True,text=True,env=env,timeout=300)
  d=json.loads(p.stdout);r['solvers'][solver]={'rc':p.returncode,'success':d.get('success'),'packages':[{k:x.get(k) for k in ['name','version','build']} for x in d.get('actions',{}).get('LINK',[])]};assert p.returncode==0,(solver,p.stderr[-1200:])
print(json.dumps(r))
