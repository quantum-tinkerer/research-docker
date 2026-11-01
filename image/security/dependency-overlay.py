"""Apply actual official security release files, not scanner/version-only edits."""
import re
from patch_checks import editor_dependency, source_digest
import json,pathlib,urllib.request,hashlib,base64,tarfile,io,shutil,subprocess,os,difflib
B=pathlib.Path('/build');releases=json.loads((B/'dependency-releases.json').read_text());editor=pathlib.Path('/opt/research-editor');npm=pathlib.Path('/opt/conda/lib/node_modules/npm');receipt={'updated':[]}
updates=[(editor/'node_modules'/n,n+'@'+v) for n,v in [('shell-quote','1.12.0'),('socks','2.8.10'),('ip-address','10.3.1'),('lodash-es','4.18.0'),('picomatch','4.0.4'),('undici','7.30.1')]]+[(npm/'node_modules/undici','undici@6.29.1')]
for dest,key in updates:
 assert dest.is_dir(),str(dest);old=json.loads((dest/'package.json').read_text());release=releases[key];data=urllib.request.urlopen(release['dist']['tarball'],timeout=120).read();alg,digest=release['dist']['integrity'].split('-',1);assert base64.b64encode(hashlib.new(alg,data).digest()).decode()==digest
 # Compare real upstream code trees before any substitution, not just versions.
 with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tf:
  fixed={str(pathlib.PurePosixPath(*pathlib.PurePosixPath(m.name).parts[1:])):tf.extractfile(m).read() for m in tf if m.isfile() and pathlib.Path(m.name).suffix in ['.js','.mjs','.cjs','.json']}
 actual={str(p.relative_to(dest)):p.read_bytes() for p in dest.rglob('*') if p.is_file() and p.suffix in ['.js','.mjs','.cjs','.json']}
 label=dest.name if str(dest).startswith(str(editor)) else 'npm/'+dest.name
 editor_dependency(label,old['version'],source_digest(actual),source_digest(fixed))
 shutil.rmtree(dest);dest.mkdir()
 with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tf:
  for m in tf.getmembers():
   parts=pathlib.PurePosixPath(m.name).parts
   if len(parts)<2:continue
   m.name=str(pathlib.PurePosixPath(*parts[1:]));assert not m.name.startswith('/') and '..' not in pathlib.PurePosixPath(m.name).parts
   tf.extract(m,dest,filter='data')
 now=json.loads((dest/'package.json').read_text());assert now['version']==release['version']
 receipt['updated'].append({'path':str(dest),'before':old['version'],'after':now['version'],'integrity':release['dist']['integrity']})
# Validate installed consumer contracts. Any root source pin changed here is a
# real source dependency patch accompanying the real code upgrade, retained as diff.
semver=npm/'node_modules/semver';patched={str(p):json.loads((p/'package.json').read_text())['version'] for p,k in updates}
diffs=[]
for prefix in [editor,npm]:
 for parent in prefix.rglob('package.json'):
  try:d=json.loads(parent.read_text())
  except Exception:continue
  oldtext=parent.read_text();changed=False;edits=[]
  for section in ['dependencies','optionalDependencies']:
   for name,requirement in list(d.get(section,{}).items()):
    cursor=parent.parent;resolved=None
    while True:
     p=cursor/'node_modules'/name
     if (p/'package.json').exists():resolved=p;break
     if cursor==prefix or cursor.parent==cursor:break
     cursor=cursor.parent
    if resolved is None or str(resolved) not in patched:continue
    version=patched[str(resolved)]
    code='const semver=require(process.argv[1]);process.exit(semver.satisfies(process.argv[2],process.argv[3])?0:1)'
    ok=subprocess.run(['node','-e',code,str(semver),version,requirement]).returncode==0
    if not ok:
     # Only update the distribution's own direct source pins. A transitive
     # incompatible consumer must be updated upstream, never forced.
     assert parent==editor/'package.json',('incompatible upstream consumer',str(parent),name,requirement,version)
     d[section][name]=version;changed=True;edits.append((name,requirement,version))
  if changed:
   newtext=oldtext
   for name,requirement,version in edits:
    pattern=r'("'+re.escape(name)+r'"\s*:\s*")'+re.escape(requirement)+r'(")'
    newtext,count=re.subn(pattern,lambda m:m.group(1)+version+m.group(2),newtext)
    assert count==1,('nonminimal source patch',str(parent),name,count)
   assert json.loads(newtext)==d
   parent.write_text(newtext);diffs.extend(difflib.unified_diff(oldtext.splitlines(True),newtext.splitlines(True),fromfile=str(parent)+'.original',tofile=str(parent)))
# Preserve the Conda Node package cache intact: it is a real package artifact,
# not the active npm installation after the explicit npm security update.
# Remaining cached-version scan findings are classified separately; no scan
# metadata or package-cache record is falsified to hide them.
receipt['node_package_cache_preserved']=True
(B/'dependency-overlay-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(B/'editor-dependency-source.patch').write_text(''.join(diffs));print(json.dumps(receipt))
