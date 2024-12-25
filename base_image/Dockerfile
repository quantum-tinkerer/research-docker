FROM jupyter/base-notebook:latest

USER root
WORKDIR /

# Debian packages
RUN apt update \
    && apt full-upgrade -y \
    && apt install -y --no-install-recommends --fix-missing \
        software-properties-common \
        autossh \
        bash-completion \
        build-essential \
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
        vim \
        zsh \
        openssh-server \
        apt-transport-https \
        supervisor \
        gnupg \
        libgl1-mesa-glx \
   && apt-add-repository -y ppa:inkscape.dev/stable \
   && apt update \
   && apt install -y inkscape \
   && curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash \
   && apt-get install -y git-lfs \
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/*

# copy startup.sh script and set start-up command
COPY startup.sh /usr/local/bin/

# setting openblas and mkl variables
ENV OPENBLAS_NUM_THREADS=1\
    OMP_NUM_THREADS=1\
    MKL_DYNAMIC=FALSE\
    MKL_NUM_THREADS=1\
    CONDA_ALWAYS_COPY=true

RUN chmod a+x /usr/local/bin/startup.sh \
    && update-alternatives --set editor /bin/nano \

RUN conda install --quiet -n base -y conda\>4.8.2 mamba \
    && conda clean --yes --all \
    && conda init --system --no-user \
    && fix-permissions /opt/conda

USER $NB_USER

CMD ["startup.sh"]
EXPOSE 22
