"""
Stable Video Diffusion (SVD) integration for VEO project.
Provides video generation using SVD as an alternative to LTX-Video.
"""

import asyncio
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import torch
from PIL import Image
import numpy as np
from loguru import logger

from ..models.config import VEOConfig, VideoRequest, AspectRatio, PersonGeneration
from ..utils.logger import get_logger


class SVDClient:
    """
    Stable Video Diffusion client for video generation.
    """
    
    def __init__(self, config: VEOConfig):
        """
        Initialize SVD client.
        
        Args:
            config: VEO configuration
        """
        self.config = config
        self.logger = get_logger("svd.video")
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.logger.info(f"SVD client initialized on device: {self.device}")
    
    async def initialize_pipeline(self):
        """
        Initialize the SVD pipeline.
        """
        if self.pipeline is not None:
            return
        
        try:
            from diffusers import StableVideoDiffusionPipeline
            
            self.logger.info("Loading SVD pipeline...")
            
            # Load the pipeline with optimizations
            self.pipeline = StableVideoDiffusionPipeline.from_pretrained(
                "stabilityai/stable-video-diffusion",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                variant="fp16" if self.device == "cuda" else None,
                use_safetensors=True,
                low_cpu_mem_usage=True
            )
            
            # Move to device
            self.pipeline = self.pipeline.to(self.device)
            
            # Enable memory efficient attention
            self.pipeline.enable_model_cpu_offload()
            
            self.logger.success("SVD pipeline loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load SVD pipeline: {e}")
            raise
    
    async def generate_video_async(
        self, 
        request: VideoRequest,
        progress_callback: Optional[callable] = None
    ) -> List[str]:
        """
        Generate video using SVD.
        
        Args:
            request: Video generation request
            progress_callback: Optional progress callback
            
        Returns:
            List of generated video URIs
        """
        self.logger.info(f"Starting SVD generation: {request.prompt[:50]}...")
        
        try:
            # Initialize pipeline if needed
            await self.initialize_pipeline()
            
            if progress_callback:
                progress_callback({"status": "initializing", "progress": 10})
            
            # Prepare generation parameters
            generation_params = self._prepare_generation_params(request)
            
            if progress_callback:
                progress_callback({"status": "generating", "progress": 25})
            
            # Generate videos
            video_paths = []
            for i in range(request.number_of_videos):
                if progress_callback:
                    progress_callback({
                        "status": "generating", 
                        "progress": 25 + (i * 50 // request.number_of_videos)
                    })
                
                # Generate single video
                video_path = await self._generate_single_video(
                    request, generation_params, i
                )
                video_paths.append(video_path)
            
            if progress_callback:
                progress_callback({"status": "completed", "progress": 100})
            
            self.logger.success(f"Generated {len(video_paths)} video(s) successfully")
            return video_paths
            
        except Exception as e:
            self.logger.error(f"SVD generation failed: {str(e)}")
            raise
    
    def _prepare_generation_params(self, request: VideoRequest) -> Dict[str, Any]:
        """
        Prepare generation parameters for SVD.
        
        Args:
            request: Video generation request
            
        Returns:
            Generation parameters
        """
        # Calculate number of frames (SVD works with 25 frames max)
        num_frames = min(25, max(14, request.duration * 3))  # ~3 FPS
        
        params = {
            "num_frames": num_frames,
            "num_inference_steps": 25,
            "min_guidance_scale": 1.0,
            "max_guidance_scale": 3.0,
            "motion_bucket_id": 127,
            "noise_aug_strength": 0.02,
        }
        
        # Add image if provided
        if request.image_path:
            params["image"] = self._load_image(request.image_path)
        else:
            # SVD requires an input image
            params["image"] = self._create_default_image()
        
        return params
    
    def _load_image(self, image_path: Path) -> Image.Image:
        """
        Load and process image for SVD.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Processed PIL Image
        """
        try:
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to SVD requirements (1024x576)
            image = image.resize((1024, 576), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            self.logger.error(f"Failed to load image {image_path}: {e}")
            raise
    
    def _create_default_image(self) -> Image.Image:
        """
        Create a default image for SVD when no input image is provided.
        
        Returns:
            Default PIL Image
        """
        # Create a simple gradient image
        width, height = 1024, 576
        image = Image.new('RGB', (width, height), color=(100, 150, 200))
        
        # Add some simple pattern
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        
        # Draw some circles
        for i in range(5):
            x = (i + 1) * width // 6
            y = height // 2
            radius = 50 + i * 10
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                        fill=(255-i*50, 100+i*30, 150+i*20))
        
        return image
    
    async def _generate_single_video(
        self, 
        request: VideoRequest, 
        params: Dict[str, Any], 
        video_index: int
    ) -> str:
        """
        Generate a single video using SVD.
        
        Args:
            request: Video generation request
            params: Generation parameters
            video_index: Index of video being generated
            
        Returns:
            Path to generated video
        """
        # Generate unique filename
        timestamp = int(time.time())
        video_filename = f"svd_video_{timestamp}_{video_index}.mp4"
        video_path = self.config.output_dir / video_filename
        
        try:
            # Generate video using SVD pipeline
            video_frames = self.pipeline(
                image=params["image"],
                num_frames=params["num_frames"],
                num_inference_steps=params["num_inference_steps"],
                min_guidance_scale=params["min_guidance_scale"],
                max_guidance_scale=params["max_guidance_scale"],
                motion_bucket_id=params["motion_bucket_id"],
                noise_aug_strength=params["noise_aug_strength"],
                generator=torch.Generator().manual_seed(int(time.time()) % 2**32),
            ).frames[0]
            
            # Save video
            self._save_video(video_frames, video_path)
            
            self.logger.info(f"Generated video: {video_path}")
            return f"file://{video_path.absolute()}"
            
        except Exception as e:
            self.logger.error(f"Failed to generate video {video_index}: {e}")
            raise
    
    def _save_video(self, frames: List[np.ndarray], output_path: Path):
        """
        Save video frames to MP4 file.
        
        Args:
            frames: List of video frames as numpy arrays
            output_path: Output file path
        """
        try:
            import imageio
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save video using imageio
            imageio.mimsave(
                str(output_path),
                frames,
                fps=3,  # SVD generates at ~3 FPS
                codec='libx264',
                quality=8
            )
            
            self.logger.info(f"Video saved: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save video: {e}")
            raise
    
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
                "message": "Local SVD generation completed"
            }
        }
