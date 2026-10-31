"""Use native NSS certutil verification with an explicit image PKCS#11 provider."""
import json,subprocess,tempfile,pathlib,re
P=pathlib.Path('/probe');r={}
def run(a):return subprocess.run(a,capture_output=True,text=True,timeout=45)
providers=sorted(set(str(p.resolve()) for root in ['/opt/conda','/usr/lib'] for p in pathlib.Path(root).glob('**/libnssckbi.so')))
assert providers
chains={p.name:p.read_text() for p in (P/'chains').glob('*.pem')};assert len(chains)==12
for host in ['dv-g3b-emudhra.we-have-a-problem.com','dv-g3b-aaa-emudhra.we-have-a-problem.com','pypi.org']:
 p=subprocess.run(['openssl','s_client','-connect',host+':443','-servername',host,'-showcerts'],input='',capture_output=True,text=True,timeout=45)
 chains[host]=p.stdout
for provider in providers:
 r[provider]={}
 for label,data in chains.items():
  certs=re.findall(r'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----',data,re.S);assert certs
  with tempfile.TemporaryDirectory() as tmp:
   db='sql:'+tmp
   assert run(['certutil','-N','-d',db,'--empty-password']).returncode==0
   p=run(['modutil','-dbdir',db,'-add','image-provider','-libfile',provider,'-force']);assert p.returncode==0,p.stderr
   for i,c in enumerate(certs):
    f=pathlib.Path(tmp)/('cert'+str(i)+'.pem');f.write_text(c)
    p=run(['certutil','-A','-d',db,'-n','chain'+str(i),'-t',',,','-i',str(f)]);assert p.returncode==0,p.stderr
   p=run(['certutil','-V','-d',db,'-n','chain0','-u','V']);good=label=='pypi.org'
   r[provider][label]={'rc':p.returncode,'message':(p.stdout+p.stderr).strip()}
   assert (p.returncode==0)==good,r[provider][label]
print(json.dumps(r))
