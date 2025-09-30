import logging

from .config import settings


def configure_logging() -> None:
    root_level = getattr(logging, settings.log_level.upper())
    logging.root.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logging.root.addHandler(handler)
    logging.root.setLevel(root_level)
