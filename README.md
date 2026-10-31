# Single user Docker image for Jupyterhub

* Official repo on [kwant-gitlab/qt/research-docker](https://gitlab.kwant-project.org/qt/research-docker)
* GitHub mirror on [github.com/quantum-tinkerer/research-docker](https://github.com/quantum-tinkerer/research-docker)
* Built automatically in Gitlab CI using Kaniko

To use it, follow the instructions of [Jupyter Docker Stacks](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/common.html#startup-hooks), for example:

```bash
docker run -d -p 8888:8888 gitlab.kwant-project.org:5005/qt/research-docker start-notebook.sh --NotebookApp.password='sha1:74ba40f8a388:c913541b7ee99d15d5ed31d4226bf7838f83a50e'
```

To test create a link `ln -s /usr/share/testing.ipynb testing.ipynb` in the home folder and run the testing notebook.

To add a new feature to test, dump it into the testing notebook.

## SSH sessions and Hub variables

The container starts an `sshd` daemon during boot so users can connect over SSH. `PermitUserEnvironment` is enabled for the daemon, and every time the notebook server starts, the Pixi environment and all variables whose name contains `JUPYTER` are collected and written to `~/.ssh/environment`. Because OpenSSH reads this file for each login, every SSH session (interactive shells and remote commands) inherits the same Hub context and Pixi executable available inside JupyterLab while keeping the configuration user-owned and editable.

The image also includes `jupyter-sshd-proxy` for SSH over the authenticated JupyterHub HTTPS/WebSocket route. Its on-demand `sshd` is patched during the image build to read `~/.ssh/environment`, matching the behavior of the daemonized SSH server.

## Pixi updates

On first startup, the hook installs the SHA256-verified official Pixi 0.82.1 archive as the notebook user. Persistent installations older than 0.82.1 are upgraded; current or newer user-selected versions are retained. The user-owned executable takes precedence in Jupyter and SSH sessions. Home ownership is established by the upstream startup script through `CHOWN_HOME=yes` (not a recursive ownership change).

## Independent source build candidate

The Dockerfile uses a public Jupyter base pinned by its linux/amd64 registry
manifest. It does not depend on any fleet checkpoint or host-local image ID.
`image/security/conda-linux-64.lock` fixes the 376 published Conda artifacts;
the 377th package, conda-rattler-solver, is rebuilt from the verified upstream
source archive. `python3.yml` documents intent, rather than resolving the build.
The editor archive and dependency overlays retain upstream integrity hashes.
The JupyterLab source backport and immutable Yarn lock preserve the original
formatter plugin ID, preferences filename, and schema identifiers.

Run `tests/build-local.sh` for the bounded rootless Podman build and exact-image
regression gates. It permits at most four CPUs and 8 GiB RAM, checks host
headroom, and writes receipts under ignored `build-evidence/`. Tests use fresh
synthetic homes, a fake Hub, public certificate chains, and an offline test VSIX.
No existing user home, fleet container, or runtime checkpoint is an input.

This is a candidate, not publication or deployment approval. See
[BUILD-HANDOFF.md](BUILD-HANDOFF.md) for measured results and remaining limits.
