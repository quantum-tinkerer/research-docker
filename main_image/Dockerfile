FROM gitlab.kwant-project.org:5005/qt/research-docker:base

USER root
WORKDIR /

# Add environment files
RUN mkdir /environments
COPY python3.yml dev.yml fenics.yml install_dev.sh /environments/

# Update the root environment
RUN conda env update --quiet -n root -f /environments/python3.yml && \
    conda clean --quiet --yes --all

# Add a dev environment (e.g. with dev kwant and holoviews)
# RUN conda env create -p /opt/conda/envs/dev -f /environments/dev.yml

# Enable `jupyter nbextension`s
RUN jupyter nbextension enable --py --sys-prefix ipyparallel && \
    jupyter nbextension enable --py --sys-prefix jupyter_cms && \
    jupyter serverextension enable --sys-prefix jupyter_server_proxy && \
    jupyter serverextension enable --py --sys-prefix jupyterlab_code_formatter && \
    # FIXME https://github.com/jupyterlab/jupyterlab-git/pull/520
    #jupyter serverextension enable --py --sys-prefix jupyterlab_git && \
    jupyter serverextension enable --sys-prefix nbgitpuller && \
    jupyter labextension install \
            @jupyter-widgets/jupyterlab-manager \
            @jupyterlab/latex \
            @bokeh/jupyter_bokeh \
            @pyviz/jupyterlab_pyviz \
            @ryantam626/jupyterlab_code_formatter \
            # FIXME https://github.com/jupyterlab/jupyterlab-git/pull/520
            #@jupyterlab/git \
            @jupyterlab/toc \
            @aquirdturtle/collapsible_headings \
            @krassowski/jupyterlab-lsp \
            && \
    jupyter lab build  # apparently jupyterlab-git needs this

# prevent nb_conda_kernels from overriding our custom kernel manager
RUN rm /opt/conda/etc/jupyter/jupyter_notebook_config.json

# Add notebook config
COPY jupyter_notebook_config.py /opt/conda/etc/jupyter/

# Create parallel profiles and copy the correct config
RUN ipython profile create --parallel --profile python3 --ipython-dir /opt/conda/etc/ipython
# RUN ipython profile create --parallel --profile dev --ipython-dir /opt/conda/etc/ipython
COPY ipcluster_config_python3.py /opt/conda/etc/ipython/profile_python3/ipcluster_config.py
# COPY ipcluster_config_dev.py /opt/conda/etc/ipython/profile_dev/ipcluster_config.py

# Fix permissions (required when following the base image)
RUN fix-permissions /opt/conda

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID
