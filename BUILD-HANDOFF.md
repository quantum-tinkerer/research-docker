# Independent notebook source candidate (2026-10-31)

Status: build and validation in progress. Not published; not approved for release
or rollout. Historical baseline results are not results for this source rebuild.

Branch: `cleanup/reproducible-security-20261031`.
Public base: `quay.io/jupyter/base-notebook@sha256:49c3267842eb52c9505dba89ebac3adf142afa73feba48d0243da3c9dbdd34d1`
(linux/amd64). No local checkpoint is a Dockerfile input.

The source carries the tested Conda/security/scientific package inventory, modern
OpenVSCode/Node and proxy wrapper, verified JS dependency overlays, nbclassic AMD
backport, independently source-built solver, and JupyterLab setting-registry
backport with fast-uri 3.1.9. It preserves formatter preferences and public IDs.
NSS provider and native-store configuration remain in place.

The OS build now uses Ubuntu snapshot `20261031T000000Z`. Git-LFS and Inkscape
come from that distribution rather than mutable external installer/PPA inputs.
The Inkscape source change is a deliberate compatibility exception needing review.

Public fixture origins and exact-image gates are documented in `tests/README.md`.
Static source-contract, Python compilation, shell syntax and whitespace checks
pass. Runtime/trust/scanner results remain pending until an exact image exists.

Remaining reproducibility limits: solver build-tool and build-host solves;
pip transitive dependencies and build isolation; TypeScript installer metadata;
upstream base artifact retention. The runtime Conda set and Yarn dependency graph
are fixed, but this is not yet a demonstrated bit-identical repeated build.
No inactive-cache finding or editor extension identity is classified as an active
runtime exposure solely from a scanner name match. A new scanner applicability
packet and native embedded-crate inventory are mandatory before release.
