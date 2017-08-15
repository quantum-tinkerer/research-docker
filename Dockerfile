FROM jupyter/base-notebook:latest
Maintainer Joseph Weston <j.b.weston@tudelft.nl>

USER root
WORKDIR /

COPY setup_user.sh startup.sh /srv/singleuser/
RUN sh /srv/singleuser/setup_user.sh
RUN mkdir /var/run/sshd /environments && \
    chown {{jupyterhub_notebook_user}} /environments

# Debian packages
RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing \
        {% for package in jupyter_apt_packages %}
        {{package}} \
        {% endfor %}
        openssh-server \
        apt-transport-https \
        supervisor \
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/*

# Syncthing installation
RUN curl -s https://syncthing.net/release-key.txt | apt-key add - && \
    echo "deb https://apt.syncthing.net/ syncthing stable" | tee /etc/apt/sources.list.d/syncthing.list && \
    apt-get update && apt-get install -y syncthing syncthing-inotify && apt-get clean

# Install supervisor for automatic starting of syncthing
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Add global bash profile
COPY profile.sh /etc/profile.d/

# Set the conda environment folder in the home folder
RUN conda config --system --add envs_dirs ~/.conda/envs

# Add environment files
COPY python2.yml python3.yml dev.yml /environments/

# Update the root environment
RUN conda env update -n root -f /environments/python3.yml

# Add a dev environment (e.g. with dev kwant and holoviews)
RUN conda env create -p /opt/conda/envs/dev -f /environments/dev.yml

# Cleanup all downloaded conda files
RUN conda clean --yes --all

{% for extension in jupyter_nbextensions %}
RUN jupyter nbextension enable --py --sys-prefix {{extension}}
{% endfor %}

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
COPY ipcluster_config_python3.py /opt/conda/etc/ipython/profile_dev/ipcluster_config.py

# setting openblas and mkl variables
ENV OPENBLAS_NUM_THREADS=1\
    OMP_NUM_THREADS=1\
    MKL_DYNAMIC=FALSE\
    MKL_NUM_THREADS=1\
    CONDA_ALWAYS_COPY=true

CMD ["sh", "/srv/singleuser/startup.sh"]
EXPOSE 22
