import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import io

# Carrega variáveis de ambiente
load_dotenv()

def generate_video_from_image(
    prompt: str,
    image_path: str,
    aspect_ratio: str = "16:9",
    duration: int = 8,
    number_of_videos: int = 1,
    person_generation: str = "allow_adult",
    output_dir: str = "output/videos"
) -> str:
    """
    Gera um vídeo usando o VEO a partir de uma imagem.
    
    Args:
        prompt: Descrição do vídeo a ser gerado
        image_path: Caminho para a imagem de base
        aspect_ratio: Proporção do vídeo ("16:9" ou "9:16")
        duration: Duração em segundos (5-8)
        number_of_videos: Número de vídeos a gerar (1-4)
        person_generation: Configuração de geração de pessoas ("allow_adult" ou "dont_allow")
        output_dir: Diretório onde os vídeos serão salvos
    
    Returns:
        str: Caminho do arquivo de vídeo gerado
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY não encontrada nas variáveis de ambiente")

    # Verifica se a imagem existe
    if not os.path.exists(image_path):
        raise ValueError(f"Imagem não encontrada: {image_path}")

    # Cria o diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)

    # Configura o cliente
    client = genai.Client(api_key=api_key)
    
    # Define o modelo
    model_id = "veo-2.0-generate-001"
    
    print("\n🔄 Enviando requisição para o VEO...")
    print(f"Modelo: {model_id}")
    print(f"Prompt: {prompt}")
    print(f"Imagem: {image_path}")
    print(f"Configurações:")
    print(f"- Proporção: {aspect_ratio}")
    print(f"- Duração: {duration}s")
    print(f"- Número de vídeos: {number_of_videos}")
    print(f"- Diretório de saída: {output_dir}")
    
    try:
        # Lê e processa a imagem
        with Image.open(image_path) as img:
            # Converte para RGB se necessário
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Redimensiona se necessário (mantendo a proporção)
            max_size = 1024
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Converte para bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=95)
            image_bytes = img_byte_arr.getvalue()
        
        # Gera o vídeo
        operation = client.models.generate_videos(
            model=model_id,
            prompt=prompt,
            image=types.Image(image_bytes=image_bytes, mime_type="image/jpeg"),
            config=types.GenerateVideosConfig(
                person_generation=person_generation,
                aspect_ratio=aspect_ratio,
                number_of_videos=number_of_videos,
                duration_seconds=duration
            )
        )
        
        print("\n⏳ Aguardando a geração do vídeo...")
        
        # Monitora o progresso
        while not operation.done:
            time.sleep(20)
            operation = client.operations.get(operation)
            print(f"Status: {operation}")
        
        print("\n✅ Vídeo gerado com sucesso!")
        
        # Processa os vídeos gerados
        video_paths = []
        for n, generated_video in enumerate(operation.result.generated_videos):
            print(f"\nVídeo {n+1}:")
            print(f"URL: {generated_video.video.uri}")
            
            # Gera um nome único para o vídeo usando timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            video_path = os.path.join(output_dir, f'video_{timestamp}_{n}.mp4')
            
            # Baixa o vídeo
            client.files.download(file=generated_video.video)
            generated_video.video.save(video_path)
            print(f"Vídeo salvo em: {video_path}")
            video_paths.append(video_path)
        
        return video_paths[0] if len(video_paths) == 1 else video_paths
        
    except Exception as e:
        print(f"\n❌ Erro na requisição: {str(e)}")
        raise

if __name__ == "__main__":
    # Exemplo de uso
    prompt = "Uma escuridão verde profunda pulsa lentamente. No centro, um girassol digital dourado gira suavemente em silêncio, pétalas de luz fluida, como se respirassem. Cada movimento emite um leve brilho, sincronizado com uma frequência invisível. Surge a palavra: 'DESPERTA'. Logo abaixo: 'Movimento com propósito.' A câmera gira lentamente ao redor da mandala solar, revelando partículas no ar, como poeira cósmica. Nada mais existe - apenas energia, luz e intenção."
    image_path = "input/sunflowerdesperta.png"  # Coloque sua imagem aqui
    
    # Cria o diretório de input se não existir
    os.makedirs("input", exist_ok=True)
    
    video_path = generate_video_from_image(
        prompt=prompt,
        image_path=image_path,
        aspect_ratio="9:16",
        duration=8,
        number_of_videos=1,
        output_dir="output/videos"
    )
    print(f"\n🎥 Vídeo gerado: {video_path}") 