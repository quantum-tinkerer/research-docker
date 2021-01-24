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
COPY ipcluster_config_python3.py /opt/conda/etc/ipython/profile_python3/ipcluster_config.py
