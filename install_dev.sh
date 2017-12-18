conda clean --yes --all  # so we don't run into space issues
conda config --system --add envs_dirs ~/.conda/envs  # because of https://gitlab.kwant-project.org/qt/research-docker/issues/4
source deactivate  # make sure we are not using the dev env now
conda env remove --yes --name dev
CONDA_ALWAYS_COPY=true conda env create --file /environments/dev.yml
conda clean --yes --all  # so we don't run into space issues
