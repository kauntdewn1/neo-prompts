"""
Configuration models for VEO video generation.
"""

from enum import Enum
from pathlib import Path
from typing import Optional, Literal
from pydantic import BaseModel, Field, validator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AspectRatio(str, Enum):
    """Supported aspect ratios for video generation."""
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"
    SQUARE = "1:1"


class PersonGeneration(str, Enum):
    """Person generation settings."""
    ALLOW_ADULT = "allow_adult"
    DONT_ALLOW = "dont_allow"


class VEOConfig(BaseModel):
    """Main configuration for VEO client."""
    
    # Hugging Face Configuration
    huggingface_token: Optional[str] = Field(None, description="Hugging Face token")
    
    # Model Configuration
    model: str = Field("Wan-AI/Wan2.1-T2V-1.3B-Diffusers", description="Video generation model to use")
    device: str = Field("auto", description="Device to use (cuda, cpu, auto)")
    low_memory: bool = Field(True, description="Use low memory mode")
    quality: str = Field("high", description="Generation quality (high, medium, low)")
    
    # Default Settings
    default_aspect_ratio: AspectRatio = Field(AspectRatio.LANDSCAPE, description="Default aspect ratio")
    default_duration: int = Field(8, ge=1, le=8, description="Default duration in seconds")
    default_number_of_videos: int = Field(1, ge=1, le=4, description="Default number of videos")
    default_person_generation: PersonGeneration = Field(PersonGeneration.ALLOW_ADULT, description="Default person generation")
    
    # Performance Settings
    max_concurrent_operations: int = Field(3, ge=1, le=10, description="Max concurrent operations")
    retry_attempts: int = Field(3, ge=1, le=10, description="Number of retry attempts")
    retry_delay: int = Field(30, ge=1, le=300, description="Delay between retries in seconds")
    
    # Output Settings
    output_dir: Path = Field(Path("output/videos"), description="Output directory for videos")
    gcs_bucket: Optional[str] = Field(None, description="GCS bucket for video storage")
    
    # Logging
    log_level: str = Field("INFO", description="Logging level")
    log_format: Literal["json", "text"] = Field("text", description="Log format")
    
    @validator('output_dir')
    def create_output_dir(cls, v):
        """Ensure output directory exists."""
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @classmethod
    def from_env(cls) -> 'VEOConfig':
        """Create config from environment variables."""
        return cls(
            huggingface_token=os.getenv("HUGGINGFACE_TOKEN"),
            model=os.getenv("VEO_MODEL", "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"),
            device=os.getenv("VEO_DEVICE", "auto"),
            low_memory=os.getenv("VEO_LOW_MEMORY", "true").lower() == "true",
            quality=os.getenv("VEO_QUALITY", "high"),
            default_aspect_ratio=AspectRatio(os.getenv("VEO_DEFAULT_ASPECT_RATIO", "16:9")),
            default_duration=int(os.getenv("VEO_DEFAULT_DURATION", "8")),
            default_number_of_videos=int(os.getenv("VEO_DEFAULT_COUNT", "1")),
            default_person_generation=PersonGeneration(os.getenv("VEO_PERSON_GENERATION", "allow_adult")),
            max_concurrent_operations=int(os.getenv("VEO_MAX_CONCURRENT", "3")),
            retry_attempts=int(os.getenv("VEO_RETRY_ATTEMPTS", "3")),
            retry_delay=int(os.getenv("VEO_REQUEST_DELAY", "30")),
            output_dir=Path(os.getenv("VEO_OUTPUT_DIR", "output/videos")),
            gcs_bucket=os.getenv("VEO_GCS_BUCKET"),
            log_level=os.getenv("VEO_LOG_LEVEL", "INFO"),
            log_format=os.getenv("VEO_LOG_FORMAT", "text")
        )


class VideoRequest(BaseModel):
    """Request model for video generation."""
    
    prompt: str = Field(..., min_length=10, max_length=10000, description="Video generation prompt")
    image_path: Optional[Path] = Field(None, description="Path to input image")
    
    # Video Settings
    aspect_ratio: AspectRatio = Field(AspectRatio.LANDSCAPE, description="Video aspect ratio")
    duration: int = Field(8, ge=1, le=8, description="Video duration in seconds")
    number_of_videos: int = Field(1, ge=1, le=4, description="Number of videos to generate")
    person_generation: PersonGeneration = Field(PersonGeneration.ALLOW_ADULT, description="Person generation setting")
    
    # Enhancement
    enhance_prompt: bool = Field(True, description="Whether to enhance the prompt")
    
    # Output
    output_gcs_uri: Optional[str] = Field(None, description="GCS URI for output")
    output_filename: Optional[str] = Field(None, description="Custom output filename")
    
    @validator('image_path')
    def validate_image_path(cls, v):
        """Validate image path exists if provided."""
        if v and not v.exists():
            raise ValueError(f"Image file not found: {v}")
        return v
    
    @validator('output_gcs_uri')
    def validate_gcs_uri(cls, v):
        """Validate GCS URI format."""
        if v and not v.startswith("gs://"):
            raise ValueError("GCS URI must start with 'gs://'")
        return v
