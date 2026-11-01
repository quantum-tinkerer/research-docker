# linux/amd64; public Jupyter Docker Stacks manifest, resolved 2026-10-31.
FROM quay.io/jupyter/base-notebook@sha256:49c3267842eb52c9505dba89ebac3adf142afa73feba48d0243da3c9dbdd34d1 AS solver
USER root
ENV HOME=/root
COPY security/patch_checks.py security/reviewed-inputs.json /build/
COPY security/solver-source.tar.gz /build/source.tar.gz
COPY security/plugin-recipe.yaml /build/recipe/meta.yaml
COPY security/solver-tools-linux-64.lock /build/solver-tools.lock
RUN cd /build && python -c 'from pathlib import Path; from patch_checks import solver_snapshot; solver_snapshot(Path("source.tar.gz").read_bytes())' \
 && mkdir /build/source && tar -xzf /build/source.tar.gz --strip-components=1 -C /build/source \
 && mamba create -y -p /build/tools --file /build/solver-tools.lock \
 && /build/tools/bin/conda build /build/recipe --no-test --output-folder /build/out --override-channels -c conda-forge

FROM quay.io/jupyter/base-notebook@sha256:49c3267842eb52c9505dba89ebac3adf142afa73feba48d0243da3c9dbdd34d1 AS runtime

USER root
WORKDIR /
ENV HOME=/root

# Published Ubuntu snapshot; no mutable PPA or fetched installer script.
RUN sed -i -E 's#https?://(archive.ubuntu.com/ubuntu/?|security.ubuntu.com/ubuntu/?)#https://snapshot.ubuntu.com/ubuntu/20261031T000000Z/#g' /etc/apt/sources.list.d/ubuntu.sources \
 && printf 'Acquire::Check-Valid-Until "false";\n' > /etc/apt/apt.conf.d/99snapshot
RUN apt update \
    && apt full-upgrade -y \
    && apt install -y --no-install-recommends --fix-missing \
        ca-certificates git-lfs inkscape \
        software-properties-common \
        bash-completion \
        cron \
        tree \
        curl \
        tig \
        htop \
        keychain \
        less \
        man \
        nano \
        rsync \
        screen \
        tmux \
        zsh \
        openssh-server \
        apt-transport-https \
        gnupg \
   && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' ca-certificates)" ge 20260816ubuntu0.24.04.1 \
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/* \
   && update-alternatives --set editor /bin/nano

   # OpenBLAS and MKL multithreading does not offer advantages in practice
   ENV OPENBLAS_NUM_THREADS=1\
   OMP_NUM_THREADS=1\
   MKL_DYNAMIC=FALSE\
   MKL_NUM_THREADS=1\
   # Otherwise volumes don't work
   CONDA_ALWAYS_COPY=true\
   # The vscode we're using
   CODE_EXECUTABLE=openvscode-server

# Add environment files. pixi.sh is intentionally not executable: Jupyter's
# hook runner sources it so its PATH update reaches the notebook server.
COPY pixi.sh startup.sh /usr/local/bin/before-notebook.d/
COPY python3.yml /environments/

# User-installed runtimes share the patched distro store; old Pixi is upgraded
# separately by pixi.sh because its old native-store option was ineffective.
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    CONDA_SSL_VERIFY=/etc/ssl/certs/ca-certificates.crt \
    MAMBA_SSL_VERIFY=/etc/ssl/certs/ca-certificates.crt \
    NODE_OPTIONS=--use-openssl-ca \
    DENO_TLS_CA_STORE=system \
    UV_NATIVE_TLS=true \
    UV_SYSTEM_CERTS=true

# Reconstruct the tested environment from published, digest-verified artifacts.
# Bootstrap mamba lives outside the target prefix; no inherited Conda packages remain.
COPY security/ /build/
COPY --from=solver /build/out/noarch/ /build/plugin-artifact/
RUN python /build/prepare-lock.py \
 && cp -a /opt/conda /opt/bootstrap \
 && rm -rf /opt/conda \
 && /opt/bootstrap/bin/mamba create -y -p /opt/conda --file /build/install.lock \
 && rm -rf /opt/bootstrap \
 && python /build/install-assets.py \
 && python /build/dependency-overlay.py \
 && python /build/nbclassic-loader.py \
 && python /build/proxy-compat.py \
 && rm /usr/local/bin/openvscode-server \
 && install -m 0755 /build/openvscode-server /usr/local/bin/openvscode-server \
 && fix-permissions /opt/conda

COPY gitconfig gitattributes gitignore /opt/conda/etc/

# Separately pinned pip-only integrations (not represented by the Conda lock).
COPY requirements-pip.txt /build/
RUN pip install --no-cache-dir --report /build/pip-report.json -r /build/requirements-pip.txt

# The distro NSS provider is now fixed. Do not replace libnssckbi.so:
# native PKCS#11/chain regressions in tests/ remain mandatory (PATCHES.md).

# jupyter-sshd-proxy starts its own sshd with "-f none", so it does not read
# the global sshd_config.d drop-in below unless the option is set explicitly.
RUN sed -i "/PrintLastLog no/a\\        '-o', 'PermitUserEnvironment yes'," \
        /opt/conda/lib/python*/site-packages/jupyter_sshd_proxy/__init__.py \
    && /opt/conda/bin/python -m py_compile \
        /opt/conda/lib/python*/site-packages/jupyter_sshd_proxy/__init__.py

# Allow SSH sessions to read per-user environment files
RUN mkdir -p /etc/ssh/sshd_config.d \
    && printf 'PermitUserEnvironment yes\n' > /etc/ssh/sshd_config.d/50-permit-user-env.conf

# Switch back to jovyan to avoid accidental container runs as root
ENV HOME=/home/jovyan CHOWN_HOME=yes
USER $NB_UID
RUN printf '\n\n\
c.ServerApp.ResourceUseDisplay.mem_limit = 21474836480\n\
c.ServerApp.ResourceUseDisplay.track_cpu_percent = True\n\
c.ServerApp.ResourceUseDisplay.cpu_limit = 5\n\
c.ContextManager.root_dir = "~"\n' >> /etc/jupyter/jupyter_notebook_config.py
# Add the manual jupyter lab config file
COPY jupyter_server_config.json /etc/jupyter/jupyter_server_config.json

EXPOSE 22

FROM runtime AS frontend
USER root
ENV HOME=/root NODE_OPTIONS="--use-openssl-ca --max-old-space-size=6144" RAYON_NUM_THREADS=4
WORKDIR /build
RUN python /build/build-assets.py

FROM runtime
USER root
RUN rm -rf /opt/conda/lib/python3.13/site-packages/jupyterlab/static /opt/conda/share/jupyter/lab/static
COPY --from=frontend /build/app/build/ /opt/conda/lib/python3.13/site-packages/jupyterlab/static/
COPY --from=frontend /build/app/build/ /opt/conda/share/jupyter/lab/static/
COPY --from=frontend /build/asset-receipt.json /usr/local/share/research-base/formatter-asset-receipt.json
COPY --from=frontend /build/app/yarn.lock /usr/local/share/research-base/formatter-yarn.lock
COPY --from=frontend /build/app/package.json /usr/local/share/research-base/formatter-package.json
COPY --from=frontend /build/typescript/package-lock.json /usr/local/share/research-base/formatter-typescript-lock.json
ENV HOME=/home/jovyan
USER 1000

# pip 26.2.2 fixes trust, but still vendors older urllib3/msgpack releases.
# Preserve pip's namespace and pure-Python msgpack implementation.
USER root
COPY pip-security.py pip-security.json /build/
RUN python /build/pip-security.py
USER 1000
