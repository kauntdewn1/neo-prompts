"""
Comprehensive tests for VEO video generation system.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import List

from veo.models.config import VEOConfig, VideoRequest, AspectRatio, PersonGeneration
from veo.core.client import VEOClient
from veo.core.generator import VideoGenerator


class TestVEOConfig:
    """Test VEO configuration."""
    
    def test_config_from_env(self):
        """Test configuration loading from environment variables."""
        with patch.dict('os.environ', {
            'GOOGLE_API_KEY': 'test_key',
            'GOOGLE_CLOUD_PROJECT': 'test_project',
            'DEFAULT_ASPECT_RATIO': '9:16',
            'DEFAULT_DURATION': '6'
        }):
            config = VEOConfig.from_env()
            
            assert config.api_key == 'test_key'
            assert config.project_id == 'test_project'
            assert config.default_aspect_ratio == AspectRatio.PORTRAIT
            assert config.default_duration == 6
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config
        config = VEOConfig(api_key="test_key")
        assert config.api_key == "test_key"
        
        # Invalid duration
        with pytest.raises(ValueError):
            VEOConfig(api_key="test_key", default_duration=10)
        
        # Invalid aspect ratio
        with pytest.raises(ValueError):
            VEOConfig(api_key="test_key", default_aspect_ratio="invalid")


class TestVideoRequest:
    """Test video request model."""
    
    def test_valid_request(self):
        """Test valid video request."""
        request = VideoRequest(
            prompt="A beautiful sunset",
            aspect_ratio=AspectRatio.LANDSCAPE,
            duration=8,
            number_of_videos=1
        )
        
        assert request.prompt == "A beautiful sunset"
        assert request.aspect_ratio == AspectRatio.LANDSCAPE
        assert request.duration == 8
        assert request.number_of_videos == 1
    
    def test_request_validation(self):
        """Test request validation."""
        # Invalid prompt length
        with pytest.raises(ValueError):
            VideoRequest(prompt="short")
        
        # Invalid duration
        with pytest.raises(ValueError):
            VideoRequest(prompt="A beautiful sunset", duration=10)
        
        # Invalid number of videos
        with pytest.raises(ValueError):
            VideoRequest(prompt="A beautiful sunset", number_of_videos=5)
    
    def test_image_path_validation(self):
        """Test image path validation."""
        # Non-existent image
        with pytest.raises(ValueError):
            VideoRequest(
                prompt="A beautiful sunset",
                image_path=Path("nonexistent.jpg")
            )
    
    def test_gcs_uri_validation(self):
        """Test GCS URI validation."""
        # Invalid GCS URI
        with pytest.raises(ValueError):
            VideoRequest(
                prompt="A beautiful sunset",
                output_gcs_uri="invalid_uri"
            )


class TestVEOClient:
    """Test VEO client functionality."""
    
    @pytest.fixture
    def config(self):
        """Test configuration."""
        return VEOConfig(api_key="test_key")
    
    @pytest.fixture
    def client(self, config):
        """Test VEO client."""
        with patch('veo.core.client.genai.Client'):
            return VEOClient(config)
    
    def test_client_initialization(self, config):
        """Test client initialization."""
        with patch('veo.core.client.genai.Client') as mock_client:
            client = VEOClient(config)
            assert client.config == config
            mock_client.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_video_async(self, client):
        """Test async video generation."""
        # Mock the client and operation
        mock_operation = Mock()
        mock_operation.done = True
        mock_operation.result.generated_videos = [
            Mock(video=Mock(uri="gs://test-bucket/video1.mp4")),
            Mock(video=Mock(uri="gs://test-bucket/video2.mp4"))
        ]
        
        client.client.models.generate_videos = Mock(return_value=mock_operation)
        client.client.operations.get = Mock(return_value=mock_operation)
        
        request = VideoRequest(prompt="Test video")
        result = await client.generate_video_async(request)
        
        assert len(result) == 2
        assert result[0] == "gs://test-bucket/video1.mp4"
        assert result[1] == "gs://test-bucket/video2.mp4"
    
    @pytest.mark.asyncio
    async def test_batch_generate_videos(self, client):
        """Test batch video generation."""
        # Mock individual generation
        with patch.object(client, 'generate_video_async', return_value=["video1.mp4", "video2.mp4"]):
            requests = [
                VideoRequest(prompt="Video 1"),
                VideoRequest(prompt="Video 2")
            ]
            
            results = await client.batch_generate_videos(requests, max_concurrent=2)
            
            assert len(results) == 2
            assert len(results[0]) == 2
            assert len(results[1]) == 2


class TestVideoGenerator:
    """Test video generator functionality."""
    
    @pytest.fixture
    def config(self):
        """Test configuration."""
        return VEOConfig(api_key="test_key", output_dir=Path("test_output"))
    
    @pytest.fixture
    def generator(self, config):
        """Test video generator."""
        with patch('veo.core.generator.VEOClient'):
            return VideoGenerator(config)
    
    @pytest.mark.asyncio
    async def test_generate_from_prompt(self, generator):
        """Test generation from prompt."""
        # Mock the client
        generator.client.generate_video_async = AsyncMock(return_value=["gs://test/video.mp4"])
        
        # Mock download
        with patch.object(generator, '_download_video', return_value=Path("test_output/video.mp4")):
            result = await generator.generate_from_prompt("Test prompt")
            
            assert len(result) == 1
            assert result[0] == Path("test_output/video.mp4")
    
    @pytest.mark.asyncio
    async def test_generate_from_image(self, generator):
        """Test generation from image."""
        # Create a temporary image file
        test_image = Path("test_image.jpg")
        test_image.touch()
        
        try:
            # Mock the client
            generator.client.generate_video_async = AsyncMock(return_value=["gs://test/video.mp4"])
            
            # Mock download
            with patch.object(generator, '_download_video', return_value=Path("test_output/video.mp4")):
                result = await generator.generate_from_image("Test prompt", test_image)
                
                assert len(result) == 1
                assert result[0] == Path("test_output/video.mp4")
        finally:
            # Clean up
            if test_image.exists():
                test_image.unlink()
    
    def test_cleanup_old_videos(self, generator):
        """Test cleanup of old videos."""
        # Create test output directory
        generator.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create some test files
        old_file = generator.config.output_dir / "old_video.mp4"
        old_file.touch()
        
        # Mock file modification time to be old
        import time
        old_time = time.time() - (8 * 24 * 60 * 60)  # 8 days ago
        old_file.touch()
        old_file.utime((old_time, old_time))
        
        try:
            removed_count = generator.cleanup_old_videos(days=7)
            assert removed_count == 1
            assert not old_file.exists()
        finally:
            # Clean up
            if old_file.exists():
                old_file.unlink()


class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_generation_flow(self):
        """Test complete video generation flow."""
        # This would be a more comprehensive integration test
        # that tests the entire flow from config to video generation
        pass


# Test utilities
def create_test_config(**kwargs):
    """Create test configuration with defaults."""
    defaults = {
        'api_key': 'test_key',
        'output_dir': Path('test_output')
    }
    defaults.update(kwargs)
    return VEOConfig(**defaults)


def create_test_request(**kwargs):
    """Create test video request with defaults."""
    defaults = {
        'prompt': 'A test video prompt that is long enough to pass validation',
        'aspect_ratio': AspectRatio.LANDSCAPE,
        'duration': 8,
        'number_of_videos': 1
    }
    defaults.update(kwargs)
    return VideoRequest(**defaults)
