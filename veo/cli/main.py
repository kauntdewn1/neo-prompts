"""
VEO CLI - Modern command-line interface for video generation.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table

from ..models.config import VEOConfig, AspectRatio, PersonGeneration
from ..core.generator import VideoGenerator
from ..utils.logger import setup_logger, get_logger

# Initialize CLI
app = typer.Typer(
    name="veo",
    help="🚀 VEO - Modern Video Generation Engine",
    no_args_is_help=True
)
console = Console()


def create_progress_callback(progress: Progress, task_id):
    """Create progress callback for video generation."""
    def callback(operation):
        if hasattr(operation, 'metadata') and operation.metadata:
            # Extract progress info if available
            progress.update(task_id, advance=1)
    return callback


@app.command()
def generate(
    prompt: str = typer.Argument(..., help="Video generation prompt"),
    image: Optional[Path] = typer.Option(None, "--image", "-i", help="Input image path"),
    aspect_ratio: AspectRatio = typer.Option(AspectRatio.LANDSCAPE, "--aspect", "-a", help="Video aspect ratio"),
    duration: int = typer.Option(8, "--duration", "-d", help="Video duration (5-8 seconds)"),
    count: int = typer.Option(1, "--count", "-c", help="Number of videos to generate"),
    person_generation: PersonGeneration = typer.Option(PersonGeneration.ALLOW_ADULT, "--person", "-p", help="Person generation setting"),
    enhance: bool = typer.Option(True, "--enhance/--no-enhance", help="Enhance prompt automatically"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output filename"),
    config_file: Optional[Path] = typer.Option(None, "--config", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Generate video from prompt or image."""
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logger(level=log_level)
    logger = get_logger("veo.cli")
    
    try:
        # Load configuration
        if config_file and config_file.exists():
            # TODO: Implement config file loading
            config = VEOConfig.from_env()
        else:
            config = VEOConfig.from_env()
        
        # Validate API key
        if not config.api_key:
            console.print("[red]❌ Error: GOOGLE_API_KEY not found in environment variables[/red]")
            console.print("Please set your API key: export GOOGLE_API_KEY=your_key_here")
            raise typer.Exit(1)
        
        # Initialize generator
        generator = VideoGenerator(config)
        
        # Display generation info
        info_table = Table(title="🎬 Video Generation Parameters")
        info_table.add_column("Parameter", style="cyan")
        info_table.add_column("Value", style="green")
        
        info_table.add_row("Prompt", prompt[:50] + "..." if len(prompt) > 50 else prompt)
        info_table.add_row("Image", str(image) if image else "None")
        info_table.add_row("Aspect Ratio", aspect_ratio.value)
        info_table.add_row("Duration", f"{duration}s")
        info_table.add_row("Count", str(count))
        info_table.add_row("Person Generation", person_generation.value)
        info_table.add_row("Enhance Prompt", str(enhance))
        info_table.add_row("Output", output or "Auto-generated")
        
        console.print(Panel(info_table, title="🚀 VEO Generation", border_style="blue"))
        
        # Generate video
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Generating video...", total=100)
            
            if image:
                # Generate from image
                video_paths = asyncio.run(generator.generate_from_image(
                    prompt=prompt,
                    image_path=image,
                    aspect_ratio=aspect_ratio,
                    duration=duration,
                    number_of_videos=count,
                    person_generation=person_generation,
                    enhance_prompt=enhance,
                    output_filename=output
                ))
            else:
                # Generate from prompt only
                video_paths = asyncio.run(generator.generate_from_prompt(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    duration=duration,
                    number_of_videos=count,
                    person_generation=person_generation,
                    enhance_prompt=enhance,
                    output_filename=output
                ))
            
            progress.update(task, completed=100)
        
        # Display results
        console.print("\n[green]✅ Video generation completed![/green]")
        
        results_table = Table(title="📁 Generated Videos")
        results_table.add_column("Index", style="cyan")
        results_table.add_column("File Path", style="green")
        results_table.add_column("Size", style="yellow")
        
        for i, video_path in enumerate(video_paths):
            size = video_path.stat().st_size / (1024 * 1024)  # MB
            results_table.add_row(
                str(i + 1),
                str(video_path),
                f"{size:.1f} MB"
            )
        
        console.print(results_table)
        
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def batch(
    prompts_file: Path = typer.Argument(..., help="File containing prompts (one per line)"),
    aspect_ratio: AspectRatio = typer.Option(AspectRatio.LANDSCAPE, "--aspect", "-a", help="Video aspect ratio"),
    duration: int = typer.Option(8, "--duration", "-d", help="Video duration (5-8 seconds)"),
    count: int = typer.Option(1, "--count", "-c", help="Number of videos per prompt"),
    person_generation: PersonGeneration = typer.Option(PersonGeneration.ALLOW_ADULT, "--person", "-p", help="Person generation setting"),
    enhance: bool = typer.Option(True, "--enhance/--no-enhance", help="Enhance prompts automatically"),
    max_concurrent: int = typer.Option(3, "--max-concurrent", help="Maximum concurrent operations"),
    config_file: Optional[Path] = typer.Option(None, "--config", help="Configuration file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Generate videos from multiple prompts in batch."""
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logger(level=log_level)
    logger = get_logger("veo.cli")
    
    try:
        # Load configuration
        config = VEOConfig.from_env()
        
        # Validate API key
        if not config.api_key:
            console.print("[red]❌ Error: GOOGLE_API_KEY not found in environment variables[/red]")
            raise typer.Exit(1)
        
        # Load prompts
        if not prompts_file.exists():
            console.print(f"[red]❌ Error: Prompts file not found: {prompts_file}[/red]")
            raise typer.Exit(1)
        
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts = [line.strip() for line in f if line.strip()]
        
        if not prompts:
            console.print("[red]❌ Error: No prompts found in file[/red]")
            raise typer.Exit(1)
        
        console.print(f"[blue]📝 Loaded {len(prompts)} prompts from {prompts_file}[/blue]")
        
        # Initialize generator
        generator = VideoGenerator(config)
        
        # Generate videos
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task(f"Generating {len(prompts)} batches...", total=len(prompts))
            
            all_video_paths = asyncio.run(generator.batch_generate_from_prompts(
                prompts=prompts,
                aspect_ratio=aspect_ratio,
                duration=duration,
                number_of_videos=count,
                person_generation=person_generation,
                enhance_prompt=enhance,
                max_concurrent=max_concurrent
            ))
            
            progress.update(task, completed=len(prompts))
        
        # Display results
        total_videos = sum(len(paths) for paths in all_video_paths)
        console.print(f"\n[green]✅ Batch generation completed! Generated {total_videos} videos total.[/green]")
        
        # Show summary
        summary_table = Table(title="📊 Batch Generation Summary")
        summary_table.add_column("Prompt Index", style="cyan")
        summary_table.add_column("Prompt", style="white")
        summary_table.add_column("Videos Generated", style="green")
        
        for i, (prompt, video_paths) in enumerate(zip(prompts, all_video_paths)):
            summary_table.add_row(
                str(i + 1),
                prompt[:50] + "..." if len(prompt) > 50 else prompt,
                str(len(video_paths))
            )
        
        console.print(summary_table)
        
    except Exception as e:
        logger.error(f"Batch generation failed: {str(e)}")
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def cleanup(
    days: int = typer.Option(7, "--days", "-d", help="Remove files older than N days"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deleted without actually deleting"),
    config_file: Optional[Path] = typer.Option(None, "--config", help="Configuration file path")
):
    """Clean up old video files."""
    
    try:
        # Load configuration
        config = VEOConfig.from_env()
        
        # Initialize generator
        generator = VideoGenerator(config)
        
        if dry_run:
            console.print(f"[yellow]🔍 Dry run: Would remove files older than {days} days[/yellow]")
            # TODO: Implement dry run functionality
        else:
            removed_count = generator.cleanup_old_videos(days)
            console.print(f"[green]✅ Cleaned up {removed_count} old video files[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def config():
    """Show current configuration."""
    
    try:
        config = VEOConfig.from_env()
        
        config_table = Table(title="⚙️ VEO Configuration")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        
        config_table.add_row("API Key", "***" + config.api_key[-4:] if config.api_key else "Not set")
        config_table.add_row("Project ID", config.project_id or "Not set")
        config_table.add_row("Region", config.region)
        config_table.add_row("Model", config.model)
        config_table.add_row("Default Aspect Ratio", config.default_aspect_ratio.value)
        config_table.add_row("Default Duration", f"{config.default_duration}s")
        config_table.add_row("Default Videos", str(config.default_number_of_videos))
        config_table.add_row("Output Directory", str(config.output_dir))
        config_table.add_row("GCS Bucket", config.gcs_bucket or "Not set")
        config_table.add_row("Max Concurrent", str(config.max_concurrent_operations))
        config_table.add_row("Retry Attempts", str(config.retry_attempts))
        config_table.add_row("Log Level", config.log_level)
        
        console.print(config_table)
        
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
