import logging
import os

logger: logging.Logger = logging.getLogger("paig_eval")

def _basic_config() -> None:
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s [%(name)s] %(filename)s  - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def setup_logging() -> None:
    env = os.environ.get("PAIG_EVEL_LOG")
    if env == "debug":
        _basic_config()
        logger.setLevel(logging.DEBUG)
    else:
        _basic_config()
        logger.setLevel(logging.INFO)