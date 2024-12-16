# app/logging_config.py

from loguru import logger
from .config import settings
import sys

def setup_logging():
    logger.remove()  # Remove the default logger
    if settings.ENABLE_LOGS:
        logger.add(sys.stdout, level="DEBUG")
        logger.add("app.log", rotation="10 MB", level="INFO")
    else:
        logger.add(sys.stdout, level="WARNING")
