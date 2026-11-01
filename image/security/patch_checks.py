"""Build-only checks for this image's specific downstream patches.

RETIRE means stop and remove the named workaround, then retain/run its regression
suite. REVIEW means the input is outside the reviewed source contract. Neither
state silently applies a patch. No network or startup hooks live in this module.
See PATCHES.md next to these sources for reasons, references and removal gates.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def source_digest(files):
    digest = hashlib.sha256()
    for name, data in sorted(files.items()):
        digest.update(name.encode() + b'\0' + data + b'\0')
    return digest.hexdigest()


def python_tree(root):
    return source_digest({str(p.relative_to(root)): p.read_bytes()
                          for p in root.rglob('*.py')})


def reviewed():
    return json.loads((HERE/'reviewed-inputs.json').read_text())


def pip_vendor(root, names=('urllib3', 'msgpack')):
    """Check actual vendored code, not pip's stale BOM or top-level libraries."""
    hashes = reviewed()
    for name in names:
        digest = python_tree(root/name)
        if digest == hashes['pip_'+name+'_fixed']:
            raise RuntimeError(f'RETIRE image/pip-security.py: pip already vendors fixed {name}; retain tests/pip-vendor-probe.py')
        if digest != hashes['pip_'+name]:
            raise RuntimeError(f'REVIEW image/pip-security.py: unsupported pip vendored {name} source ({digest})')


def setting_registry(source, behavior_fixed=False):
    digest = hashlib.sha256(source).hexdigest()
    hashes = reviewed()
    if behavior_fixed or digest == hashes['settingregistry_fixed']:
        raise RuntimeError('RETIRE image/security/settingregistry.patch and source replacement in build-assets.py; retain schema-tests.js')
    if digest != hashes['settingregistry_original']:
        raise RuntimeError('REVIEW settingregistry.patch: unsupported JupyterLab source/API drift')


def solver_snapshot(source_archive):
    if hashlib.sha256(source_archive).hexdigest() != '18b436a8293cf22e34815b2e27a223bc1c63cc76a3cab6b2eb642673dd75949a':
        raise RuntimeError('REVIEW plugin-recipe.yaml: solver snapshot source changed; run upstream-refresh.py and both solver regressions')


def solver_release(requirements):
    """requirements are read from the verified released wheel's METADATA."""
    from packaging.requirements import Requirement
    rattler = [Requirement(r) for r in requirements if Requirement(r).name == 'py-rattler']
    if len(rattler) != 1:
        raise RuntimeError('REVIEW plugin-recipe.yaml: released solver dependency/API contract changed')
    if rattler[0].specifier.contains('0.28.1'):
        raise RuntimeError('RETIRE solver dev snapshot: replace solver Dockerfile stage, plugin-recipe.yaml and prepare-lock.py entry with released Conda artifact; rerun solver-probe.py')
    if str(rattler[0].specifier) != '<0.27.0a0,>=0.26.0':
        raise RuntimeError('REVIEW plugin-recipe.yaml: unsupported released solver dependency constraint')


def nbclassic(root, standalone_fixed=False, bundle_fixed=False):
    if standalone_fixed or bundle_fixed:
        which = 'nbclassic-loader.py and Underscore install-assets.py substitution' if standalone_fixed and bundle_fixed else ('Underscore install-assets.py substitution' if standalone_fixed else 'nbclassic-loader.py')
        raise RuntimeError(f'RETIRE {which}: released AMD code passes deep flatten/equality; retain browser-probe.js')
    files = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*')
             if p.is_file() and (p.suffix == '.js' or p == root/'templates/page.html')}
    if source_digest(files) != reviewed()['nbclassic']:
        raise RuntimeError('REVIEW nbclassic-loader.py: unsupported shipped AMD/template source drift')


def editor_dependency(name, version, digest, fixed_digest):
    """Digests cover the actual shipped JS/package files from verified archives."""
    if digest == fixed_digest:
        raise RuntimeError(f'RETIRE dependency-overlay.py substitution for {name}: shipped package already matches fixed official bytes; retain dependency-probe.js')
    expected = reviewed()['editor_dependencies'][name]
    if version != expected['version'] or digest != expected['sha256']:
        raise RuntimeError(f'REVIEW dependency-overlay.py: unsupported {name} source/API drift')


def editor_node(version, abi, clean_roots):
    import re
    parts = tuple(map(int, version[1:].split('.'))) if re.fullmatch(r'v22\.\d+\.\d+', version) else ()
    if parts >= (22, 23, 4) and abi == '127' and clean_roots:
        raise RuntimeError('RETIRE install-assets.py editor Node substitution: shipped fixed native runtime; retain both Node TLS modes and VSIX tests')
    if (version, abi) != ('v22.21.1', '127'):
        raise RuntimeError('REVIEW install-assets.py: unsupported editor Node/ABI; evaluate native TLS before replacing')


def fast_uri_lock(lock):
    import re
    versions = re.findall(r'"fast-uri@[^\n]+\n  version: ([^\n]+)', lock)
    if versions and all(v == '3.1.9' for v in versions):
        raise RuntimeError('RETIRE fast-uri resolution in build-assets.py and regenerate resolved-yarn.lock: upstream staging already pins the fixed release')
    if versions != ['3.1.8']:
        raise RuntimeError('REVIEW fast-uri override: unsupported JupyterLab/Ajv staging dependency graph')


def global_npm(version, digest, fixed_digest):
    if digest == fixed_digest:
        raise RuntimeError('RETIRE install-assets.py global npm replacement: shipped official npm code is fixed; retain dependency-probe.js')
    expected = reviewed()['global_npm']
    if version != expected['version'] or digest != expected['sha256']:
        raise RuntimeError('REVIEW install-assets.py global npm: unsupported shipped source/API drift')
