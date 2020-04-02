# Single user Docker image for Jupyterhub

* Official repo on [kwant-gitlab/qt/research-docker](https://gitlab.kwant-project.org/qt/research-docker)
* GitHub mirror on [github.com/quantum-tinkerer/research-docker](https://github.com/quantum-tinkerer/research-docker)
* Built automatically in Gitlab CI using Kaniko

To use it, follow the instructions of [Jupyter Docker Stacks](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/common.html#startup-hooks), for example:

```bash
docker run -d -p 8888:8888 gitlab.kwant-project.org:5005/qt/research-docker start-notebook.sh --NotebookApp.password='sha1:74ba40f8a388:c913541b7ee99d15d5ed31d4226bf7838f83a50e'
```
