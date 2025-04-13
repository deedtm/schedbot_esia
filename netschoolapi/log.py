from os import path as p
import logging

logger_name = __file__.split(p.sep)[-2]
logger = logging.getLogger(logger_name)
