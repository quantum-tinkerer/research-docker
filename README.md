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

The container starts an `sshd` daemon during boot so users can connect over SSH. `PermitUserEnvironment` is enabled for the daemon, and every time the notebook server starts, all environment variables whose name contains `JUPYTER` are collected and written to `~/.ssh/environment`. Because OpenSSH reads this file for each login, every SSH session (interactive shells and remote commands) inherits the same Hub context available inside JupyterLab while keeping the configuration user-owned and editable.

The image also includes `jupyter-sshd-proxy` for SSH over the authenticated JupyterHub HTTPS/WebSocket route. Its on-demand `sshd` is patched during the image build to read `~/.ssh/environment`, matching the behavior of the daemonized SSH server.
