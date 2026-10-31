"""Build from image-supplied pinned staging lock and verified upstream source."""
import pathlib,json,subprocess,hashlib,shutil,base64
B=pathlib.Path('/build');S=pathlib.Path('/opt/conda/lib/python3.13/site-packages/jupyterlab/staging');A=B/'app';shutil.copytree(S,A,ignore=shutil.ignore_patterns('node_modules','build'));r={}
def run(args):subprocess.run(args,cwd=A,check=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r['input_lock_sha256']=sha(A/'yarn.lock')
p=json.loads((A/'package.json').read_text());p['resolutions']['fast-uri']='3.1.9';p['jupyterlab']['outputDir']='../output';(A/'package.json').write_text(json.dumps(p,indent=2)+'\n')
shutil.copy2(B/'resolved-yarn.lock',A/'yarn.lock')
run(['jlpm','install','--immutable'])
P=A/'node_modules/@jupyterlab/settingregistry';metadata=json.loads((P/'package.json').read_text());assert metadata['version']=='4.6.5'
assert sha(P/'src/settingregistry.ts')==sha(B/'settingregistry-source.ts'), 'npm/source release mismatch'
shutil.copy2(B/'settingregistry-patched.ts',P/'src/settingregistry.ts')
# The source is compiled, never searched/replaced inside minified assets.
run(['npm','install','--prefix','/build/typescript','typescript@5.9.3','--no-audit','--no-fund'])
run(['node','/build/typescript/node_modules/typescript/bin/tsc','--noEmit','--target','ES2018','--module','ESNext','--moduleResolution','node','--esModuleInterop','--resolveJsonModule','--skipLibCheck',str(P/'src/settingregistry.ts')])
run(['node','-e',"const fs=require('fs'),ts=require('/build/typescript/node_modules/typescript');const p=process.argv[1];const out=ts.transpileModule(fs.readFileSync(p+'/src/settingregistry.ts','utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2018,module:ts.ModuleKind.ESNext,sourceMap:false}});if(out.diagnostics?.length)throw Error(JSON.stringify(out.diagnostics));fs.writeFileSync(p+'/lib/settingregistry.js',out.outputText)",str(P)])
r['compiled_registry_sha256']=sha(P/'lib/settingregistry.js');r['patched_source_sha256']=sha(P/'src/settingregistry.ts');r['settingregistry_version']=metadata['version'];r['typescript']='5.9.3';r['output_lock_sha256']=sha(A/'yarn.lock')
run(['node','-e',"const fs=require('fs'),path=require('path'),semver=require('semver');const registry=require('./node_modules/@jupyterlab/settingregistry/package.json');const ajvPath=require.resolve('ajv/package.json',{paths:[path.resolve('node_modules/@jupyterlab/settingregistry')]});const ajv=require(ajvPath);const uri=require(require.resolve('fast-uri/package.json',{paths:[path.dirname(ajvPath)]}));if(!semver.satisfies(ajv.version,registry.dependencies.ajv)||!semver.satisfies(uri.version,ajv.dependencies['fast-uri']))throw Error('dependency constraint violation');fs.writeFileSync('/build/runtime-js-dependencies.json',JSON.stringify({registry:registry.version,ajv:ajv.version,ajv_constraint:registry.dependencies.ajv,fast_uri:uri.version,fast_uri_constraint:ajv.dependencies['fast-uri']},null,2))"])
r['runtime_js_dependencies']=json.loads((B/'runtime-js-dependencies.json').read_text())
run(['jlpm','run','build:prod:minimize'])
# Package build emits assets into build; ship exactly that output as JupyterLab static.
output=A/'build';assert (output/'package.json').exists();r['assets']={x.name:sha(x) for x in output.iterdir() if x.is_file()}
(B/'asset-receipt.json').write_text(json.dumps(r,indent=2)+'\n')
