FROM jupyter/base-notebook:latest
Maintainer Joseph Weston <j.b.weston@tudelft.nl>

USER root
WORKDIR /

# Debian packages
RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing \
        autossh\
        bash-completion\
        build-essential\
        cron\
        curl\
        dvipng\
        gfortran\
        git\
        htop\
        imagemagick\
        inkscape\
        keychain\
        latexmk\
        less\
        man\
        nano\
        rsync\
        screen\
        texlive-bibtex-extra\
        texlive-extra-utils\
        texlive-fonts-extra\
        texlive-fonts-recommended\
        texlive-generic-recommended\
        texlive-latex-base\
        texlive-latex-extra\
        texlive-latex-recommended\
        texlive-publishers\
        texlive-science\
        texlive-xetex\
        texlive-lang-cyrillic\
        cm-super  # extra font\
        vim\
        zsh\
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/*

# Install supervisor for automatic starting of syncthing
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Add global bash profile
COPY profile.sh /etc/profile.d/

# Set the conda environment folder in the home folder
RUN conda config --system --add envs_dirs ~/.conda/envs

# Add environment files
RUN mkdir /environments
COPY python3.yml dev.yml /environments/

# Update the root environment
RUN conda env update -n root -f /environments/python3.yml

# Add a dev environment (e.g. with dev kwant and holoviews)
RUN conda env create -p /opt/conda/envs/dev -f /environments/dev.yml

# Cleanup all downloaded conda files
RUN conda clean --yes --all

# Enable jupyter nbextension-s
RUN jupyter nbextension enable --py --sys-prefix ipyparallel &&\
    jupyter nbextension enable --py --sys-prefix jupyter_cms &&\
    jupyter nbextension enable --py --sys-prefix jupyter_dashboards

# prevent nb_conda_kernels from overriding our custom kernel manager
RUN rm /opt/conda/etc/jupyter/jupyter_notebook_config.json

# Add notebook config
COPY jupyter_notebook_config.py /opt/conda/etc/jupyter
# Register nbdime as a git diff and merge tool
COPY git* /etc/

# Create parallel profiles and copy the correct config
RUN ipython profile create --parallel --profile python3 --ipython-dir /opt/conda/etc/ipython
RUN ipython profile create --parallel --profile dev --ipython-dir /opt/conda/etc/ipython
COPY ipcluster_config_python3.py /opt/conda/etc/ipython/profile_python3/ipcluster_config.py
COPY ipcluster_config_dev.py /opt/conda/etc/ipython/profile_dev/ipcluster_config.py

# setting openblas and mkl variables
ENV OPENBLAS_NUM_THREADS=1\
    OMP_NUM_THREADS=1\
    MKL_DYNAMIC=FALSE\
    MKL_NUM_THREADS=1\
    CONDA_ALWAYS_COPY=true

# copy startup.sh script and set start-up command
COPY startup.sh /srv/singleuser/
CMD ["sh", "/srv/singleuser/startup.sh"]
EXPOSE 22
