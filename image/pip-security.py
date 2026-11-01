"""Backport released pure-Python library bytes into pip's vendor namespace."""
import difflib, hashlib, io, json, pathlib, re, shutil, urllib.request, zipfile
root = pathlib.Path('/opt/conda/lib/python3.13/site-packages/pip/_vendor')
releases = json.loads(pathlib.Path('/build/pip-security.json').read_text())
# Reason/removal/tests: security/PATCHES.md (pip vendor backport).
from patch_checks import pip_vendor
pip_vendor(root, releases)
receipt = {}
for name, release in releases.items():
    data = urllib.request.urlopen(release['url'], timeout=120).read()
    assert hashlib.sha256(data).hexdigest() == release['sha256']
    archive = zipfile.ZipFile(io.BytesIO(data))
    members = [m for m in archive.namelist() if m.startswith(name+'/') and (m.endswith('.py') or m.endswith('py.typed'))]
    assert members and all('..' not in pathlib.PurePosixPath(m).parts for m in members)
    shutil.rmtree(root/name)
    changes = []
    for member in members:
        destination = root/member
        destination.parent.mkdir(parents=True, exist_ok=True)
        original = archive.read(member).decode()
        # Match pip's vendor namespace, leaving relative imports unchanged.
        modified = re.sub(r'(?m)^(\s*from )'+name+r'(\b)',r'\1pip._vendor.'+name+r'\2',original)
        def vendor_import(match):
            indent, suffix = match.groups()
            result = indent + 'from pip._vendor import ' + name
            if suffix:
                result += '\n' + indent + 'import pip._vendor.' + name + suffix
            return result
        modified = re.sub(r'(?m)^([ \t]*)import '+name+r'(\.[a-zA-Z0-9_.]+)?(?=\s*(?:#.*)?$)',vendor_import,modified)
        assert not re.search(r'(?m)^\s*import '+name+r'\b',modified), member
        destination.write_text(modified)
        changes.extend(difflib.unified_diff(original.splitlines(True),modified.splitlines(True),fromfile=member,tofile=member))
    licenses = [m for m in archive.namelist() if '.dist-info/licenses/' in m and not m.endswith('/')]
    for member in licenses:
        destination=root/name/'licenses'/pathlib.Path(member).name
        destination.parent.mkdir(exist_ok=True)
        destination.write_bytes(archive.read(member))
    assert licenses
    receipt[name] = dict(release, namespace_patch=''.join(changes), pure_python_only=True)
    vendor = root/'vendor.txt'
    text, count = re.subn(r'(?m)^([ \t]*'+name+r'==)[^\n]+',r'\g<1>'+release['version'],vendor.read_text())
    assert count == 1
    vendor.write_text(text)
pathlib.Path('/usr/local/share/research-base/pip-security.json').write_text(json.dumps(receipt,indent=2)+'\n')
