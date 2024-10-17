import os, sys
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)
try:
    """Optional dependency for running the app in a notebook."""
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

from database_setup import create_or_update_tables
from app.thread_server import ThreadServer
from typing import Optional
from core.utils import set_up_standalone_mode
import uvicorn
from core import constants
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
            app="app.server:app",
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
        print(f"📺 Opening a view to the PAIG SecureChat app. The app is running at {self.url}")
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
    host: str = "0.0.0.0",
    port: int = 3535,
    debug: bool = False,
    config_path: str = None,
    custom_config_path: str = None,
    disable_paig_shield_plugin: bool = False,
    openai_api_key: str = None,
    startup_timeout: int = 600
):
    global _session, _GOOGLE_COLAB
    if _is_colab():
        _GOOGLE_COLAB = True
    if _session is not None and _session.active:
        _session.end()
    set_up_standalone_mode(
        ROOT_DIR,
        debug,
        config_path,
        custom_config_path,
        disable_paig_shield_plugin,
        host,
        port,
        openai_api_key,
        single_user_mode=_GOOGLE_COLAB
    )

    if not os.path.exists("securechat"):
        os.makedirs("securechat")

    if run_in_thread:
        create_or_update_tables(ROOT_DIR)
        _session = ThreadSession(host=host, port=port, root_path=ROOT_DIR, startup_timeout=startup_timeout)
    else:
        create_or_update_tables(ROOT_DIR)
        uvicorn.run(
            app="app.server:app",
            host=host,
            port=port,
            workers=1,
            root_path=ROOT_DIR,
        )
    return _session


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
