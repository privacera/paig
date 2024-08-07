import os, sys
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)
try:
    """Optional dependency for running the app in a notebook."""
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

from core.thread_server import ThreadServer
from typing import Optional
import uvicorn

try:
    from IPython.display import IFrame
except:
    pass

_GOOGLE_COLAB = False


def _get_url(host: str, port: int) -> str:
    """Determines the IFrame URL based on whether this is in a Colab or in a local notebook"""
    global _GOOGLE_COLAB
    if _GOOGLE_COLAB:
        from google.colab.output import eval_js
        return str(eval_js(f"google.colab.kernel.proxyPort({port}, {{'cache': true}})"))
    if host == "0.0.0.0" or host == "127.0.0.1":
        return f"http://localhost:{port}/"
    return f"http://{host}:{port}/"


class ThreadSession:
    def __init__(self, host: str, port: int, root_path: str, startup_timeout=600):
        self.host = host
        self.port = port
        self.root_path = root_path
        self.server = ThreadServer(
            app="server:app",
            host=self.host,
            port=self.port,
            root_path=self.root_path,
        ).run_in_thread(startup_timeout=startup_timeout)
        # start the server
        self.server_thread = next(self.server)

    @property
    def url(self) -> str:
        return _get_url(self.host, self.port)

    @property
    def active(self) -> bool:
        return self.server_thread.is_alive()

    def end(self) -> None:
        self.server.close()

    def view(self, height: int = 1000):
        print(f"📺 Opening a view to the Privacera PAIG app. The app is running at {self.url}")
        return IFrame(src=self.url, width="100%", height=height)


def _is_colab() -> bool:
    """Determines whether this is in a Colab"""
    try:
        import google.colab
    except ImportError:
        return False
    try:
        from IPython.core.getipython import get_ipython
    except ImportError:
        return False
    return get_ipython() is not None


_session: Optional[ThreadSession] = None


def launch_app(
    run_in_thread: bool = True,
    host: str = "127.0.0.1",
    port: int = 4545,
    config_path: str = None,
    custom_config_path: str = None,
    paig_deployment: str = 'dev',
    startup_timeout: int = 600,
    workers: int = 1
):
    global _session, _GOOGLE_COLAB
    if _is_colab():
        _GOOGLE_COLAB = True
    if _session is not None and _session.active:
        _session.end()
    set_up_standalone_mode(
        host,
        port,
        config_path,
        custom_config_path,
        paig_deployment,
        ROOT_DIR
    )
    cleanup()
    from alembic_db import create_or_update_tables, create_default_user_and_ai_application
    create_or_update_tables(ROOT_DIR)
    create_default_user_and_ai_application()

    import asyncio
    from api.encryption.events.startup import create_default_encryption_keys
    asyncio.run(create_default_encryption_keys())

    if run_in_thread:
        _session = ThreadSession(host=host, port=port, root_path=ROOT_DIR, startup_timeout=startup_timeout)
    else:
        uvicorn.run(
            app="server:app",
            host=host,
            port=port,
            workers=workers,
            root_path=ROOT_DIR,
        )
    return _session


def set_up_standalone_mode(
        host,
        port,
        config_path,
        custom_config_path,
        paig_deployment,
        root_dir
):
    from core import constants
    constants.SINGLE_USER_MODE = _is_colab()
    constants.HOST = host
    constants.PORT = port
    constants.MODE = "standalone"
    if config_path is None:
        config_path = os.path.join(root_dir, "conf")
    if custom_config_path is None:
        custom_config_path = 'custom-conf'
    os.environ["CONFIG_PATH"] = str(config_path)
    os.environ["EXT_CONFIG_PATH"] = str(custom_config_path)
    os.environ["PAIG_ROOT_DIR"] = str(root_dir)
    if paig_deployment:
        os.environ["PAIG_DEPLOYMENT"] = str(paig_deployment)


def active_session():
    """
    Returns the active session if one exists, otherwise returns None
    """
    if _session and _session.active:
        print("Active session found")
        return _session
    print("No active session found")
    return None


def close_app() -> None:
    """
    Closes the  application.
    The application server is shut down and will no longer be accessible.
    """
    global _session
    if _session is None:
        print("No active session to close")
        return
    _session.end()
    _session = None
    print("Session closed")


def cleanup():
    import atexit
    import shutil
    import os
    import fasteners
    from core import constants
    lock = fasteners.InterProcessLock(constants.SCHEDULER_LOCK)
    atexit.register(lock.release)
    _temp_dir = os.path.join(ROOT_DIR, constants.TEMP_DIR)
    if os.path.exists(_temp_dir):
        shutil.rmtree(_temp_dir, ignore_errors=True)
