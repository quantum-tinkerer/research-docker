FROM jupyter/base-notebook:latest

USER root
WORKDIR /

# Debian packages
RUN apt-get update \
    && apt-get full-upgrade -y \
    && apt-get install -y --no-install-recommends --fix-missing \
        autossh \
        bash-completion \
        build-essential \
        cron \
        tree \
        curl \
        dvipng \
        gfortran \
        tig \
        htop \
        imagemagick \
        inkscape \
        jq \
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
        texlive-generic-recommended \
        texlive-latex-base \
        texlive-latex-extra \
        texlive-latex-recommended \
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
   && curl -s https://syncthing.net/release-key.txt | apt-key add - \
   && echo "deb https://apt.syncthing.net/ syncthing stable" > \
        /etc/apt/sources.list.d/syncthing.list \
   && apt-get update \
   && apt-get install -y syncthing \
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/*

RUN conda update -y -n base --all \
    && conda install -n base -y \
        git \
        nbdime \
        nbstripout \
        ffmpeg \
        pandoc \
    && conda clean --yes --all \
    && conda init --system --no-user \
    && fix-permissions /opt/conda

RUN update-alternatives --set editor /bin/nano
# https://docs.syncthing.net/users/faq.html#how-do-i-increase-the-inotify-limit-to-get-my-filesystem-watcher-to-work
RUN echo "fs.inotify.max_user_watches=204800" | sudo tee -a /etc/sysctl.conf
# Install supervisor for automatic starting of syncthing
COPY supervisord.conf /etc/supervisor/supervisord.conf
# copy startup.sh script and set start-up command
COPY startup.sh /usr/local/bin/

# setting openblas and mkl variables
ENV OPENBLAS_NUM_THREADS=1\
    OMP_NUM_THREADS=1\
    MKL_DYNAMIC=FALSE\
    MKL_NUM_THREADS=1\
    CONDA_ALWAYS_COPY=true

CMD ["startup.sh"]
EXPOSE 22

USER $NB_USER
COPY gitconfig gitattributes /opt/conda/etc/
