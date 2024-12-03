import sys
from pathlib import Path

from loguru import logger


LOGGER_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)


def reinit_logger(log_level: str, log_path: str | None):
    """Setup logger"""
    logger.remove()
    logger.add(
        sys.stderr, level=log_level, format=LOGGER_FORMAT, colorize=True
    )
    logger.log(log_level, "Logger re-inited")

    if not log_path:
        return

    log_path = Path(log_path)
    log_path.mkdir(parents=True, exist_ok=True)
    log_file = log_path / "app.log"

    logger.log(log_level, f"Log directory: {log_path}")
    logger.add(
        log_file, level=log_level, format=LOGGER_FORMAT, rotation="2 week"
    )
