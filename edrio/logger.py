"""
Logger module for edrio.
"""

import emoji
from loguru import logger


def log(message, level="info"):
    """
    Log a message.
    """
    funcs = {
        "debug": logger.debug,
        "info": logger.info,
        "warning": logger.warning,
        "error": logger.error,
    }
    if level not in funcs:
        logger.error(f"Invalid log level: {level}")
        raise ValueError(f"Invalid log level: {level}")
    funcs[level](emoji.emojize(message))
