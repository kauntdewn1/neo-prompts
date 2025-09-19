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
    
    # API Configuration
    api_key: str = Field(..., description="Google API key")
    project_id: Optional[str] = Field(None, description="Google Cloud project ID")
    region: str = Field("us-central1", description="Google Cloud region")
    
    # Model Configuration
    model: str = Field("veo-3.0-generate-preview", description="VEO model to use")
    
    # Default Settings
    default_aspect_ratio: AspectRatio = Field(AspectRatio.LANDSCAPE, description="Default aspect ratio")
    default_duration: int = Field(8, ge=5, le=8, description="Default duration in seconds")
    default_number_of_videos: int = Field(1, ge=1, le=4, description="Default number of videos")
    default_person_generation: PersonGeneration = Field(PersonGeneration.ALLOW_ADULT, description="Default person generation")
    
    # Performance Settings
    max_concurrent_operations: int = Field(3, ge=1, le=10, description="Max concurrent operations")
    retry_attempts: int = Field(3, ge=1, le=10, description="Number of retry attempts")
    retry_delay: int = Field(30, ge=5, le=300, description="Delay between retries in seconds")
    
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
            api_key=os.getenv("GOOGLE_API_KEY", ""),
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
            region=os.getenv("GOOGLE_CLOUD_REGION", "us-central1"),
            model=os.getenv("VEO_MODEL", "veo-3.0-generate-preview"),
            default_aspect_ratio=AspectRatio(os.getenv("DEFAULT_ASPECT_RATIO", "16:9")),
            default_duration=int(os.getenv("DEFAULT_DURATION", "8")),
            default_number_of_videos=int(os.getenv("DEFAULT_NUMBER_OF_VIDEOS", "1")),
            default_person_generation=PersonGeneration(os.getenv("DEFAULT_PERSON_GENERATION", "allow_adult")),
            max_concurrent_operations=int(os.getenv("MAX_CONCURRENT_OPERATIONS", "3")),
            retry_attempts=int(os.getenv("RETRY_ATTEMPTS", "3")),
            retry_delay=int(os.getenv("RETRY_DELAY", "30")),
            output_dir=Path(os.getenv("OUTPUT_DIR", "output/videos")),
            gcs_bucket=os.getenv("GCS_BUCKET"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "text")
        )


class VideoRequest(BaseModel):
    """Request model for video generation."""
    
    prompt: str = Field(..., min_length=10, max_length=10000, description="Video generation prompt")
    image_path: Optional[Path] = Field(None, description="Path to input image")
    
    # Video Settings
    aspect_ratio: AspectRatio = Field(AspectRatio.LANDSCAPE, description="Video aspect ratio")
    duration: int = Field(8, ge=5, le=8, description="Video duration in seconds")
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
