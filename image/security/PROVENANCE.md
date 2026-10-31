These source files and locks originate in the tested 2026-10-30 research-base
incident packet, specifically its continued and formatter directories. No runtime
checkpoint, user home, private key, credential, or image configuration was copied.

* Public Jupyter base: quay.io/jupyter/base-notebook, amd64 manifest
  sha256:49c3267842eb52c9505dba89ebac3adf142afa73feba48d0243da3c9dbdd34d1.
* Solver: https://github.com/conda/conda-rattler-solver commit
  50108b638eed81ab9b0029812360d58dcfae7c0b. Source tarball SHA256
  18b436a8293cf22e34815b2e27a223bc1c63cc76a3cab6b2eb642673dd75949a.
  The locally rebuilt package is intentionally a development version. The old
  local artifact hash in conda-artifacts.json is historical reference only;
  prepare-lock.py hashes the newly built package for the actual installation.
* py-rattler 0.28.1 is a published Conda artifact, not a locally rebuilt binary.
  The incident packet measured zip 9.1.3, PyO3 0.29.3 and quinn-proto 0.11.19
  inside its native library. A new image inventory must verify that again.
* OpenVSCode 1.109.5 and same-ABI Node 22.23.4: official release URLs/digests in
  upstream.json. Dependency source overlays use official npm integrity records.
  shell-quote is installed directly at the final tested 1.12.0 version.
* nbclassic 1.3.3: verified upstream Underscore 1.13.8 UMD bytes with a named AMD
  alias. Old optimized definitions remain inactive; do not call them active
  exposures without testing loader resolution.
* JupyterLab 4.6.5: settingregistry.patch, original/patched TypeScript and resolved
  Yarn lock with fast-uri 3.1.9. No public settings ID or preference migration.

PyPI metadata rechecked 2026-10-31 still lists solver 0.2.0, JupyterLab 4.6.5,
nbclassic 1.3.3 and py-rattler 0.28.1. Retain backports until a compatible official
release passes the same runtime gates. Retain NSS/native trust hooks until the
actual replacement stores and TLS engines, not upstream branch bundles, pass.

`solver-tools-linux-64.lock` pins the successful solver bootstrap
environment. Conda-build still resolves its separate build-host environment.

The first independent rebuild found blocked roots in pip 26.1.2's vendored
certifi store. The lock now selects published conda-forge pip 26.2.2
(pyh145f28c_0), SHA256
5edc68a9d14102ba90d5d41e871163a90c6fa0a60b10fc8b66e44c99b92ae9ae.
Its actual downloaded cacert.pem passed all 20 fingerprint checks before adoption.
This is an explicit one-package delta from the historical 377-record inventory.
