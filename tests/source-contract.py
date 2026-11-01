"""Cheap build-input checks; these do not replace exact-image runtime gates."""
import difflib, hashlib, json, pathlib, re
root = pathlib.Path(__file__).resolve().parents[1]
s = root / 'image/security'
records = json.loads((s/'conda-artifacts.json').read_text())
assert len(records) == len({r['name'] for r in records}) == 377
lock = (s/'conda-linux-64.lock').read_text().splitlines()
assert lock[0] == '@EXPLICIT'
assert len(lock) == 377
assert all(re.fullmatch(r'https://conda.anaconda.org/conda-forge/(linux-64|noarch)/[^#]+#[0-9a-f]{64}', line) for line in lock[1:])
assert hashlib.sha256((s/'solver-source.tar.gz').read_bytes()).hexdigest() == '18b436a8293cf22e34815b2e27a223bc1c63cc76a3cab6b2eb642673dd75949a'
for line in (root/'image/Dockerfile').read_text().splitlines():
    if line.startswith('FROM '):
        assert re.fullmatch(r'FROM (quay.io/jupyter/base-notebook@sha256:[0-9a-f]{64} AS (solver|runtime)|runtime( AS frontend)?)', line), line
# Validate the exact reviewed diff without requiring patch/git in the CI image.
path = 'packages/settingregistry/src/settingregistry.ts'
expected = ''.join(difflib.unified_diff(
    (s/'settingregistry-source.ts').read_text().splitlines(True),
    (s/'settingregistry-patched.ts').read_text().splitlines(True),
    fromfile='a/'+path, tofile='b/'+path))
assert (s/'settingregistry.patch').read_text() == expected
assert len(json.loads((root/'tests/blocked-fingerprints.json').read_text())) == 20
assert len(list((root/'tests/chains').glob('*.pem'))) == 12
print('source contracts passed; runtime and trust remain separate gates')
