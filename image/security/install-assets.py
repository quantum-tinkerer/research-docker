"""Install pinned official release bytes; keep the scientific environment intact."""
import pathlib,json,urllib.request,hashlib,tarfile,io,subprocess,shutil,base64,os
from patch_checks import nbclassic, editor_node, source_digest, global_npm
B=pathlib.Path('/build');u=json.loads((B/'upstream.json').read_text());r={}
def get(url,sha=None,integrity=None):
 data=urllib.request.urlopen(url,timeout=180).read()
 if sha:assert hashlib.sha256(data).hexdigest()==sha
 if integrity:alg,digest=integrity.split('-',1);assert base64.b64encode(hashlib.new(alg,data).digest()).decode()==digest
 return data
editor=next(x for x in u['editor']['data']['assets'] if x['name'].endswith('linux-x64.tar.gz'));data=get(editor['browser_download_url'],editor['digest'].split(':')[1]);root=pathlib.Path('/opt/research-editor');root.mkdir()
with tarfile.open(fileobj=io.BytesIO(data)) as tf:
 for m in tf.getmembers():
  parts=pathlib.PurePosixPath(m.name).parts
  if len(parts)<2:continue
  m.name=str(pathlib.PurePosixPath(*parts[1:]));assert not m.name.startswith('/') and '..' not in pathlib.PurePosixPath(m.name).parts
  tf.extract(m,root,filter='data')
node=root/'node';r['editor_shipped_node']={k:subprocess.check_output([str(node),'-p',expr],text=True).strip() for k,expr in [('version','process.version'),('modules','process.versions.modules')]}
# Archive digest above binds the shipped runtime; native roots are checked too.
roots=json.loads(subprocess.check_output([str(node),'-e',"console.log(JSON.stringify(require('tls').rootCertificates.map(c=>new(require('crypto').X509Certificate)(c).fingerprint256.replaceAll(':',''))))"],text=True))
blocked=set(json.loads((B/'blocked-fingerprints.json').read_text()))
editor_node(r['editor_shipped_node']['version'],r['editor_shipped_node']['modules'],not blocked.intersection(roots))
n=u['selected_node_archive'];data=get(n['url'],n['sha256'])
with tarfile.open(fileobj=io.BytesIO(data),mode='r:xz') as tf:
 member=next(x for x in tf.getmembers() if x.name.endswith('/bin/node'));binary=tf.extractfile(member).read()
path=pathlib.Path('/tmp/official-node');path.write_bytes(binary);path.chmod(0o755)
abi=subprocess.check_output([str(path),'-p','process.versions.modules'],text=True).strip();assert abi==r['editor_shipped_node']['modules'],'Editor native module ABI mismatch'
# Replace only with the same-major, same-ABI official security maintenance runtime.
assert r['editor_shipped_node']['version'].split('.')[0]==n['version'].split('.')[0]
shutil.copy2(path,node);r['editor_runtime']={'version':n['version'],'modules':abi,'archive_sha256':n['sha256']}
launcher=pathlib.Path('/usr/local/bin/openvscode-server');launcher.symlink_to(root/'bin/openvscode-server')
# The package-manager-owned global npm gets a real supported npm installation.
npm=u['npm']['data']; archive=B/'npm.tgz'; archive.write_bytes(get(npm['dist']['tarball'],integrity=npm['dist']['integrity']))
with tarfile.open(archive) as tf:
 fixed_npm={str(pathlib.PurePosixPath(*pathlib.PurePosixPath(m.name).parts[1:])):tf.extractfile(m).read() for m in tf if m.isfile() and pathlib.Path(m.name).suffix in ['.js','.mjs','.cjs','.json']}
npm_root=pathlib.Path('/opt/conda/lib/node_modules/npm')
actual_npm={str(p.relative_to(npm_root)):p.read_bytes() for p in npm_root.rglob('*') if p.is_file() and p.suffix in ['.js','.mjs','.cjs','.json']}
global_npm(subprocess.check_output(['npm','--version'],text=True).strip(),source_digest(actual_npm),source_digest(fixed_npm))
subprocess.run(['npm','install','-g',str(archive),'--offline','--no-audit','--no-fund'],check=True)
# nbclassic has no patched release. Use the complete official 1.13.8 JS artifact,
# with the legacy RequireJS URL preserved by an additional byte-identical copy.
# Fail before replacing either the component or its AMD loader (PATCHES.md).
classic=pathlib.Path('/opt/conda/lib/python3.13/site-packages/nbclassic')
behavior=json.loads(subprocess.check_output(['node',str(B/'nbclassic-check.cjs'),str(classic)],text=True))
nbclassic(classic,behavior['standalone_fixed'],behavior['bundle_fixed'])
ujs=u['underscore'];data=get(ujs['dist']['tarball'],integrity=ujs['dist']['integrity']);dest=pathlib.Path('/opt/conda/lib/python3.13/site-packages/nbclassic/static/components/underscore')
if dest.exists():shutil.rmtree(dest)
dest.mkdir()
with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tf:
 for m in tf.getmembers():
  parts=pathlib.PurePosixPath(m.name).parts
  if len(parts)<2:continue
  m.name=str(pathlib.PurePosixPath(*parts[1:]));assert not m.name.startswith('/') and '..' not in pathlib.PurePosixPath(m.name).parts
  tf.extract(m,dest,filter='data')
shutil.copyfile(dest/'underscore-umd-min.js',dest/'underscore-min.js')
r['underscore']={'version':ujs['version'],'integrity':ujs['dist']['integrity'],'served_sha256':hashlib.sha256((dest/'underscore-min.js').read_bytes()).hexdigest()}
(B/'asset-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
