"""
High-level video generation interface with file management and utilities.
"""

import asyncio
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import aiofiles
from google.cloud import storage

from ..models.config import VEOConfig, VideoRequest, AspectRatio, PersonGeneration
from ..core.client import VEOClient
from ..utils.logger import get_logger


class VideoGenerator:
    """
    High-level video generation interface with file management and utilities.
    """
    
    def __init__(self, config: VEOConfig):
        """
        Initialize video generator.
        
        Args:
            config: VEO configuration
        """
        self.config = config
        self.client = VEOClient(config)
        self.logger = get_logger("veo.generator")
        
        # Initialize GCS client if bucket is configured
        self.gcs_client = None
        if config.gcs_bucket:
            try:
                self.gcs_client = storage.Client()
                self.logger.info(f"GCS client initialized for bucket: {config.gcs_bucket}")
            except Exception as e:
                self.logger.warning(f"Failed to initialize GCS client: {e}")
                self.gcs_client = None
    
    async def generate_from_prompt(
        self,
        prompt: str,
        aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE,
        duration: int = 8,
        number_of_videos: int = 1,
        person_generation: PersonGeneration = PersonGeneration.ALLOW_ADULT,
        enhance_prompt: bool = True,
        output_filename: Optional[str] = None
    ) -> List[Path]:
        """
        Generate video from text prompt.
        
        Args:
            prompt: Video generation prompt
            aspect_ratio: Video aspect ratio
            duration: Video duration in seconds
            number_of_videos: Number of videos to generate
            person_generation: Person generation setting
            enhance_prompt: Whether to enhance the prompt
            output_filename: Custom output filename
            
        Returns:
            List of local file paths for generated videos
        """
        request = VideoRequest(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            duration=duration,
            number_of_videos=number_of_videos,
            person_generation=person_generation,
            enhance_prompt=enhance_prompt,
            output_filename=output_filename
        )
        
        return await self._generate_and_download(request)
    
    async def generate_from_image(
        self,
        prompt: str,
        image_path: Union[str, Path],
        aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE,
        duration: int = 8,
        number_of_videos: int = 1,
        person_generation: PersonGeneration = PersonGeneration.ALLOW_ADULT,
        enhance_prompt: bool = True,
        output_filename: Optional[str] = None
    ) -> List[Path]:
        """
        Generate video from image and prompt.
        
        Args:
            prompt: Video generation prompt
            image_path: Path to input image
            aspect_ratio: Video aspect ratio
            duration: Video duration in seconds
            number_of_videos: Number of videos to generate
            person_generation: Person generation setting
            enhance_prompt: Whether to enhance the prompt
            output_filename: Custom output filename
            
        Returns:
            List of local file paths for generated videos
        """
        request = VideoRequest(
            prompt=prompt,
            image_path=Path(image_path),
            aspect_ratio=aspect_ratio,
            duration=duration,
            number_of_videos=number_of_videos,
            person_generation=person_generation,
            enhance_prompt=enhance_prompt,
            output_filename=output_filename
        )
        
        return await self._generate_and_download(request)
    
    async def _generate_and_download(self, request: VideoRequest) -> List[Path]:
        """
        Generate video and download to local storage.
        
        Args:
            request: Video generation request
            
        Returns:
            List of local file paths for generated videos
        """
        self.logger.info(f"Generating video: {request.prompt[:50]}...")
        
        # Set up GCS output if configured
        if self.config.gcs_bucket and not request.output_gcs_uri:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            request.output_gcs_uri = f"gs://{self.config.gcs_bucket}/videos/{timestamp}/"
        
        # Generate video
        video_uris = await self.client.generate_video_async(request)
        
        # Download videos
        local_paths = []
        for i, uri in enumerate(video_uris):
            local_path = await self._download_video(uri, request, i)
            local_paths.append(local_path)
        
        self.logger.success(f"Generated and downloaded {len(local_paths)} video(s)")
        return local_paths
    
    async def _download_video(
        self, 
        video_uri: str, 
        request: VideoRequest, 
        index: int
    ) -> Path:
        """
        Download video from URI to local storage.
        
        Args:
            video_uri: Video URI (GCS or direct)
            request: Original video request
            index: Video index for naming
            
        Returns:
            Local file path
        """
        # Generate filename
        if request.output_filename:
            if len(video_uris) > 1:
                name = f"{request.output_filename}_{index}.mp4"
            else:
                name = f"{request.output_filename}.mp4"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"video_{timestamp}_{index}.mp4"
        
        local_path = self.config.output_dir / name
        
        # Download based on URI type
        if video_uri.startswith("file://"):
            # Local file - use API client
            await self.client.api_client.download_video(video_uri, local_path)
        elif video_uri.startswith("gs://"):
            if self.gcs_client:
                await self._download_from_gcs(video_uri, local_path)
            else:
                # Use the API client to download
                await self.client.api_client.download_video(video_uri, local_path)
        else:
            await self._download_from_url(video_uri, local_path)
        
        self.logger.info(f"Downloaded video: {local_path}")
        return local_path
    
    async def _download_from_gcs(self, gcs_uri: str, local_path: Path) -> None:
        """
        Download video from Google Cloud Storage.
        
        Args:
            gcs_uri: GCS URI (gs://bucket/path)
            local_path: Local destination path
        """
        if not self.gcs_client:
            raise ValueError("GCS client not initialized")
        
        # Parse GCS URI
        if not gcs_uri.startswith("gs://"):
            raise ValueError("Invalid GCS URI format")
        
        bucket_name, blob_name = gcs_uri[5:].split("/", 1)
        
        # Download
        bucket = self.gcs_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Ensure directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download file
        blob.download_to_filename(str(local_path))
    
    async def _download_from_url(self, url: str, local_path: Path) -> None:
        """
        Download video from direct URL.
        
        Args:
            url: Video URL
            local_path: Local destination path
        """
        import httpx
        
        # Ensure directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download with progress
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                
                async with aiofiles.open(local_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        await f.write(chunk)
    
    async def _create_mock_video(self, local_path: Path) -> None:
        """
        Create a mock video file for testing.
        
        Args:
            local_path: Local destination path
        """
        # Ensure directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a simple text file as mock video
        mock_content = f"Mock video file created at {datetime.now()}\nThis is a placeholder for the actual video file."
        
        async with aiofiles.open(local_path, "w") as f:
            await f.write(mock_content)
    
    async def batch_generate_from_prompts(
        self,
        prompts: List[str],
        aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE,
        duration: int = 8,
        number_of_videos: int = 1,
        person_generation: PersonGeneration = PersonGeneration.ALLOW_ADULT,
        enhance_prompt: bool = True,
        max_concurrent: Optional[int] = None
    ) -> List[List[Path]]:
        """
        Generate multiple videos from prompts concurrently.
        
        Args:
            prompts: List of video generation prompts
            aspect_ratio: Video aspect ratio
            duration: Video duration in seconds
            number_of_videos: Number of videos to generate per prompt
            person_generation: Person generation setting
            enhance_prompt: Whether to enhance prompts
            max_concurrent: Maximum concurrent operations
            
        Returns:
            List of video file path lists for each prompt
        """
        self.logger.info(f"Starting batch generation of {len(prompts)} prompts")
        
        # Create requests
        requests = []
        for prompt in prompts:
            request = VideoRequest(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                duration=duration,
                number_of_videos=number_of_videos,
                person_generation=person_generation,
                enhance_prompt=enhance_prompt
            )
            requests.append(request)
        
        # Generate videos
        video_uri_lists = await self.client.batch_generate_videos(
            requests, 
            max_concurrent
        )
        
        # Download all videos
        all_local_paths = []
        for i, video_uris in enumerate(video_uri_lists):
            local_paths = []
            for j, uri in enumerate(video_uris):
                request = requests[i]
                local_path = await self._download_video(uri, request, j)
                local_paths.append(local_path)
            all_local_paths.append(local_paths)
        
        self.logger.success(f"Batch generation completed: {len(all_local_paths)} prompt results")
        return all_local_paths
    
    def cleanup_old_videos(self, days_old: int = 7) -> int:
        """
        Clean up old video files.
        
        Args:
            days_old: Remove files older than this many days
            
        Returns:
            Number of files removed
        """
        import time
        
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        removed_count = 0
        
        for file_path in self.config.output_dir.glob("*.mp4"):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                removed_count += 1
                self.logger.debug(f"Removed old file: {file_path}")
        
        self.logger.info(f"Cleaned up {removed_count} old video files")
        return removed_count
