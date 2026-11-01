#!/usr/bin/env python3
"""Explicit, build-time-only refresh of released artifacts, independent of pins.

Does not update a lock or apply a patch. RETIRE and unknown source/API changes
both exit nonzero. After either result, review the named source, update/remove
it and run the retained exact-image regressions. Never call this at startup.
"""
import argparse
import base64
import email
import hashlib
import io
import json
from pathlib import Path
import re
import ssl
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'image/security'))
import patch_checks as checks


def get(url):
    return urllib.request.urlopen(url,timeout=120).read()


def verified(url,sha=None,integrity=None):
    data=get(url)
    if sha and hashlib.sha256(data).hexdigest()!=sha:
        raise RuntimeError('REVIEW published artifact hash mismatch: '+url)
    if integrity:
        algorithm,value=integrity.split('-',1)
        if base64.b64encode(hashlib.new(algorithm,data).digest()).decode()!=value:
            raise RuntimeError('REVIEW published artifact integrity mismatch: '+url)
    return data


def npm_files(metadata):
    raw=verified(metadata['dist']['tarball'],integrity=metadata['dist']['integrity'])
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        return {str(Path(*Path(m.name).parts[1:])):archive.extractfile(m).read()
                for m in archive if m.isfile() and '..' not in Path(m.name).parts}


