#!/usr/bin/env python3
"""Build-time distrust of public CA source files, NSS providers and Java cacerts."""
import hashlib,os,re,subprocess,sys,base64
from pathlib import Path
FINGERPRINTS = {'0164d7ceae5bb909c272af151ff44b1177ae9b47d9424b94f1d9558c30934d19', 'fd9d5c2dbbd4995ab69b8d50c439d9527b00529199c2fd01b2174eb58f07021f', '7485b51c0ed192878fa1d2f948fb529ae1842cc5086c4b67f7be5b2039de9489', '4b2460a466f95fd40113bcdcca2ceb29b3b093921de45474da7df48874c630b1', 'cb6e15165ac802e9b3f993f16c25d41f4e81c21ebde71ae1b012ac00bf9c7c3f', 'f2edaaff3d9b701fb4d14c9f285f8c0bad90fc3bcc1fa07d47f4718edaba34a5', '5f1ded4dd590af74631290cf073b122a2aac6a1fa479778a0bd43579bd832699', 'd7a7a0fb5d7e2731d771e9484ebcdef71d5f0c3e0a2948782bc83ee0ea699ef4', 'a496e23ac0cab8155fc9b117b97eae368efcbb9041aec8804d5a308d2d01c2d8', '432ec25f0d28de9006d97bf752f17bbb2cd41f669933fcb072d9a1148d0261f3', '579480aea166290bd3c643589e795fc0d0e54e86505d180f1dff99efd3199512', '86a1ecba089c4a8d3bbe2734c612ba341d813e043cf9e8a862cd5c57a36bbe6b', 'e7568fe6e12331f4fd7de61da4c7559d0f8eb192a218d4741a3ba75184333838', '9e39de2881273acc225a149c72ba3e0f51424963669ab633ee1dc7df5db067b4', '62b7f9868263f72f6911fc78ceaf72c1979158b7368bf648683bb2aa39b02e72', '84112972b8e59d14560ae7e7119654474aad119990cf3722bfc1e3b91615e1fd', '98b896625c0c230adeec3eb2cf6aad5001ecf9156a68644e82374ce5833bc25b', '45a883f349aedfd5f3a649b5498ffb121712ba8b448f3f2a91dbc5a766fcddbe', '7dd78d5f4f13459a83dff9abbba62edbaf6f2d102bf257fd712f4d9f2746ed8d', '42c4accd12c4f59597925e1a08a7a90102608543809308d50ec427e118ba1493'}
PEM=re.compile(rb'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----',re.S)
def fingerprint(pem):return hashlib.sha256(base64.b64decode(b''.join(pem.splitlines()[1:-1]))).hexdigest()
# These directories contain public system trust anchors, not application keys.
for root in ['/usr/share/ca-certificates','/usr/local/share/ca-certificates']:
 for path in Path(root).rglob('*.crt'):
  blocks=PEM.findall(path.read_bytes())
  if any(fingerprint(p) in FINGERPRINTS for p in blocks):
   kept=[p for p in blocks if fingerprint(p) not in FINGERPRINTS]
   if kept:path.write_bytes(b'\n'.join(kept)+b'\n')
   else:path.unlink()
subprocess.run(['update-ca-certificates'],check=True)
# NSS uses an embedded root provider. Do not replace its cryptographic engine.
providers=list(Path('/usr/lib').rglob('p11-kit-trust.so'))
if len(providers)!=1:raise RuntimeError('Expected one distro p11-kit trust provider')
provider=providers[0].resolve();probe=Path(__file__).with_name('pkcs11-ca-probe.py')
subprocess.run([sys.executable,str(probe),str(provider)],check=True)
for root in ['/usr/lib','/usr/local/lib','/opt']:
 for module in Path(root).rglob('libnssckbi.so'):
  if module.resolve()==provider:continue
  # Load with this environment's library search path before changing its provider.
  env=dict(os.environ);env['LD_LIBRARY_PATH']=str(module.parent)+(':'+env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else '')
  subprocess.run([sys.executable,str(probe),str(provider)],env=env,check=True)
  module.unlink();module.symlink_to(provider)
  subprocess.run([sys.executable,str(probe),str(module)],env=env,check=True)
# Java's standard public root stores use the documented default password changeit.
# Never inspect application keystores; only installed cacerts public trust stores.
import shutil
keytool=shutil.which('keytool')
if keytool:
 seen=set()
 for root in ['/usr/lib/jvm','/etc/ssl/certs/java','/opt']:
  for path in Path(root).rglob('cacerts'):
   if not path.is_file() or path.resolve() in seen:continue
   seen.add(path.resolve())
   args=[keytool,'-J-Duser.language=en','-J-Duser.country=US','-keystore',str(path),'-storepass','changeit']
   result=subprocess.run(args+['-list','-v'],capture_output=True,text=True,check=True)
   alias=None
   for line in result.stdout.splitlines():
    if line.startswith('Alias name: '):alias=line[len('Alias name: '):]
    if 'SHA256:' in line and line.split('SHA256:',1)[1].strip().replace(':','').lower() in FINGERPRINTS:
     if not alias:raise RuntimeError('Could not identify public CA alias')
     subprocess.run(args+['-delete','-alias',alias],check=True,stdout=subprocess.DEVNULL)
print('Public native CA sources, NSS root providers and available Java stores sanitized')
