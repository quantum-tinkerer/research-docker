import pathlib,json,subprocess,ssl,hashlib,urllib.request,urllib.error,tempfile,os
P=pathlib.Path('/probe');bad=set(json.loads((P/'blocked-fingerprints.json').read_text()));ctx=ssl.create_default_context();roots=ctx.get_ca_certs(binary_form=True);assert not bad.intersection(hashlib.sha256(c).hexdigest().upper() for c in roots)
r={'openssl':ssl.OPENSSL_VERSION,'ca_file':ssl.get_default_verify_paths().cafile,'roots':len(roots),'blocked':[],'offline':[],'python_tls':{},'curl':{}}
for chain in (P/'chains').glob('*.pem'):
 p=subprocess.run(['/usr/bin/openssl','verify','-CAfile',r['ca_file'],'-no-CApath','-no-CAstore','-untrusted',str(chain),str(chain)],capture_output=True,text=True);assert p.returncode and any(x in p.stderr+p.stdout for x in ['unable to get local issuer certificate','certificate rejected','self-signed certificate']);r['offline'].append({'chain':chain.name,'rejected':True})
assert len(r['offline'])==12
with tempfile.TemporaryDirectory() as home:
 env={'PATH':'/usr/bin:/bin','HOME':home}
 for host,good in [('dv-g3b-emudhra.we-have-a-problem.com',False),('dv-g3b-aaa-emudhra.we-have-a-problem.com',False),('pypi.org',True)]:
  try:
   with urllib.request.urlopen('https://'+host,context=ctx,timeout=25) as response:assert good and response.status==200;r['python_tls'][host]={'status':response.status}
  except urllib.error.URLError as e:
   assert not good and isinstance(e.reason,ssl.SSLCertVerificationError);r['python_tls'][host]={'certificate_rejected':True,'verify_code':e.reason.verify_code}
  p=subprocess.run(['/usr/bin/curl','-q','--silent','--show-error','--output','/dev/null','--write-out','%{http_code}','--max-time','25','https://'+host],capture_output=True,text=True,env=env,timeout=30)
  assert (p.returncode==0 and p.stdout=='200') if good else p.returncode==60
  r['curl'][host]={'rc':p.returncode,'status':p.stdout,'certificate_rejected':p.returncode==60}
print(json.dumps(r))
