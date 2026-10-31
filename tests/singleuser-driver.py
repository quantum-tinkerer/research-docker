"""Executed by the image's real tini/start.sh, against a new owned test home only."""
import os,pathlib,json,subprocess,http.server,threading,zipfile,signal,time,hashlib
O=pathlib.Path('/out');home=pathlib.Path.home();r={'uid':os.getuid(),'gid':os.getgid(),'home':str(home),'home_uid':home.stat().st_uid}
assert os.getuid()==1000 and str(home)=='/home/tinkerer' and home.stat().st_uid==1000
cache=home/'.cache';cache.mkdir(exist_ok=True);(cache/'owned-probe').write_text('synthetic')
r['cache_uid']=cache.stat().st_uid
assert r['cache_uid']==1000
r['pixi_version']=subprocess.check_output(['pixi','--version'],text=True).strip()
p=subprocess.run(['pixi','search','--channel','conda-forge','zlib'],capture_output=True,text=True,timeout=180);r['pixi_default_cache']={'rc':p.returncode,'certificate_error':'certificate' in p.stderr.lower()};assert p.returncode==0,p.stderr[-500:]
# A local offline VSIX exercises actual extension installation/activation/API use.
ext=home/'test-extensions';ext.mkdir();vsix=pathlib.Path('/tmp/synthetic-extension.vsix')
manifest={'name':'security-probe','displayName':'Research Security Probe','publisher':'research-audit','version':'0.0.1','engines':{'vscode':'^1.109.0'},'main':'./extension.js','extensionKind':['workspace'],'activationEvents':['onStartupFinished','onCommand:research.securityProbe'],'contributes':{'commands':[{'command':'research.securityProbe','title':'Research Security Probe'}]}}
js="""const vscode=require('vscode'),fs=require('fs'),cp=require('child_process');
exports.activate=ctx=>{fs.writeFileSync('/out/extension-activated.json',JSON.stringify({vscode:vscode.version,node:process.version,abi:process.versions.modules}));ctx.subscriptions.push(vscode.commands.registerCommand('research.securityProbe',async()=>{let output=cp.execFileSync('python',['-c','import json,numpy as np,os; assert np.allclose(np.linalg.solve([[2.,1.],[1.,3.]],[1.,2.]),[0.2,0.6]); print(json.dumps(dict(numpy=np.__version__,uid=os.getuid())))'],{encoding:'utf8'});fs.writeFileSync('/out/extension-command.json',JSON.stringify({passed:true,python:JSON.parse(output)}));await vscode.window.showInformationMessage('Research probe passed');}));};
"""
xml='''<?xml version="1.0" encoding="utf-8"?><PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011"><Metadata><Identity Language="en-US" Id="security-probe" Version="0.0.1" Publisher="research-audit"/><DisplayName>Research Security Probe</DisplayName><Description xml:space="preserve">Synthetic offline integration probe</Description></Metadata><Installation><InstallationTarget Id="Microsoft.VisualStudio.Code"/></Installation><Dependencies/><Assets><Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true"/></Assets></PackageManifest>'''
with zipfile.ZipFile(vsix,'w') as z:
 z.writestr('extension/package.json',json.dumps(manifest));z.writestr('extension/extension.js',js);z.writestr('extension.vsixmanifest',xml);z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="json" ContentType="application/json"/><Default Extension="js" ContentType="application/javascript"/><Default Extension="vsixmanifest" ContentType="text/xml"/></Types>')
p=subprocess.run(['openvscode-server','--install-extension',str(vsix),'--extensions-dir',str(ext),'--force'],capture_output=True,text=True,timeout=90);r['extension_install']={'rc':p.returncode,'output':p.stdout+p.stderr};assert p.returncode==0,r['extension_install']
os.environ['CODE_EXTENSIONSDIR']=str(ext)
r['installed_extensions']=subprocess.check_output(['openvscode-server','--list-extensions','--show-versions','--extensions-dir',str(ext)],text=True).splitlines()
import jupyter_vscode_proxy
r['proxy_command']=jupyter_vscode_proxy.setup_vscode()['command'](0,'')
class Hub(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def reply(self):
  body={'version':'5.5.0'} if self.path.rstrip('/')=='/hub/api' else {'name':'synthetic','admin':False,'groups':[],'kind':'user','scopes':['access:servers!server=synthetic/','access:servers!user=synthetic','read:users:name!user=synthetic']}
  data=json.dumps(body).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('X-JupyterHub-Version','5.5.0');self.end_headers();self.wfile.write(data)
 do_GET=reply
 do_POST=reply
hub=http.server.ThreadingHTTPServer(('127.0.0.1',51592),Hub);threading.Thread(target=hub.serve_forever,daemon=True).start()
os.environ.update(JUPYTERHUB_API_TOKEN='synthetic-server-only',JUPYTERHUB_CLIENT_ID='jupyterhub-user-synthetic',JUPYTERHUB_API_URL='http://127.0.0.1:51592/hub/api',JUPYTERHUB_ACTIVITY_URL='http://127.0.0.1:51592/hub/api/users/synthetic/activity',JUPYTERHUB_USER='synthetic',JUPYTERHUB_SERVER_NAME='',JUPYTERHUB_SERVICE_PREFIX='/user/synthetic/',JUPYTERHUB_SERVICE_URL='http://127.0.0.1:51591/user/synthetic/',JUPYTERHUB_BASE_URL='/',JUPYTERHUB_HOST='',JUPYTERHUB_OAUTH_CALLBACK_URL='/user/synthetic/oauth_callback',JUPYTERHUB_OAUTH_ACCESS_SCOPES='["access:servers!server=synthetic/"]')
(O/'startup.json').write_text(json.dumps(r,indent=2)+'\n')
p=subprocess.Popen(['jupyterhub-singleuser','--ip=127.0.0.1','--port=51591','--ServerApp.port_retries=0','--ServerApp.open_browser=False','--ServerApp.root_dir='+str(home),'--ServerApp.default_url=/lab','--LabApp.expose_app_in_browser=True'],cwd=home)
def stop(*a):
 p.terminate()
 try:p.wait(timeout=25)
 except subprocess.TimeoutExpired:p.kill()
 hub.shutdown();raise SystemExit(0)
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
raise SystemExit(p.wait())
