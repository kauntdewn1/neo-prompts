"""
Video Generation API integration.
Provides interface to SVD and LTX-Video for video generation.
"""

import asyncio
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from loguru import logger

from ..models.config import VEOConfig, VideoRequest, AspectRatio, PersonGeneration
from ..utils.logger import get_logger
from .ltx_video_client import LTXVideoClient
from .svd_client import SVDClient


class VideoGeneratorAPI:
    """
    Video generation API using SVD and LTX-Video.
    """
    
    def __init__(self, config: VEOConfig):
        """
        Initialize video generation API.
        
        Args:
            config: VEO configuration
        """
        self.config = config
        self.logger = get_logger("video.generator")
        
        # Initialize video generation clients
        self.ltx_client = LTXVideoClient(config)
        self.svd_client = SVDClient(config)
        
        self.logger.info("Video generation API initialized with SVD and LTX-Video")
    
    async def generate_video_async(
        self, 
        request: VideoRequest,
        progress_callback: Optional[callable] = None
    ) -> List[str]:
        """
        Generate video using SVD (primary) or LTX-Video (fallback).
        
        Args:
            request: Video generation request
            progress_callback: Optional progress callback
            
        Returns:
            List of generated video URIs
        """
        self.logger.info(f"Starting video generation: {request.prompt[:50]}...")
        
        try:
            # Try SVD first (most reliable)
            try:
                self.logger.info("Attempting SVD generation...")
                video_uris = await self.svd_client.generate_video_async(request, progress_callback)
                self.logger.success(f"SVD generated {len(video_uris)} video(s) successfully")
                return video_uris
                
            except Exception as svd_error:
                self.logger.warning(f"SVD failed: {svd_error}")
                self.logger.info("Falling back to LTX-Video...")
                
                # Fallback to LTX-Video
                video_uris = await self.ltx_client.generate_video_async(request, progress_callback)
                self.logger.success(f"LTX-Video generated {len(video_uris)} video(s) successfully")
                return video_uris
            
        except Exception as e:
            self.logger.error(f"All video generation methods failed: {str(e)}")
            raise
    
    async def download_video(self, video_uri: str, local_path: Path) -> bool:
        """
        Download video from URI to local path.
        
        Args:
            video_uri: Video URI (file:// or http://)
            local_path: Local path to save video
            
        Returns:
            True if successful
        """
        try:
            if video_uri.startswith("file://"):
                # Local file, just copy
                source_path = Path(video_uri[7:])  # Remove file://
                if source_path.exists():
                    import shutil
                    shutil.copy2(source_path, local_path)
                    self.logger.info(f"Copied video: {source_path} -> {local_path}")
                    return True
                else:
                    self.logger.error(f"Source file not found: {source_path}")
                    return False
            else:
                # HTTP download
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(video_uri)
                    response.raise_for_status()
                    
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                    
                    self.logger.info(f"Downloaded video: {video_uri} -> {local_path}")
                    return True
                    
        except Exception as e:
            self.logger.error(f"Failed to download video {video_uri}: {str(e)}")
            return False
    
    async def check_operation_status(self, operation_id: str) -> Dict[str, Any]:
        """
        Check operation status (not applicable for local generation).
        
        Args:
            operation_id: Operation ID
            
        Returns:
            Status information
        """
        return {
            "operation_id": operation_id,
            "status": "completed",
            "progress": 100,
            "result": {
                "message": "Local generation completed"
            }
        }
