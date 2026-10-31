"""Measure actual installed records and selected imports, without exporting Env."""
import hashlib, importlib, importlib.metadata, json, pathlib, subprocess
for name in ['gitconfig', 'gitattributes', 'gitignore']:
    assert (pathlib.Path('/opt/conda/etc')/name).is_file(), name
expected = json.loads(pathlib.Path('/build/conda-artifacts.json').read_text())
actual = [json.loads(p.read_text()) for p in pathlib.Path('/opt/conda/conda-meta').glob('*.json')]
by_name = {r['name']:r for r in actual}
assert len(by_name) == len(actual) == len(expected)
for r in expected:
    got = by_name[r['name']]
    assert (got['version'],got['build']) == (r['version'],r['build']), r['name']
    if r['name'] != 'conda-rattler-solver': assert got['sha256'] == r['sha256'], r['name']
imports = {}
for module, version in [('numpy','2.5.1'),('pandas','3.0.3'),('matplotlib','3.10.9'),('panel','1.9.3'),('plotly','6.9.0'),('bokeh','3.9.1'),('ipympl','0.10.0'),('ipywidgets','8.1.8')]:
    m = importlib.import_module(module)
    assert m.__version__ == version, (module,m.__version__)
    imports[module] = {'version':m.__version__,'file':m.__file__}
rattler = list(pathlib.Path('/opt/conda/lib/python3.13/site-packages').glob('rattler/*.so'))
assert rattler
print(json.dumps({'conda':[{k:r.get(k) for k in ['name','version','build','sha256']} for r in actual], 'imports':imports,'rattler_native':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in rattler},'os_packages':subprocess.check_output(['dpkg-query','-W','-f=${Package}\t${Version}\n'],text=True)},indent=2))
