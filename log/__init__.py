import logging
from .__utils import edit_name

def get_logger(name: str, logger_level: int = logging.INFO) -> logging.Logger:
    if '.' in name:
        name = edit_name(name)
    logger = logging.getLogger(name)
    logger.setLevel(logger_level)
    return logger

logger = get_logger(__name__)
