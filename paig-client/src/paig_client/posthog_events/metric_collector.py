import os
import platform


def get_version():
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../VERSION')) as file:
            for line in file:
                if line.startswith('__version__'):
                    # Extract the version value from the line
                    version = line.split('=')[1].strip().strip("'\"")
                    return version
    except Exception:
        return 'unknown'


class MetricsClient:

    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsClient, cls).__new__(cls)
            cls._instance.data = dict()
        return cls._instance

    def initialize(self):
        self.data['app_version'] = get_version()
        self.data.update(self._get_system_info())

    @staticmethod
    def _get_system_info():
        return {
            'python_version': platform.python_version(),
            'os': platform.system(),
            'env': detect_environment(),
            'deployment': os.environ.get('PAIG_CLIENT', 'dev')
        }

    def get_data(self):
        return self.data


def get_metric_client():
    return MetricsClient()

def detect_environment():
    if is_jupyter_notebook():
        return 'jupyter'
    elif is_colab():
        return 'colab'
    elif is_docker():
        return 'docker'
    else:
        return 'local'


def is_jupyter_notebook():
    try:
        from IPython import get_ipython
        # Check if IPython is available and running in a notebook environment
        ipython = get_ipython()
        if ipython is None:
            return False
        return 'IPKernelApp' in ipython.config.get('IPKernelApp', {})
    except:
        return False


def is_colab():
    try:
        import google.colab
    except ImportError:
        return False
    try:
        from IPython.core.getipython import get_ipython
    except ImportError:
        return False
    return True


def is_docker():
    return os.path.exists('/.dockerenv')