def write_files(root,files):
    for name,data in files.items():
        path=Path(name)
        if path.is_absolute() or '..' in path.parts:
            raise RuntimeError('REVIEW unsafe published archive path')
        destination=root/path;destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(data)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    receipts={};errors=[]
    def check(name,fn):
        try:
            detail=fn();receipts[name]={'status':'reviewed affected input / retained configuration','detail':detail}
        except Exception as error:
            detail=str(error)
            if not detail.startswith(('RETIRE','REVIEW')):detail='REVIEW '+name+': released artifact/API check failed: '+detail
            receipts[name]={'status':'ERROR','detail':detail};errors.append(name)
    blocked=set(json.loads((ROOT/'tests/blocked-fingerprints.json').read_text()))
    def ca_file(data):
        certs=re.findall(b'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----',data,re.S)
        if not certs:raise RuntimeError('REVIEW empty released CA store')
        hits=blocked.intersection(hashlib.sha256(ssl.PEM_cert_to_DER_cert(c.decode())).hexdigest().upper() for c in certs)
        if hits:raise RuntimeError('REVIEW blocked roots in actual released CA bundle')
        return len(certs)
    with tempfile.TemporaryDirectory(prefix='research-upstream-') as temporary:
        temporary=Path(temporary)
        wheels={}
        for name in ['conda-rattler-solver','jupyterlab','nbclassic','pip','certifi']:
            meta=json.loads(get('https://pypi.org/pypi/'+name+'/json'))
            artifact=next(f for f in meta['urls'] if f['filename'].endswith('none-any.whl') and not f['yanked'])
            data=verified(artifact['url'],sha=artifact['digests']['sha256'])
            archive=zipfile.ZipFile(io.BytesIO(data));files={n:archive.read(n) for n in archive.namelist() if not n.endswith('/')}
            directory=temporary/name;write_files(directory,files);wheels[name]=(directory,files)
            receipts[name+'_release']={'version':meta['info']['version'],'url':artifact['url'],'sha256':artifact['digests']['sha256']}
        def solver():
            files=wheels['conda-rattler-solver'][1]
            metadata=email.message_from_bytes(next(v for k,v in files.items() if k.endswith('.dist-info/METADATA')))
            requirements=metadata.get_all('Requires-Dist',[]);checks.solver_release(requirements);return requirements
        check('solver snapshot',solver)
        def classic():
            directory=wheels['nbclassic'][0]/'nbclassic'
            result=json.loads(subprocess.check_output(['node',str(ROOT/'image/security/nbclassic-check.cjs'),str(directory)],text=True))
            checks.nbclassic(directory,result['standalone_fixed'],result['bundle_fixed']);return result
        check('nbclassic AMD',classic)
        check('pip vendor backport',lambda:checks.pip_vendor(wheels['pip'][0]/'pip/_vendor',json.loads((ROOT/'image/pip-security.json').read_text())))
        check('pip actual CA store',lambda:ca_file(wheels['pip'][1]['pip/_vendor/certifi/cacert.pem']))
        check('certifi actual CA store',lambda:ca_file(wheels['certifi'][1]['certifi/cacert.pem']))
        check('fast-uri resolution',lambda:checks.fast_uri_lock(wheels['jupyterlab'][1]['jupyterlab/staging/yarn.lock'].decode()))
        meta=json.loads(get('https://registry.npmjs.org/@jupyterlab/settingregistry/latest'));files=npm_files(meta)
        receipts['settingregistry_release']={'version':meta['version'],'url':meta['dist']['tarball'],'integrity':meta['dist']['integrity']}
        def registry():
            # Probe the actual released compiled class with its declared Ajv/json5
            # dependencies; an unfamiliar but fixed implementation must retire,
            # rather than being classified by a version number alone.
            directory=temporary/'settingregistry';write_files(directory,files)
            dependencies=temporary/'validator-dependencies'
            user_config=temporary/'npm-user.conf';user_config.write_text('')
            global_config=temporary/'npm-global.conf';global_config.write_text('')
            with (args.output/'validator-dependencies.log').open('w') as log:
                subprocess.run(['npm','install','--prefix',str(dependencies),'--ignore-scripts','--no-audit','--no-fund','--userconfig='+str(user_config),'--globalconfig='+str(global_config),
                    'ajv@'+meta['dependencies']['ajv'],'json5@'+meta['dependencies']['json5']],check=True,stdout=log,stderr=subprocess.STDOUT,timeout=120)
            (directory/'node_modules').symlink_to(dependencies/'node_modules',target_is_directory=True)
            behavior=json.loads(subprocess.check_output(['node',str(ROOT/'image/security/settingregistry-check.cjs'),str(directory)],text=True))
            (args.output/'validator-package-lock.json').write_bytes((dependencies/'package-lock.json').read_bytes())
            checks.setting_registry(files['src/settingregistry.ts'],behavior['fixed']);return behavior
        check('settingregistry patch',registry)
        uri=json.loads(get('https://registry.npmjs.org/fast-uri'))
        receipts['fast_uri_latest']={'latest':uri['dist-tags']['latest'],'latest_compatible_3':max((v for v in uri['versions'] if re.fullmatch(r'3\.\d+\.\d+',v)),key=lambda v:tuple(map(int,v.split('.'))))}
        editor=json.loads(get('https://api.github.com/repos/gitpod-io/openvscode-server/releases/latest'))
        asset=next(a for a in editor['assets'] if a['name'].endswith('linux-x64.tar.gz'))
        raw=verified(asset['browser_download_url'],sha=asset['digest'].removeprefix('sha256:'))
        with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
            files={str(Path(*Path(m.name).parts[1:])):archive.extractfile(m).read() for m in archive if m.isfile()}
        receipts['editor_release']={'version':editor['tag_name'],'url':asset['browser_download_url'],'sha256':asset['digest']}
        binary=temporary/'editor-node';binary.write_bytes(files['node']);binary.chmod(0o755)
        native=json.loads(subprocess.check_output([str(binary),'-e',"console.log(JSON.stringify({version:process.version,abi:process.versions.modules,roots:require('tls').rootCertificates.map(c=>new(require('crypto').X509Certificate)(c).fingerprint256.replaceAll(':',''))}))"],text=True,env={'PATH':'/usr/bin:/bin','HOME':str(temporary)}))
        check('editor native Node',lambda:checks.editor_node(native['version'],native['abi'],not blocked.intersection(native['roots'])))
        releases=json.loads((ROOT/'image/security/dependency-releases.json').read_text())
        for name,target in [('shell-quote','1.12.0'),('socks','2.8.10'),('ip-address','10.3.1'),('lodash-es','4.18.0'),('picomatch','4.0.4'),('undici','7.30.1')]:
            prefix='node_modules/'+name+'/'
            actual={k[len(prefix):]:v for k,v in files.items() if k.startswith(prefix) and Path(k).suffix in ['.js','.mjs','.cjs','.json']}
            fixed={k:v for k,v in npm_files(releases[name+'@'+target]).items() if Path(k).suffix in ['.js','.mjs','.cjs','.json']}
            version=json.loads(actual['package.json'])['version']
            check('editor '+name,lambda n=name,v=version,a=actual,f=fixed:checks.editor_dependency(n,v,checks.source_digest(a),checks.source_digest(f)))
        # npm is independently installed, so refresh its actual current tarball too.
        npm=json.loads(get('https://registry.npmjs.org/npm/latest'));files=npm_files(npm);prefix='node_modules/undici/'
        actual={k[len(prefix):]:v for k,v in files.items() if k.startswith(prefix) and Path(k).suffix in ['.js','.mjs','.cjs','.json']}
        fixed={k:v for k,v in npm_files(releases['undici@6.29.1']).items() if Path(k).suffix in ['.js','.mjs','.cjs','.json']}
        check('npm undici',lambda:checks.editor_dependency('npm/undici',json.loads(actual['package.json'])['version'],checks.source_digest(actual),checks.source_digest(fixed)))
        receipts['npm_release']={'version':npm['version'],'url':npm['dist']['tarball'],'integrity':npm['dist']['integrity']}
        # Global npm comes from the supported Conda Node 22 artifact. Inspect the
        # moving released artifact, independent of conda-linux-64.lock.
        conda=json.loads(get('https://api.anaconda.org/package/conda-forge/nodejs'))
        candidates=[f for f in conda['files'] if f.get('attrs',{}).get('subdir')=='linux-64' and re.fullmatch(r'22\.\d+\.\d+',f['version'])]
        artifact=max(candidates,key=lambda f:(tuple(map(int,f['version'].split('.'))),f['attrs'].get('build_number',0)))
        url='https://conda.anaconda.org/conda-forge/'+artifact['basename']
        raw=verified(url,sha=artifact['sha256']);archive=zipfile.ZipFile(io.BytesIO(raw))
        data=archive.read(next(n for n in archive.namelist() if n.startswith('pkg-')))
        data=subprocess.check_output(['zstd','-dc'],input=data)
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            prefix='lib/node_modules/npm/'
            actual={m.name[len(prefix):]:archive.extractfile(m).read() for m in archive if m.isfile() and m.name.startswith(prefix) and Path(m.name).suffix in ['.js','.mjs','.cjs','.json']}
        pinned=json.loads((ROOT/'image/security/upstream.json').read_text())['npm']['data']
        fixed={k:v for k,v in npm_files(pinned).items() if Path(k).suffix in ['.js','.mjs','.cjs','.json']}
        check('Conda global npm',lambda:checks.global_npm(json.loads(actual['package.json'])['version'],checks.source_digest(actual),checks.source_digest(fixed)))
        receipts['conda_node_release']={'version':artifact['version'],'url':url,'sha256':artifact['sha256']}

    (args.output/'upstream-refresh.json').write_text(json.dumps(receipts,indent=2)+'\n')
    for name,result in receipts.items():
        if 'status' in result:print(name+': '+result['status']+((': '+result['detail']) if result['status']=='ERROR' else ''))
    return bool(errors)


if __name__=='__main__':
    raise SystemExit(main())
