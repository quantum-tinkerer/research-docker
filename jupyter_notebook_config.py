from nb_conda_kernels import CondaKernelSpecManager
from jupyter_client.kernelspec import NATIVE_KERNEL_NAME, KernelSpec


class QTKernelSpecManager(CondaKernelSpecManager):

    def find_kernel_specs(self):
        kspecs = super(QTKernelSpecManager, self).find_kernel_specs()
        # remove the "conda-root" kernelspec
        kspecs.pop('conda-root-py', None)
        return kspecs

    def get_kernel_spec(self, kernel_name):
        kspec = super(QTKernelSpecManager, self).get_kernel_spec(kernel_name)
        if kernel_name == 'python3':
            # override Conda kernel manager display name
            kspec = kspec.to_dict()
            kspec['display_name'] = 'Python 3'
            kspec = KernelSpec(**kspec)
        return kspec


NBApp = c.NotebookApp
NBApp.kernel_spec_manager_class = QTKernelSpecManager
NBApp.nbserver_extensions = {
  "nb_conda": True,
  "jupyterlab": True,
  "jupyter_cms": True,
  "ipyparallel.nbextension": True,
  "jupyter_server_proxy": True,
  "jupyterlab_black": True,
}
