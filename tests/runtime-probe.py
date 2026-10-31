import asyncio,hashlib,importlib.metadata as m,json,os,pathlib,re,ssl,subprocess,sys,tempfile,time,urllib.error,urllib.request,socket
import certifi
import atexit
P=pathlib.Path('/probe');R={'packages':{d.metadata['Name']:d.version for d in m.distributions()}}
def run(a):
 p=subprocess.run(a,text=True,capture_output=True,timeout=180)
 if p.returncode: raise RuntimeError(a[0]+' failed: '+p.stderr[-1000:])
 return p.stdout.strip()
atexit.register(lambda: print(json.dumps(R)))
# A real kernel executes scientific Python against shipped native libraries.
import nbformat
from nbclient import NotebookClient
code="""import numpy as np
from PIL import Image
import brotli,git,jwt,cryptography,aiohttp,tornado,urllib3,rattler
x=np.array([[2.,1.],[1.,3.]])
assert np.allclose(x@np.linalg.solve(x,np.array([1.,2.])),[1.,2.])
assert np.allclose(np.linalg.eigvalsh(x),[1.381966011250105,3.618033988749895])
assert brotli.decompress(brotli.compress(b'science-smoke'))==b'science-smoke'
assert Image.new('RGB',(4,4)).resize((8,8)).size==(8,8)
print('native scientific kernel passed')
"""
nb=nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(code)])
with tempfile.TemporaryDirectory() as d:
 NotebookClient(nb,timeout=120,kernel_name='python3',resources={'metadata':{'path':d}}).execute()
 R['kernel']={'passed':True,'outputs':[x.get('text') for x in nb.cells[0].outputs]}
# Real Jupyter Server process and HTTP API using only synthetic container storage.
with tempfile.TemporaryDirectory() as d:
 port=51567
 with open(d+'/server.log','w') as log:
  p=subprocess.Popen(['jupyter','server','--no-browser','--ServerApp.ip=127.0.0.1','--ServerApp.port='+str(port),'--ServerApp.port_retries=0','--ServerApp.token=','--ServerApp.password=','--ServerApp.root_dir='+d],cwd=d,stdout=log,stderr=log)
  try:
   for _ in range(45):
    try:
     with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/api/status',timeout=2) as resp:
      assert resp.status==200;R['jupyter_server']={'status':resp.status};break
    except urllib.error.URLError: pass
    assert p.poll() is None,'server exited'
    time.sleep(1)
   else:raise RuntimeError('server startup timeout')
  finally:p.terminate();p.wait(timeout=20)

# Inspect public CA bundles and active contexts; never read private keys/config.
bad=set(json.loads((P/'blocked-fingerprints.json').read_text()));R['ca_files']={}
paths={pathlib.Path(p).resolve() for p in ['/etc/ssl/certs/ca-certificates.crt', certifi.where(), '/opt/conda/ssl/cert.pem', __import__('pip._vendor.certifi',fromlist=['where']).where()]}
for f in sorted(paths):
 data=f.read_bytes(); certs=re.findall(b'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----',data,re.S)
 hits=[hashlib.sha256(ssl.PEM_cert_to_DER_cert(x.decode())).hexdigest().upper() for x in certs]
 assert not bad.intersection(hits),str(f)
 if certs:R['ca_files'][str(f)]={'certificates':len(certs),'sha256':hashlib.sha256(data).hexdigest()}
# Extra GitLab HTTP availability and native TLS controls are retained separately in gitlab-tls.json.
R['tls']={};stores={'default':None,'conda':'/opt/conda/ssl/cert.pem','certifi':certifi.where(),'system':'/etc/ssl/certs/ca-certificates.crt','pip_vendor':__import__('pip._vendor.certifi',fromlist=['where']).where()}
for name,store in stores.items():
 ctx=ssl.create_default_context(cafile=store);assert not bad.intersection(hashlib.sha256(x).hexdigest().upper() for x in ctx.get_ca_certs(binary_form=True))
 R['tls'][name]={}
 for host,good in [('dv-g3b-emudhra.we-have-a-problem.com',False),('dv-g3b-aaa-emudhra.we-have-a-problem.com',False),('pypi.org',True)]:
  print('TLS probe:',name,host,file=sys.stderr,flush=True)
  try:
   with urllib.request.urlopen('https://'+host,context=ctx,timeout=25) as r:assert good and r.status==200;R['tls'][name][host]={'status':r.status}
  except urllib.error.URLError as e:
   assert not good and isinstance(e.reason,ssl.SSLCertVerificationError)
   R['tls'][name][host]={'certificate_rejected':True,'verify_code':e.reason.verify_code}
R['offline_chains']=[]
for store in set([ssl.get_default_verify_paths().cafile, *[p for p in stores.values() if p]]):
 for chain in (P/'chains').glob('*.pem'):
  p=subprocess.run(['openssl','verify','-CAfile',store,'-no-CApath','-no-CAstore','-untrusted',str(chain),str(chain)],capture_output=True,text=True)
  assert p.returncode and any(s in p.stderr+p.stdout for s in ['unable to get local issuer certificate','certificate rejected','self-signed certificate'])
  R['offline_chains'].append({'store':store,'chain':chain.name,'rejected':True})
# Node native TLS with active OpenSSL CA mode.
R['node_tls']=json.loads(run(['node',str(P/'runtime-node-tls.js')]))

R['nss']={}
for p in [*pathlib.Path('/opt/conda').glob('**/libnssckbi.so'),*pathlib.Path('/usr/lib').glob('**/libnssckbi.so')]:
 R['nss'][str(p)]={'target':str(p.resolve()),'probe':json.loads(run([sys.executable,'/probe/pkcs11-ca-probe.py',str(p)]))}
assert R['nss'],'No NSS provider tested'
