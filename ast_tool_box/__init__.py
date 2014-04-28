__author__ = 'Chick Markley'

__version__ = "0.5.0"

import logging

logger = logging.getLogger(__name__)


def logging_basic_config(level):
    """ Setup basic config logging. Useful for debugging to quickly setup a useful logger"""
    fmt = '%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s'
    logging.basicConfig(level=level, format=fmt)



