import logging
from . import logger


def disable_loggers(names: tuple[str] | str):
    if isinstance(names, tuple):
        names_str = ', '.join(names)
    else:
        names_str = names
    logger.info(f'Disabling {names_str} logging...')

    for name, _logger in logging.root.manager.loggerDict.items():
        if name.startswith(names) and isinstance(_logger, logging.Logger):
            logger.info(f"Disabled {name}")
            _logger.setLevel(logging.WARNING)

    logger.info('Logging was disabled')
    