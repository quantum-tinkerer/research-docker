FROM jupyter/base-notebook:latest
ARG GITLAB_API_TOKEN
ARG CI_PIPELINE_ID

USER root
WORKDIR /

# setting openblas and mkl variables
ENV OPENBLAS_NUM_THREADS=1\
    OMP_NUM_THREADS=1\
    MKL_DYNAMIC=FALSE\
    MKL_NUM_THREADS=1\
    CONDA_ALWAYS_COPY=true

# Debian packages
RUN apt-get update \
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

# Install supervisor for automatic starting of syncthing
COPY supervisord.conf /etc/supervisor/supervisord.conf

# copy startup.sh script
COPY startup.sh /usr/local/bin/
RUN chmod a+x /usr/local/bin/startup.sh \
    && update-alternatives --set editor /bin/nano \
    # https://docs.syncthing.net/users/faq.html#how-do-i-increase-the-inotify-limit-to-get-my-filesystem-watcher-to-work
    && echo "fs.inotify.max_user_watches=204800" >> /etc/sysctl.conf
CMD ["/usr/local/bin/startup.sh"]

RUN conda install --quiet -n base -y conda\>4.8.2 mamba \
    && conda install --quiet -n base -y \
        git \
        nbdime \
        nbstripout \
        ffmpeg \
        pandoc \
    && conda clean --yes --all \
    && conda init --system --no-user \
    && fix-permissions /opt/conda

# Add environment files
COPY environments/ /environments/

# Update the root environment
# We install python beforehand, otherwise the post-update scripts break :(
RUN mamba install -y -n base python=3.8* \
    && mamba env update --quiet -n base -f /environments/python3.yml \
    && mamba clean --quiet --yes --all \
    && fix-permissions /opt/conda

# Add a dev environment (e.g. with dev kwant and holoviews)
# RUN conda env create -p /opt/conda/envs/dev -f /environments/dev.yml

# Enable `jupyter nbextension`s
RUN jupyter nbextension enable --py --sys-prefix ipyparallel \
    && jupyter serverextension enable --sys-prefix jupyter_server_proxy \
    && jupyter serverextension enable --py --sys-prefix jupyterlab_code_formatter \
    && jupyter serverextension enable --py --sys-prefix jupyter_lsp \
    && jupyter serverextension enable --py --sys-prefix jupyterlab_git \
    && jupyter serverextension enable --sys-prefix nbgitpuller \
    && jupyter serverextension enable --py --sys-prefix dask_labextension \
    && jupyter labextension install --no-build \
            @jupyter-widgets/jupyterlab-manager \
            # FIXME https://github.com/jupyterlab/jupyterlab-latex/issues/135
            # @jupyterlab/latex \
            @bokeh/jupyter_bokeh \
            @pyviz/jupyterlab_pyviz \
            # @ryantam626/jupyterlab_code_formatter \
            @jupyterlab/git \
            @jupyterlab/toc \
            @jupyterlab/server-proxy \
            @aquirdturtle/collapsible_headings \
            @krassowski/jupyterlab-lsp \
            dask-labextension \
            jupyterlab-plotly \
            plotlywidget \
            jupyterlab-topbar-extension\
            jupyterlab-system-monitor\
            jupyter-matplotlib\
    && jupyter lab build \
    && fix-permissions /opt/conda

# Figure out the future Singularity image address
COPY resolve_singularity.py /usr/local/bin/resolve_singularity.py
RUN /opt/conda/bin/python /usr/local/bin/resolve_singularity.py \
    && rm /usr/local/bin/resolve_singularity.py

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID
RUN printf '\n\n\
c.NotebookApp.ResourceUseDisplay.mem_limit = 21474836480\n\
c.NotebookApp.ResourceUseDisplay.track_cpu_percent = True\n\
c.NotebookApp.ResourceUseDisplay.cpu_limit = 5\n\
c.ContextManager.root_dir = "~"\n' >> /etc/jupyter/jupyter_notebook_config.py

# Create parallel profiles and copy the correct config
RUN ipython profile create --parallel --profile python3 --ipython-dir /opt/conda/etc/ipython
COPY ipcluster_config.py /opt/conda/etc/ipython/profile_python3/ipcluster_config.py
COPY gitconfig gitattributes /opt/conda/etc/

EXPOSE 22