# Independent notebook source handoff — 2026-10-31

The clean-source candidate builds and passes the exact-image runtime/trust suite.
It is ready for source review, **not an unconditional release approval**. Nothing
was pushed, tagged, merged, published or deployed. Admin-notes and live hosts,
containers, routing, databases, credentials and deployment pins were untouched.

## Identity and provenance

- Branch: `cleanup/reproducible-security-20261031`.
- Build source commit: `4aa893c4d865e14043aff0ef0ee617056f20801b`.
- Final local image: `sha256:3579555e313c0e96df877b49b628d083770604e6951b84aff9d1d881444fc289`.
- Local tag: `localhost/research-source:20261031` (not a registry digest).
- Export: `build-evidence/candidate.tar`, SHA256
  `5c424d779ebb29c4a0518e682d25711f6b8613752f6232a08662a079688d0593`.
- Public amd64 base:
  `quay.io/jupyter/base-notebook@sha256:49c3267842eb52c9505dba89ebac3adf142afa73feba48d0243da3c9dbdd34d1`.
- OS inputs: Ubuntu snapshot `20261031T000000Z`.
- Rebuilt solver package SHA256:
  `133e4070ede382845ff7c7d38c03f62c03b72b004ca4fbd3841b5a754b200dfd`.

No Dockerfile stage uses a host-local checkpoint. Rootless local builds and tests
used at most four CPUs/eight GiB, with memory/disk preflight; browser and server
split that budget. All owned runtime-test containers and temporary homes were
removed. The synthetic singleuser driver's teardown required SIGKILL after its
10-second grace period; graceful shutdown is not established by this harness.

[Machine-readable results](validation/20261031/summary.json),
[all 22 reported high/critical classifications](validation/20261031/scan-applicability.json),
and [evidence hashes](validation/20261031/evidence-sha256.json) are committed.
Detailed logs, inventories, browser receipts and the export remain locally under
`build-evidence/`; they are intentionally not added to Git.

## Fixes carried into source

The 377-package Conda inventory retains Python 3.13.14 and the tested numerical,
plotting and widget versions. The explicit lock reconstructs the prefix rather
than inheriting old packages. The one additional package update is official
conda-forge pip 26.2.2: the first independent build exposed blocked roots in
26.1.2's vendored certifi bundle. The actual released 26.2.2 artifact passed all
20 fingerprint checks, followed by native TLS checks in the final image.

OpenVSCode 1.109.5 uses official same-ABI Node 22.23.4, verified released dependency
bytes, IPv4 launcher binding and the modern proxy folder URL. nbclassic 1.3.3
loads the verified Underscore 1.13.8 AMD alias. JupyterLab 4.6.5 is compiled with
the setting-registry source patch and immutable fast-uri 3.1.9 Yarn lock. Public
formatter IDs, schema references and preference paths remain unchanged.

conda-rattler-solver is genuinely rebuilt from upstream commit
`50108b638eed81ab9b0029812360d58dcfae7c0b` as `0.2.1.dev0+g50108b638`.
Published py-rattler 0.28.1 provides the native fix; final binary inventory
confirms zip 9.1.3, PyO3 0.29.3 and quinn-proto 0.11.19. Current released solver
0.2.0 does not provide the required py-rattler compatibility.

pip 26.2.2 still bundled older urllib3/msgpack, so a narrow source backport installs
SHA256-verified released urllib3 2.8.0/msgpack 1.2.4 Python files into its vendor
namespace. It retains pure-Python msgpack, upstream licenses, exact namespace
diffs and a receipt. Actual vendor pins change with the code; the original BOM
is retained and explicitly classified rather than rewritten to erase findings.

## Validation

- All 377 Conda records and scientific imports match the intended versions;
  real kernel linear algebra, imaging, plotting/dataframes/widgets and Jupytext
  round-trip pass. Both libmamba and rattler solve the real test request.
- Real entrypoint gives UID 1000 an owned `/home/tinkerer` and writable default
  caches. Pixi fresh/repeated startup, old-version upgrade, newer-version
  preservation, valid channel access and bad-chain rejection pass.
- Real singleuser/fake-Hub flow, launcher/editor, offline VSIX activation and
  command invoking scientific Python pass. nbclassic executes the expected
  asset and deep flatten/equality regressions.
- Original formatter preferences load, save and survive browser reload; invalid
  settings are rejected without persistence. Black changes one real document
  without errors. All 93 loaded schemas and 26 additional schema cases pass.
- System, Conda, certifi, pip-vendor and default Python trust pass, including
  48 offline PEM checks. Native NSS rejects all 12 captured chains and both
  live badchains, and accepts PyPI. Both Node runtimes pass bundled/OpenSSL modes.
- pip consistency, actual pip index access, CacheControl serialization and
  vendored Requests TLS pass. All 20 blocked fingerprints remain excluded.
- Static source contracts, Python compilation, shell syntax and diff checks pass.

Trivy 0.76.1 ran vulnerability-only with `--ignore-unfixed`, without an ignore
list. Raw counts remain **3 critical / 19 high**: 17 editor identity mismatches,
four original pip-BOM references to replaced library versions, and one
setuptools report targeting absent `PackageIndex` code (only its pkg_resources
subset is vendored; full installed setuptools is 83.0.0). No applicable active
high/critical finding was established among these reports. This is not complete
Conda or compiled-JavaScript advisory coverage; medium/low findings remain.

## Outstanding exceptions and release readiness

The build is independent of the fleet's local image chain. Bit-identical repeat
builds are not established: Conda-build still resolves its separate build-host
environment; pip build isolation/artifact locking and the TypeScript bootstrap
need further locking. Solver bootstrap, runtime Conda, editor archives, pip
vendor replacements and frontend dependency graph are pinned.

**Deliberate compatibility deviation:** Git-LFS and Inkscape now come from the
Ubuntu snapshot, replacing the mutable external setup script/PPA. Inkscape is
1.2.2-2ubuntu12; compatibility with workflows needing newer PPA features is not
validated. This requires review before release.

The solver development snapshot, nbclassic loader adapter, formatter patch and
pip vendor backport remain maintained source exceptions. Replace them only when
official releases pass equivalent tests. NSS/native trust hooks remain: clean
upstream branch bundles alone do not justify removing them. Publication should
retain the immutable source/base/artifacts and receipts and address the locking,
Inkscape and coverage exceptions above. No publication or fleet rollout is part
of this handoff.
