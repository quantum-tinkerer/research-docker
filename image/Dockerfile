FROM quay.io/jupyter/base-notebook:ubuntu-24.04

USER root
WORKDIR /

# Debian packages
RUN apt update \
    && apt full-upgrade -y \
    && apt install -y --no-install-recommends --fix-missing \
        software-properties-common \
        bash-completion \
        cron \
        tree \
        curl \
        dvipng \
        tig \
        htop \
        imagemagick \
        keychain \
        latexmk \
        latexdiff \
        less \
        man \
        nano \
        rsync \
        screen \
        tmux \
        # LaTeX packages
        biber \
        texlive-bibtex-extra \
        texlive-extra-utils \
        texlive-fonts-extra \
        texlive-fonts-recommended \
        texlive-latex-base \
        texlive-latex-extra \
        texlive-latex-recommended \
        texlive-plain-generic \
        texlive-publishers \
        texlive-science \
        texlive-xetex \
        texlive-lang-cyrillic \
        texlive-lang-european \
        lmodern \
        cm-super \
        zsh \
        openssh-server \
        apt-transport-https \
        gnupg \
   && curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash \
   && apt-get install -y git-lfs \
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/* \
   && update-alternatives --set editor /bin/nano


   # OpenBLAS and MKL multithreading does not offer advantages in practice
   ENV OPENBLAS_NUM_THREADS=1 \
   OMP_NUM_THREADS=1 \
   MKL_DYNAMIC=FALSE \
   MKL_NUM_THREADS=1 \
   # Otherwise volumes don't work
   CONDA_ALWAYS_COPY=true \
   # The vscode we're using
   CODE_EXECUTABLE=openvscode-server

# Add environment files
COPY startup.sh /usr/local/bin/before-notebook.d/
COPY python3.yml /environments/
COPY gitconfig gitattributes gitignore /opt/conda/etc/

RUN cat /opt/conda/etc/gitconfig
# Update the base environment
RUN mamba env update -n base -f /environments/python3.yml \
    && mamba clean --quiet --yes --all \
    && fix-permissions /opt/conda
RUN echo "AFTER MAMBA:" && cat /opt/conda/etc/gitconfig

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID
RUN printf '\n\n\
c.ServerApp.ResourceUseDisplay.mem_limit = 21474836480\n\
c.ServerApp.ResourceUseDisplay.track_cpu_percent = True\n\
c.ServerApp.ResourceUseDisplay.cpu_limit = 5\n\
c.ContextManager.root_dir = "~"\n' >> /etc/jupyter/jupyter_notebook_config.py
# Add the manual jupyter lab config file
COPY jupyter_server_config.json /etc/jupyter/jupyter_server_config.json

