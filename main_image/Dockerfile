FROM gitlab.kwant-project.org:5005/qt/research-docker:base

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
    && jupyter labextension install \
            @jupyter-widgets/jupyterlab-manager \
            # FIXME https://github.com/jupyterlab/jupyterlab-latex/issues/135
            # @jupyterlab/latex \
            @bokeh/jupyter_bokeh \
            @pyviz/jupyterlab_pyviz \
            @ryantam626/jupyterlab_code_formatter \
            @jupyterlab/git \
            @jupyterlab/toc \
            @jupyterlab/server-proxy \
            @aquirdturtle/collapsible_headings \
            @krassowski/jupyterlab-lsp \
            dask-labextension \
    && jupyter lab build \
    && fix-permissions /opt/conda

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID
COPY jupyter_notebook_config.d/set_root_dir.json /opt/conda/etc/jupyter/jupyter_notebook_config.d
# Create parallel profiles and copy the correct config
RUN ipython profile create --parallel --profile python3 --ipython-dir /opt/conda/etc/ipython
# RUN ipython profile create --parallel --profile dev --ipython-dir /opt/conda/etc/ipython
COPY ipcluster_config_python3.py /opt/conda/etc/ipython/profile_python3/ipcluster_config.py
# COPY ipcluster_config_dev.py /opt/conda/etc/ipython/profile_dev/ipcluster_config.py
