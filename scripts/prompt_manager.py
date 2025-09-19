#!/usr/bin/env python3
"""
Gerenciador de Prompts VEO
Facilita a criação, organização e uso de prompts.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import argparse
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from veo.models.config import VEOConfig
from veo.core.generator import VideoGenerator
from veo.utils.logger import setup_logger, get_logger


class PromptManager:
    """Gerenciador de prompts para VEO."""
    
    def __init__(self):
        self.prompts_dir = project_root / "prompts"
        self.logger = get_logger("prompt_manager")
        setup_logger()
    
    def list_prompts(self, category: str = "all") -> List[Path]:
        """Lista todos os prompts disponíveis."""
        prompts = []
        
        if category == "all":
            for subdir in ["templates", "projects", "examples"]:
                prompts.extend(self.prompts_dir.glob(f"{subdir}/*.txt"))
        else:
            prompts.extend(self.prompts_dir.glob(f"{category}/*.txt"))
        
        return sorted(prompts)
    
    def show_prompt(self, prompt_file: Path) -> str:
        """Mostra o conteúdo de um prompt."""
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            self.logger.error(f"Erro ao ler prompt: {e}")
            return ""
    
    def create_prompt(self, name: str, content: str, category: str = "projects") -> Path:
        """Cria um novo prompt."""
        category_dir = self.prompts_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        prompt_file = category_dir / f"{name}.txt"
        
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Prompt criado: {prompt_file}")
        return prompt_file
    
    def generate_from_prompt(self, prompt_file: Path, **kwargs) -> List[Path]:
        """Gera vídeo a partir de um prompt."""
        try:
            # Load configuration
            config = VEOConfig.from_env()
            generator = VideoGenerator(config)
            
            # Read prompt content
            prompt_content = self.show_prompt(prompt_file)
            
            # Extract prompt from content (remove markdown headers)
            lines = prompt_content.split('\n')
            prompt_lines = []
            in_prompt = False
            
            for line in lines:
                if line.startswith('#') and ('prompt' in line.lower() or 'cena' in line.lower()):
                    in_prompt = True
                    continue
                elif line.startswith('#') and in_prompt:
                    break
                elif in_prompt and line.strip():
                    prompt_lines.append(line.strip())
            
            if not prompt_lines:
                # If no structured prompt found, use the whole content
                prompt_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
            
            prompt_text = ' '.join(prompt_lines)
            
            if not prompt_text:
                raise ValueError("Nenhum prompt encontrado no arquivo")
            
            self.logger.info(f"Gerando vídeo com prompt: {prompt_text[:100]}...")
            
            # Generate video
            import asyncio
            video_paths = asyncio.run(generator.generate_from_prompt(
                prompt=prompt_text,
                **kwargs
            ))
            
            return video_paths
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar vídeo: {e}")
            raise
    
    def batch_generate(self, prompt_files: List[Path], **kwargs) -> List[List[Path]]:
        """Gera vídeos em lote a partir de múltiplos prompts."""
        try:
            # Load configuration
            config = VEOConfig.from_env()
            generator = VideoGenerator(config)
            
            # Read all prompts
            prompts = []
            for prompt_file in prompt_files:
                content = self.show_prompt(prompt_file)
                # Extract prompt text (simplified)
                lines = [line.strip() for line in content.split('\n') 
                        if line.strip() and not line.startswith('#')]
                prompt_text = ' '.join(lines)
                if prompt_text:
                    prompts.append(prompt_text)
            
            if not prompts:
                raise ValueError("Nenhum prompt válido encontrado")
            
            self.logger.info(f"Gerando {len(prompts)} vídeos em lote...")
            
            # Generate videos
            import asyncio
            all_video_paths = asyncio.run(generator.batch_generate_from_prompts(
                prompts=prompts,
                **kwargs
            ))
            
            return all_video_paths
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar vídeos em lote: {e}")
            raise


def main():
    """CLI para o gerenciador de prompts."""
    parser = argparse.ArgumentParser(description="Gerenciador de Prompts VEO")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # List command
    list_parser = subparsers.add_parser("list", help="Lista prompts disponíveis")
    list_parser.add_argument("--category", choices=["all", "templates", "projects", "examples"], 
                           default="all", help="Categoria de prompts")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Mostra conteúdo de um prompt")
    show_parser.add_argument("prompt_file", help="Arquivo de prompt")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Cria um novo prompt")
    create_parser.add_argument("name", help="Nome do prompt")
    create_parser.add_argument("--category", default="projects", 
                             choices=["templates", "projects", "examples"],
                             help="Categoria do prompt")
    create_parser.add_argument("--content", help="Conteúdo do prompt")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Gera vídeo a partir de prompt")
    generate_parser.add_argument("prompt_file", help="Arquivo de prompt")
    generate_parser.add_argument("--aspect", default="16:9", help="Proporção do vídeo")
    generate_parser.add_argument("--duration", type=int, default=8, help="Duração em segundos")
    generate_parser.add_argument("--count", type=int, default=1, help="Número de vídeos")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Gera vídeos em lote")
    batch_parser.add_argument("--category", default="projects", 
                            choices=["templates", "projects", "examples"],
                            help="Categoria de prompts")
    batch_parser.add_argument("--aspect", default="16:9", help="Proporção do vídeo")
    batch_parser.add_argument("--duration", type=int, default=8, help="Duração em segundos")
    batch_parser.add_argument("--count", type=int, default=1, help="Número de vídeos por prompt")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = PromptManager()
    
    try:
        if args.command == "list":
            prompts = manager.list_prompts(args.category)
            print(f"\n📝 Prompts disponíveis ({args.category}):")
            for prompt in prompts:
                print(f"  {prompt.relative_to(project_root)}")
        
        elif args.command == "show":
            prompt_file = Path(args.prompt_file)
            if not prompt_file.is_absolute():
                # Check if it's already a relative path from prompts/
                if prompt_file.parts[0] == "prompts":
                    prompt_file = project_root / prompt_file
                else:
                    prompt_file = project_root / "prompts" / prompt_file
            content = manager.show_prompt(prompt_file)
            print(f"\n📄 Conteúdo do prompt: {prompt_file.name}")
            print("-" * 50)
            print(content)
        
        elif args.command == "create":
            if not args.content:
                print("❌ Erro: --content é obrigatório para criar prompt")
                return
            
            prompt_file = manager.create_prompt(args.name, args.content, args.category)
            print(f"✅ Prompt criado: {prompt_file}")
        
        elif args.command == "generate":
            prompt_file = Path(args.prompt_file)
            
            # Add .txt extension if not present
            if not prompt_file.suffix:
                prompt_file = prompt_file.with_suffix('.txt')
            
            if not prompt_file.is_absolute():
                # Check if it's already a relative path from prompts/
                if prompt_file.parts[0] == "prompts":
                    prompt_file = project_root / prompt_file
                else:
                    # Try different possible paths
                    possible_paths = [
                        project_root / "prompts" / prompt_file,
                        project_root / "prompts" / "projects" / prompt_file,
                        project_root / "prompts" / "templates" / prompt_file,
                        project_root / "prompts" / "examples" / prompt_file
                    ]
                    
                    # Find the first existing path
                    prompt_file = None
                    for path in possible_paths:
                        if path.exists():
                            prompt_file = path
                            break
                    
                    if prompt_file is None:
                        raise FileNotFoundError(f"Prompt file not found: {args.prompt_file}")
            
            video_paths = manager.generate_from_prompt(
                prompt_file,
                aspect_ratio=args.aspect,
                duration=args.duration,
                number_of_videos=args.count
            )
            
            print(f"\n✅ Vídeo(s) gerado(s):")
            for i, path in enumerate(video_paths):
                print(f"  {i+1}. {path}")
        
        elif args.command == "batch":
            prompts = manager.list_prompts(args.category)
            if not prompts:
                print(f"❌ Nenhum prompt encontrado em {args.category}")
                return
            
            all_video_paths = manager.batch_generate(
                prompts,
                aspect_ratio=args.aspect,
                duration=args.duration,
                number_of_videos=args.count
            )
            
            print(f"\n✅ {len(all_video_paths)} lote(s) de vídeos gerados:")
            for i, video_paths in enumerate(all_video_paths):
                print(f"  Lote {i+1}: {len(video_paths)} vídeo(s)")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
