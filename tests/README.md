Run `python3 tests/source-contract.py` before building, then `tests/build-local.sh`.
Use `python3 tests/run-image.py sha256:<local-image-id> --output build-evidence/runtime`
to rerun runtime gates without rebuilding. This runner creates disposable rootless
containers only; it does not connect to fleet hosts or mount existing user homes.
The browser test uses Playwright directly (not the user's browser session).

Public trust fixtures come from
`admin-notes/security/emudhra-20261021/blocked-fingerprints.json` and
`admin-notes/security/emudhra-20261021/chains/*.pem`. The paths name captured
public certificate chains, not credentials or runtime bundles. No private-key
TLS replay is claimed. Live badchain endpoints must fail specifically with a
certificate error; network timeouts do not pass. PyPI is the positive control.

Required gates: real startup and UID/home ownership, repeated persistent Pixi,
real kernel and scientific/plotting smoke, both Conda solvers, editor library
APIs, offline VSIX activation/command through the real launcher, nbclassic AMD
resolution/deep regressions, original formatter-ID load/save/reload and invalid
setting rejection, compiled schema cases, system/Conda/certifi/pip trust,
PKCS#11/NSS and both Node runtimes in bundled and OpenSSL modes.

Scanner evidence must be collected on the final image, retaining raw findings
and an applicability table. VS Code extension names such as `npm` or `diff`
are not automatically npm-library identities. Old package caches are not
runtime exposures without installed inode/symlink or loader evidence. Static
source checks, historical candidate results and copied test code are not
passing runtime receipts for a new image.
