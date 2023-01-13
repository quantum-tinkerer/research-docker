FROM gitlab.kwant-project.org:5005/qt/research-docker:base
ARG JOBS_URL

USER root
WORKDIR /

# Add environment files
COPY python3.yml dev.yml fenics.yml install_dev.sh /environments/

# Update the root environment
RUN rm "${CONDA_DIR}/conda-meta/pinned" \
    && mamba install -n base -y python=3.10* \
    && mamba env update --quiet -n base -f /environments/python3.yml \
    && mamba clean --quiet --yes --all \
    && mamba list python | grep '^python ' | tr -s ' ' | cut -d ' ' -f 1,2 >> "${CONDA_DIR}/conda-meta/pinned" \
    && fix-permissions /opt/conda

# Add a dev environment (e.g. with dev kwant and holoviews)
# RUN conda env create -p /opt/conda/envs/dev -f /environments/dev.yml

# Figure out the future Singularity image address
COPY resolve_singularity.py .gitlab-ci.yml /usr/local/bin/
RUN /opt/conda/bin/python /usr/local/bin/resolve_singularity.py \
    && rm /usr/local/bin/resolve_singularity.py /usr/local/bin/.gitlab-ci.yml \
    && export SINGULARITY_URL=$(cat /etc/singularity_url)

COPY gitconfig gitattributes gitignore /opt/conda/etc/

# Create parallel profiles and copy the correct config
RUN mkdir -p /opt/conda/etc/ipython && ipython profile create --parallel --profile python3 --ipython-dir /opt/conda/etc/ipython
COPY ipcluster_config_python3.py /opt/conda/etc/ipython/profile_python3/ipcluster_config.py

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID
RUN printf '\n\n\
c.ServerApp.ResourceUseDisplay.mem_limit = 21474836480\n\
c.ServerApp.ResourceUseDisplay.track_cpu_percent = True\n\
c.ServerApp.ResourceUseDisplay.cpu_limit = 5\n\
c.ContextManager.root_dir = "~"\n' >> /etc/jupyter/jupyter_notebook_config.py
# Add the manual jupyter lab config file
COPY jupyter_server_config.json /etc/jupyter/jupyter_server_config.json
# Add the test notebook
COPY test_notebook.ipynb /usr/share/test_notebook.ipynb
