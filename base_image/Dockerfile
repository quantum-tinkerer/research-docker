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
        libgl1-mesa-glx \
   && apt-add-repository -y ppa:inkscape.dev/stable \
   && apt update \
   && apt install -y inkscape \
   && curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash \
   && apt-get install -y git-lfs \
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/*

COPY startup.sh /usr/local/bin/before-notebook.d/

# setting openblas and mkl variables
ENV OPENBLAS_NUM_THREADS=1\
    OMP_NUM_THREADS=1\
    MKL_DYNAMIC=FALSE\
    MKL_NUM_THREADS=1\
    CONDA_ALWAYS_COPY=true

RUN update-alternatives --set editor /bin/nano

RUN conda install --quiet -n base -y conda\>4.8.2 mamba \
    && conda clean --yes --all \
    && conda init --system --no-user \
    && fix-permissions /opt/conda

USER $NB_USER

EXPOSE 22
