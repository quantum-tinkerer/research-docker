FROM quay.io/jupyter/base-notebook:ubuntu-24.04

USER root
WORKDIR /

# Debian packages
RUN apt update \
    && apt full-upgrade -y \
    && apt install -y --no-install-recommends --fix-missing \
        ca-certificates p11-kit-modules \
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
   && apt-add-repository -y ppa:inkscape.dev/stable \
   && apt update \
   && apt install -y inkscape \
   && curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash \
   && apt-get install -y git-lfs \
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
COPY gitconfig gitattributes gitignore /opt/conda/etc/

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

# Update the base environment
RUN mamba env update -n base -f /environments/python3.yml \
    && mamba clean --quiet --yes --all \
    && fix-permissions /opt/conda

# Conda NSS does not yet ship the upstream trust fix. Use the distro's documented
# p11-kit root provider, leaving the NSS cryptographic engine unchanged.
RUN nss_provider=$(dpkg-query -L p11-kit-modules | sed -n '/\/p11-kit-trust\.so$/p') \
    && test -f "$nss_provider" \
    && find /opt/conda /usr/lib -name libnssckbi.so -exec ln -sf "$nss_provider" {} \;

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
USER $NB_UID
RUN printf '\n\n\
c.ServerApp.ResourceUseDisplay.mem_limit = 21474836480\n\
c.ServerApp.ResourceUseDisplay.track_cpu_percent = True\n\
c.ServerApp.ResourceUseDisplay.cpu_limit = 5\n\
c.ContextManager.root_dir = "~"\n' >> /etc/jupyter/jupyter_notebook_config.py
# Add the manual jupyter lab config file
COPY jupyter_server_config.json /etc/jupyter/jupyter_server_config.json

EXPOSE 22
