"""Validate an explicit local image using only fresh synthetic container storage."""
import argparse, json, pathlib, subprocess, tempfile, time, shutil
p = argparse.ArgumentParser()
p.add_argument('image')
p.add_argument('--output', type=pathlib.Path, required=True)
a = p.parse_args()
a.output = a.output.resolve(); a.output.mkdir(parents=True, exist_ok=True)
probe = pathlib.Path(__file__).resolve().parent
name = 'research-source-test-' + str(time.time_ns())
def run(args, **kw):
    return subprocess.run(args, check=True, **kw)
def container(command, label, *, root=False, entrypoint=None, env=()):
    cmd = ['podman', 'run', '--rm', '--cpus=4', '--memory=8g', '--memory-swap=8g', '-v', f'{probe}:/probe:ro', '-v', f'{a.output}:/out', '-e', 'NB_USER=tinkerer', '-e', 'GRANT_SUDO=yes', '--user=0']
    if entrypoint: cmd += ['--entrypoint', entrypoint]
    for e in env: cmd += ['-e', e]
    with (a.output/(label+'.log')).open('w') as log:
        run(cmd + [a.image, *command], stdout=log, stderr=subprocess.STDOUT, timeout=900)
# Rootless mapped user must be able to write receipts; this is a task-owned directory.
a.output.chmod(0o777)
container(['python', '/probe/inventory.py'], 'inventory')
container(['python', '/probe/entrypoint-probes.py'], 'entrypoint')
container(['bash', '/probe/pixi-probe.sh'], 'pixi')
container(['-c', 'unset SSL_CERT_FILE REQUESTS_CA_BUNDLE; /usr/bin/python3 /probe/system-native-probe.py'], 'system', entrypoint='/bin/bash')
for binary in ['/opt/conda/bin/node', '/opt/research-editor/node']:
    for mode in ['', '--use-openssl-ca']:
        container([binary, '/probe/runtime-node-tls.js'], binary.split('/')[-2] + ('-system' if mode else '-bundled'), entrypoint='/usr/bin/env', env=['NODE_OPTIONS='+mode])
container(['node', '/probe/dependency-probe.js'], 'editor-apis')
container(['python', '/probe/solver-probe.py'], 'solvers')
container(['python', '/probe/tools-probe.py'], 'retained-tools')
# Native NSS tools are installed only in this disposable diagnostic container.
container(['-c', '''before=$(dpkg-query -W -f='${Version}' libnss3); apt-get update -qq && apt-get install -y --no-install-recommends libnss3-tools && test "$before" = "$(dpkg-query -W -f='${Version}' libnss3)" && python /probe/nss-probe.py'''], 'nss', entrypoint='/bin/bash')
with tempfile.TemporaryDirectory(prefix='research-browser-') as d:
    home = pathlib.Path(d)/'home'; home.mkdir()
    settings = home/'.jupyter/lab/user-settings/jupyterlab_code_formatter'; settings.mkdir(parents=True)
    (settings/'settings.jupyterlab-settings').write_text(json.dumps({'black':{'line_length':97,'string_normalization':True},'formatOnSave':False}))
    run(['podman', 'unshare', 'chown', '-R', '1000:100', str(home)])
    try:
        run(['podman','run','-d','--name',name,'--cpus=2','--memory=4g','--memory-swap=4g','--user=0','-e','NB_USER=tinkerer','-e','GRANT_SUDO=yes','-v',f'{home}:/home/tinkerer','-v',f'{probe}:/probe:ro','-v',f'{a.output}:/out',a.image,'python','/probe/singleuser-driver.py'], stdout=subprocess.DEVNULL)
        for _ in range(120):
            if (a.output/'startup.json').exists(): break
            time.sleep(1)
        else: raise RuntimeError('singleuser startup timeout')
        with (a.output/'browser.log').open('w') as log:
            run(['podman','run','--rm','--cpus=2','--memory=4g','--memory-swap=4g','--network','container:'+name,'-v',f'{probe}:/probe:ro','-v',f'{a.output}:/out','mcr.microsoft.com/playwright:v1.64.1-noble','bash','-c','npm install --prefix /tmp/browser playwright@1.64.1 --no-audit --no-fund && node /probe/browser-probe.js'],stdout=log,stderr=subprocess.STDOUT,timeout=600)
    finally:
        run(['podman','rm','-f',name],stdout=subprocess.DEVNULL)
        run(['podman','unshare','chown','-R','0:0',str(home)])
print('Exact-image runtime gates passed:', a.image)
