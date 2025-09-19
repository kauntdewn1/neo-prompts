"""
Logging utilities for VEO.
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Literal, Optional


def setup_logger(
    level: str = "INFO",
    format_type: Literal["json", "text"] = "text",
    log_file: Optional[Path] = None
) -> None:
    """
    Setup structured logging for VEO.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Log format type (json or text)
        log_file: Optional log file path
    """
    # Remove default handler
    logger.remove()
    
    # Choose format
    if format_type == "json":
        log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"
    else:
        log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
    
    # Console handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=level,
        colorize=format_type == "text",
        backtrace=True,
        diagnose=True
    )
    
    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            format=log_format,
            level=level,
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
    
    # Add custom levels (only if they don't exist)
    try:
        logger.level("SUCCESS", no=25, color="<green>")
    except ValueError:
        pass  # Level already exists
    
    try:
        logger.level("PROGRESS", no=15, color="<blue>")
    except ValueError:
        pass  # Level already exists
    
    return logger


def get_logger(name: str = "veo"):
    """Get logger instance for a specific module."""
    return logger.bind(name=name)
