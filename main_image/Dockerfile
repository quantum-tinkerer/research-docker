FROM gitlab.kwant-project.org:5005/qt/research-docker:base
ARG GITLAB_API_TOKEN
ARG CI_PIPELINE_ID

USER root
WORKDIR /

# Add environment files
RUN mkdir /environments
COPY python3.yml dev.yml fenics.yml install_dev.sh /environments/

# Update the root environment
# We install python beforehand, otherwise the post-update scripts break :(
RUN mamba install -y -n base python=3.9* \
    && mamba env update --quiet -n base -f /environments/python3.yml \
    && mamba clean --quiet --yes --all \
    && fix-permissions /opt/conda

# Add a dev environment (e.g. with dev kwant and holoviews)
# RUN conda env create -p /opt/conda/envs/dev -f /environments/dev.yml

# Enable `jupyter nbextension`s
#RUN jupyter labextension install --no-build \
#            # FIXME https://github.com/jupyterlab/jupyterlab-latex/issues/154
#            # @jupyterlab/latex \
#    && jupyter lab build \
#    && fix-permissions /opt/conda

# Figure out the future Singularity image address
COPY resolve_singularity.py /usr/local/bin/resolve_singularity.py
RUN /opt/conda/bin/python /usr/local/bin/resolve_singularity.py \
    && rm /usr/local/bin/resolve_singularity.py

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID
RUN printf '\n\n\
c.ServerApp.ResourceUseDisplay.mem_limit = 21474836480\n\
c.ServerApp.ResourceUseDisplay.track_cpu_percent = True\n\
c.ServerApp.ResourceUseDisplay.cpu_limit = 5\n\
c.ContextManager.root_dir = "~"\n' >> /etc/jupyter/jupyter_notebook_config.py

# Create parallel profiles and copy the correct config
RUN ipython profile create --parallel --profile python3 --ipython-dir /opt/conda/etc/ipython
COPY ipcluster_config_python3.py /opt/conda/etc/ipython/profile_python3/ipcluster_config.py
