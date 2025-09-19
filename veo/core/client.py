"""
VEO API client with async support and retry logic.
"""

import asyncio
import time
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..models.config import VEOConfig, VideoRequest
from ..utils.logger import get_logger
from .video_generator_api import VideoGeneratorAPI


class VEOClient:
    """
    Modern VEO API client with async support, retry logic, and proper error handling.
    """
    
    def __init__(self, config: VEOConfig):
        """
        Initialize VEO client.
        
        Args:
            config: VEO configuration
        """
        self.config = config
        self.logger = get_logger("veo.client")
        
        # Initialize video generation API
        self.api_client = VideoGeneratorAPI(config)
        
        self.logger.info(f"VEO client initialized with model: {config.model}")
    
    async def generate_video_async(
        self, 
        request: VideoRequest,
        progress_callback: Optional[callable] = None
    ) -> List[str]:
        """
        Generate video asynchronously with progress tracking.
        
        Args:
            request: Video generation request
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of generated video URIs
        """
        self.logger.info(f"Starting video generation: {request.prompt[:50]}...")
        
        try:
            # Use real VEO API
            video_uris = await self.api_client.generate_video_async(request, progress_callback)
            
            self.logger.success(f"Generated {len(video_uris)} video(s) successfully")
            return video_uris
            
        except Exception as e:
            self.logger.error(f"Video generation failed: {str(e)}")
            raise
    
    async def check_operation_status(self, operation_id: str) -> Dict[str, Any]:
        """
        Check the status of a VEO operation.
        
        Args:
            operation_id: Operation ID to check
            
        Returns:
            Operation status information
        """
        return await self.api_client.check_operation_status(operation_id)
    
    def generate_video_sync(
        self, 
        request: VideoRequest,
        progress_callback: Optional[callable] = None
    ) -> List[str]:
        """
        Synchronous wrapper for video generation.
        
        Args:
            request: Video generation request
            progress_callback: Optional progress callback
            
        Returns:
            List of generated video URIs
        """
        return asyncio.run(self.generate_video_async(request, progress_callback))
    
    async def batch_generate_videos(
        self, 
        requests: List[VideoRequest],
        max_concurrent: Optional[int] = None
    ) -> List[List[str]]:
        """
        Generate multiple videos concurrently.
        
        Args:
            requests: List of video generation requests
            max_concurrent: Maximum concurrent operations
            
        Returns:
            List of video URI lists for each request
        """
        max_concurrent = max_concurrent or self.config.max_concurrent_operations
        
        self.logger.info(f"Starting batch generation of {len(requests)} videos (max concurrent: {max_concurrent})")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_semaphore(request):
            async with semaphore:
                return await self.generate_video_async(request)
        
        tasks = [generate_with_semaphore(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Request {i} failed: {str(result)}")
                successful_results.append([])
            else:
                successful_results.append(result)
        
        self.logger.success(f"Batch generation completed: {len(successful_results)} results")
        return successful_results