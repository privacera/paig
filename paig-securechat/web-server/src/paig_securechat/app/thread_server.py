from threading import Thread
from time import sleep, time
from typing import Generator
from uvicorn import Config, Server
from uvicorn.config import LoopSetupType
import asyncio



def _nest_asyncio_applied() -> bool:
    """
    Determines whether nest_asyncio has been applied. If it is applied, the app must use
    the "asyncio" loop.
    """
    return hasattr(asyncio, "_nest_patched")


class ThreadServer(Server):
    """Server that runs in a (non-daemon) thread"""

    def __init__(
        self,
        app: str,
        host: str,
        port: int,
        root_path: str,
    ) -> None:
        """ Must use asyncio loop if nest_asyncio is applied,
        Otherwise the app crashes when the server is run in a thread. """

        loop: LoopSetupType = "asyncio" if _nest_asyncio_applied() else "auto"
        config = Config(
            app=app,
            host=host,
            port=port,
            root_path=root_path,
            loop=loop,
            workers=1,
        )
        super().__init__(config=config)

    def install_signal_handlers(self) -> None:
        pass

    def run_in_thread(self, startup_timeout) -> Generator[Thread, None, None]:
        """A coroutine to keep the server running in a thread."""
        thread = Thread(target=self.run, daemon=True)
        thread.start()
        time_limit = time() + startup_timeout  # seconds to start the server
        try:
            while (
                time() < time_limit
                and thread.is_alive()
                and not self.should_exit
                and not self.started
            ):
                sleep(1e-3)
            if time() >= time_limit and not self.started:
                self.should_exit = True
                raise RuntimeError("Server took too long to start")
            yield thread
        finally:
            self.should_exit = True
            thread.join(timeout=5)
