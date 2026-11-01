# Downstream fixes and their removal gates

These are build/candidate checks, never startup or recovery network requests.
Run `python3 tests/upstream-refresh.py --output <empty-evidence-directory>` from
the repository root to inspect current **released artifacts**, even while build
pins remain unchanged. It verifies archive digests, reads actual package/source
bytes and executes nbclassic's shipped library and the editor's native Node.
Unknown release/API changes fail REVIEW; known incorporated fixes fail RETIRE.
After either failure, review/update or remove the specifically named source and
rerun the retained regression/build checks. A later release number alone does
not prove that a bundled library, optimized AMD module or trust store is fixed.

`patch_checks.py` contains the small source-specific decisions; `reviewed-inputs.json`
records the reviewed affected bytes. The refresh needs Python with `packaging`,
Node and `zstd`; the separate CI refresh also needs rootless Podman. These checks run before replacement. They
must not be updated just to make a build green. `tests/test_patch_checks.py` covers
affected, incorporated and unsupported states. The live refresh exercises the
actual released artifacts, and the image build runs the same checks on its inputs.

## Solver development snapshot

Reason: released conda-rattler-solver 0.2.0 excludes py-rattler 0.28.1, whose native
zip/PyO3/quinn fixes are needed. Source: [official solver](https://github.com/conda/conda-rattler-solver),
commit `50108b638eed81ab9b0029812360d58dcfae7c0b` and its published
[0.2.0 metadata](https://pypi.org/project/conda-rattler-solver/0.2.0/).
The build verifies the snapshot before building; refresh reads dependency metadata
from the hash-verified latest wheel, not just the index's version field.

Remove the solver stage, `plugin-recipe.yaml`, `solver-source.tar.gz`, bootstrap
lock and `prepare-lock.py` local-package entry when a compatible official Conda
release is available. Pin that released artifact instead. RETIRE is raised when
the released solver admits the required py-rattler. Keep `solver-probe.py` (both
solvers) and native rattler crate inventory; compatibility metadata alone is not
a successful solve or proof of the native zip version.

## JupyterLab settings registry and fast-uri

Reason: strict URI parsing rejects the original opaque
`jupyterlab_code_formatter:settings` ID. The patch affects internal schema keys;
it must not rename public IDs, `$id`/`$ref` values or user preferences.
Sources: [JupyterLab registry](https://github.com/jupyterlab/jupyterlab/blob/v4.6.5/packages/settingregistry/src/settingregistry.ts),
[fast-uri](https://github.com/fastify/fast-uri). No upstream fix/issue is claimed
where one has not been established.

Before patching, `build-assets.py` executes the shipped compiled validator against
the original ID, repeated lookup, defaults, type errors and strict malformed
URIs. Passing behavior raises RETIRE; otherwise only the reviewed source is
accepted. Remove `settingregistry.patch`, original/patched source replacement
and corresponding build steps when upstream provides that behavior. Keep
`schema-tests.js` and full browser preference/formatting checks. The regression
suite deliberately does not depend on our private `_schemaKey` method.

The fast-uri resolution has a separate gate: the upstream staging lock containing
3.1.9 raises RETIRE for that override; unsupported graphs raise REVIEW. Regenerate
the frontend lock after removing the override. Current latest fast-uri 4.x is
outside the reviewed Ajv `^3` contract and does not by itself retire anything.

## Editor and npm substitutions

Sources: [OpenVSCode releases](https://github.com/gitpod-io/openvscode-server/releases),
[Node releases](https://nodejs.org/en/about/previous-releases), and official npm
package artifacts in `upstream.json` / `dependency-releases.json`.
Reasons: shipped Node 22.21.1 and bundled shell-quote, SOCKS/ip-address, lodash-es,
picomatch and Undici need compatible maintenance updates. npm's Undici is checked
separately from the editor's. Consumer constraints remain checked after overlays.

The archive digest binds the editor input; its actual Node version, ABI and
bundled roots are inspected. A compatible fixed shipped Node raises RETIRE for
that replacement, followed by both native TLS modes and real VSIX tests. Unknown
ABI/source changes raise REVIEW. The global npm replacement compares actual
JS/package trees to the official fixed archive and to the reviewed Conda package
bytes, alongside the running CLI version. Refresh independently downloads the
latest compatible Conda Node 22 release to discover an incorporated npm update.

Each dependency overlay compares actual JS/package-file digests with the reviewed
old bytes and fixed official release bytes. Already-fixed code raises RETIRE for
that individual substitution, never a silent overwrite. Remove its update entry
and unused release lock record; keep `dependency-probe.js`, native Node trust and
browser/editor/VSIX gates. Future unfamiliar packages require code review, even
when package.json advertises a plausible version.

## nbclassic AMD backport

Sources: [nbclassic](https://github.com/jupyter/nbclassic),
[Underscore 1.13.8](https://github.com/jashkenas/underscore/releases/tag/1.13.8).
Reason: replacing a standalone library leaves old optimized AMD definitions active.
`nbclassic-check.cjs` executes the shipped standalone deep flatten/equality cases
and checks which optimized bundles contain those exact executable bytes. The
whole reviewed JS/template tree must match before applying the fix.

A fixed component raises RETIRE for its substitution; fixed optimized bundles
raise RETIRE for `nbclassic-loader.py`. Partial retirement is reported explicitly.
Remove only the obsolete portion, then rerun the real browser RequireJS resolution
and deep regressions. Keep those tests after the loader adapter is gone.

## pip vendored urllib3/msgpack

Sources: [pip vendoring](https://github.com/pypa/pip/tree/26.2.2/src/pip/_vendor),
[urllib3](https://github.com/urllib3/urllib3/releases/tag/2.8.0),
[msgpack](https://github.com/msgpack/msgpack-python/releases/tag/v1.2.4).
Reason: pip 26.2.2 fixes its CA store but still vendors older library code. The
backport retains pip's namespace and pure-Python msgpack implementation.

Before mutation, `pip-security.py` checks actual Python source trees. Already-fixed
vendored bytes raise RETIRE for the relevant substitution; unknown source changes
raise REVIEW. Remove that entry and unused downloaded artifact record, preserving
`pip-vendor-probe.py`: real vendor imports, CacheControl round-trip, pip index
access and positive/negative native TLS. Do not classify pip's old BOM as runtime
code without checking actual imports. The existing applicability record remains.

## NSS replacement — retired 2026-11-01

The locked environment contains no Conda NSS package. The actual unmodified
Ubuntu snapshot `libnss3` package's provider has zero blocked fingerprints and
passes all 12 offline chains, both live badchains and PyPI through native NSS.
The blanket `libnssckbi.so` symlink replacement and explicit p11-kit provider
installation are therefore removed. Evidence: integration validation packet.
Keep `pkcs11-ca-probe.py`, `nss-probe.py` and `runtime-probe.py`; a future dirty
provider must fail these gates and receive review, not silently restore the hook.

## Deliberately retained application behavior and trust policy

The IPv4 editor launcher, working-folder proxy integration, SSH environment option
and home ownership are application/configuration behavior, not temporary incident
library patches. Their real launcher, VSIX, startup and ownership tests remain;
no artificial version-based retirement hook is added. Existing source-shape
assertions protect proxy edits against unsupported drift.

CA version floors, shared system-store environment settings and the persistent
Pixi minimum protect user-installed runtimes too. Clean shipped Node/Python roots
do not establish cleanliness of arbitrary persistent user installations. These
are explicit trust/bootstrap policy, not grounds to silently remove configuration.
The refresh inspects actual released pip/certifi bundles; final native store,
Node, NSS and persistent-user Pixi regressions remain required. No upstream query
is added to startup/recovery.

## CI Kaniko CA bootstrap

The original main job published `combined:main` on every source push. Source
integration now runs only tests and `--no-push --no-push-cache` builds. Project
Auto DevOps is disabled and no push webhooks are configured; the remaining
Mattermost integration is a push notification, not deployment.

[Google's archived Kaniko](https://github.com/GoogleContainerTools/kaniko) debug
artifact `sha256:9e22d0ba2c78cffbd47e2269aa6d3dc43fc3e3ecc6b61262399279dec5e67d45`
still contains two blocked roots. `tests/ci/kaniko-ca.sh` accepts only its reviewed
bundle, errors on clean upstream with the exact script/CI wiring to retire, and
errors on unknown affected bytes. The replacement is the hash-verified published
certifi 2026.10.23 store, checked against all 20 fingerprints. The older public
Jupyter bootstrap store itself contains one blocked root, so it must not be
copied as the replacement. No host CA store or credential is used.

Run `sh tests/ci/upstream-refresh.sh` to inspect the moving official released
image independently of the CI pin. Retire the script, CA artifact preparation
and CI copy when that actual store is clean and native TLS/build regressions
pass. Keep `kaniko-native.test.sh` after retirement. `kaniko-ca.test.sh` checks
actual affected, replaced and deliberately changed stores before each CI build.
Migration from archived Kaniko to a maintained builder remains outstanding;
a different publisher requires build/native trust review, not an automatic swap.
