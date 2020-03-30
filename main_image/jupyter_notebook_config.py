NBApp = c.NotebookApp
NBApp.kernel_spec_manager_class = 'qt_kernel_spec_manager.QTKernelSpecManager'
NBApp.nbserver_extensions = {
  "nb_conda": True,
  "jupyterlab": True,
  "jupyter_cms": True,
  "ipyparallel.nbextension": True,
  "jupyter_server_proxy": True,
  "jupyterlab_black": True,
  "jupyterlab_git": True,
  "nbgitpuller": True,
}
