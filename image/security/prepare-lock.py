"""Add this build's solver artifact to the published exact-artifact lock."""
import hashlib
from pathlib import Path
root = Path('/build')
artifacts = list((root/'plugin-artifact').glob('conda-rattler-solver-*.conda'))
assert len(artifacts) == 1, artifacts
artifact = artifacts[0]
lock = (root/'conda-linux-64.lock').read_text()
(root/'install.lock').write_text(lock + artifact.as_uri() + '#' + hashlib.sha256(artifact.read_bytes()).hexdigest() + '\n')
