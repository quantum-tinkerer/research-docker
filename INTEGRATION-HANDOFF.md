# Notebook source integration — 2026-11-01

The source candidate includes explicit per-patch application, retirement and drift
checks. The exact image passes the complete runtime suite and a fresh scan.
Source integration is authorized; image publication, release exceptions and fleet
rollout are separate and have not been approved. The October 31 handoff remains
an unchanged historical evidence record except for its link to this follow-up.

## Artifact and upstream review

- Local image: `sha256:694d627c2cc5873ee97cca6c61a45ba64dd00ba8d950907dbe46be1091be1821`.
- Local tag: `localhost/research-source:20261101-final`; no registry publication.
- Docker archive SHA256: `a9b9d8ce6ae841bfbb37137739ecc2f4b58446cf6d53c1e19d26b23e7cfaae3c`.
- Archive: ignored `build-evidence/integration-20261101/candidate.tar`.
- All [image input hashes](validation/20261101/build-context.json),
  [validation summary](validation/20261101/summary.json),
  [released artifact checks](validation/20261101/upstream-refresh.json), and
  [local evidence hashes](validation/20261101/evidence-sha256.json) are recorded.

Current released artifacts still require the solver development snapshot,
JupyterLab 4.6.5 registry patch and fast-uri 3.1.9 resolution, OpenVSCode 1.109.5
Node/dependency substitutions, nbclassic AMD adapter, and pip 26.2.2 vendor
backports. The actual latest compatible Conda Node 22.23.4 still supplies npm
10.9.9. The refresh executes actual released nbclassic/Node/registry code, reads
verified solver metadata and pip/npm source trees, and scans actual CA bundles.
It is independent of build pins and never runs at notebook startup.

**Retired:** the blanket NSS provider replacement. No Conda NSS package is locked;
the original Ubuntu snapshot libnss3 provider exposes 169 certificates with zero
blocked fingerprints and passes all offline/live native chain checks. The final
image uses the original provider. The permanent tests remain.

The specific reasons, upstream references and removal gates are adjacent to the
patches in [PATCHES.md](image/security/PATCHES.md). Unknown bytes/APIs require
review; incorporated fixes stop with the precise patch/configuration to retire.
Ordinary proxy/home/SSH behavior retains normal regression coverage.

## Exact-image validation

The bounded rootless build uses the same public digest and Ubuntu snapshot as
the previous candidate, with no local checkpoint ancestry. Eight transition
contracts, source contracts and before/after compiled-validator checks pass.
The full real-image suite was rerun: owned default home, persistent Pixi
old/current/newer behavior, both solvers, scientific kernel/imports, real
launcher/editor/offline VSIX, nbclassic deep AMD regressions, original formatter
preference load/save/reload, Black formatting, 93 schemas and 26 schema cases.
System/Conda/certifi/pip/default trust, both native Node modes, 48 offline PEM
checks, native NSS's 12 captured chains and live positive/negative TLS pass.

The fresh Trivy scan has exactly the previous finding set: 3 critical, 19 high,
29 medium, 7 low. The [22 high/critical classifications](validation/20261031/scan-applicability.json)
remain applicable: 17 editor extension identity mismatches, four stale pip BOM
references, one absent setuptools PackageIndex implementation. Actual installed
vendor imports and editor identities were retested. This is not comprehensive
Conda/compiled-JavaScript coverage or acceptance of residual findings.

## CI and integration boundary

Main previously published `combined:main` implicitly. CI now runs patch contracts
and a no-push/no-cache-push build, with no registry credential preparation or
release job. Project Auto DevOps is disabled, push webhooks are empty, and the
remaining Mattermost integration provides push notifications. The managed Git
workflow performs an ordinary fast-forward after a fresh main fetch.

The actual released Kaniko image still carries two blocked roots. Its pinned
build-only CA replacement has real affected/fixed/drift tests and native Go TLS
no-push probes; all pass. A first local harness run used a download destination
that collided with the mounted test directory; correcting that path produced a
passing unchanged trust test. The moving-release refresh still reports affected.
The replacement is a verified official certifi artifact; the old Jupyter
bootstrap CA store (one blocked fingerprint) is explicitly not copied. Original
public base/intermediate layers remain historical inputs, not active final-image
trust stores. Migration from archived Kaniko remains outstanding.

Local YAML parsing and no-publication checks pass. GitLab CI lint POST is denied
HTTP 403 by the existing managed API scope; no broader lease was requested.
The first integrated pipeline [261807](https://gitlab.kwant-project.org/qt/research-docker/-/pipelines/261807)
passed all eight patch contracts, then failed because the bootstrap image lacks
`patch`. The source-contract check now compares the exact unified diff using
Python's standard library; it requires neither `patch` nor Git. All three source
job commands pass inside the exact CI image. The native Kaniko probe also removes
its downloaded public fixture before the subsequent image build. The final
source SHA, remote readback and one-time CI status observation are returned in
the publication receipt, not inferred from local validation.

## Outstanding exceptions

No existing release exception is accepted: solver development snapshot and
remaining backports; build-host Conda resolution, pip build isolation/artifact
locking and TypeScript bootstrap still prevent a bit-identical repeat-build
claim; Inkscape 1.2.2 snapshot compatibility with newer-PPA workflows is untested;
scanner coverage and medium/low findings remain. Yarn still emits the TypeScript
compatibility-patch warning; direct TypeScript compilation and real browser
regressions pass. Browser diagnostics retain the same 24 caught descriptions
and zero console errors as the prior image. The synthetic singleuser driver's
10-second teardown again required SIGKILL, so graceful shutdown is not proven.
No live hosts, admin-notes, deployment pins, credentials or fleet state changed.
