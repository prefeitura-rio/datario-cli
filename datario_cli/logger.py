"""
Logger module for edrio.
"""

import sys

import emoji
from loguru import logger

fmt = (
    # "<blue>{time:YYYY-MM-DD HH:mm:ss.SSS}</blue> | "
    # "<level>{level: <8}</level> | "
    "<level>{message}</level>"
)
config = {
    "handlers": [
        {"sink": sys.stderr, "format": fmt},
    ]
}
logger.configure(**config)


def log(message, level="info"):
    """
    Log a message.
    """
    funcs = {
        "debug": logger.debug,
        "info": logger.info,
        "success": logger.success,
        "warning": logger.warning,
        "error": logger.error,
    }
    if level not in funcs:
        logger.error(f"Invalid log level: {level}")
        raise ValueError(f"Invalid log level: {level}")
    funcs[level](emoji.emojize(message))
