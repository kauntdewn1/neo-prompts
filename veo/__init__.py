"""
VEO - Video Generation Engine
A modern, async-first video generation system using Google's VEO API.
"""

__version__ = "2.0.0"
__author__ = "Mellø"

from .core.client import VEOClient
from .core.generator import VideoGenerator
from .models.config import VEOConfig, VideoRequest
from .utils.logger import setup_logger

__all__ = [
    "VEOClient",
    "VideoGenerator", 
    "VEOConfig",
    "VideoRequest",
    "setup_logger"
]
