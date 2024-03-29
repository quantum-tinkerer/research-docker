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
        gfortran \
        tig \
        htop \
        imagemagick \
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
   && curl -s https://syncthing.net/release-key.txt | apt-key add - \
   && echo "deb https://apt.syncthing.net/ syncthing stable" > \
        /etc/apt/sources.list.d/syncthing.list \
   && apt-add-repository -y ppa:inkscape.dev/stable \
   && apt update \
   && apt install -y syncthing inkscape \
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/*

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

RUN chmod a+x /usr/local/bin/startup.sh \
    && update-alternatives --set editor /bin/nano \
    # https://docs.syncthing.net/users/faq.html#how-do-i-increase-the-inotify-limit-to-get-my-filesystem-watcher-to-work
    && echo "fs.inotify.max_user_watches=204800" >> /etc/sysctl.conf

RUN conda install --quiet -n base -y conda\>4.8.2 mamba \
    && conda clean --yes --all \
    && conda init --system --no-user \
    && fix-permissions /opt/conda

USER $NB_USER
# Allow running image in CI with user mismatch, see
# e.g. https://github.com/actions/checkout/issues/760
# and https://gitlab.com/gitlab-org/gitlab-runner/-/issues/2750
RUN git config --global --add safe.directory '*'

CMD ["startup.sh"]
EXPOSE 22
