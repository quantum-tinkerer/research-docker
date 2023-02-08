FROM gitlab.kwant-project.org:5005/qt/research-docker:base
ARG SINGULARITY_URL
ENV SINGULARITY_URL=$SINGULARITY_URL

USER root
WORKDIR /

# Add environment files
COPY python3.yml /environments/

# Update the root environment
RUN mamba env update -n base -f /environments/python3.yml \
    && mamba clean --quiet --yes --all \
    && fix-permissions /opt/conda

# Figure out the future Singularity image address
COPY gitconfig gitattributes gitignore /opt/conda/etc/

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
