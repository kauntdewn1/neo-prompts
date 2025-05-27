import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Carrega variáveis de ambiente
load_dotenv()

def test_veo():
    """Testa a API do VEO usando a biblioteca google-genai."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY não encontrada nas variáveis de ambiente")

    # Configura o cliente
    client = genai.Client(api_key=api_key)
    
    # Define o modelo
    model_id = "veo-2.0-generate-001"
    
    # Prepara o prompt
    prompt = "Um gato dançando break dance em uma rua movimentada"
    
    print("\n🔄 Enviando requisição para o VEO...")
    print(f"Modelo: {model_id}")
    print(f"Prompt: {prompt}")
    
    try:
        # Gera o vídeo
        operation = client.models.generate_videos(
            model=model_id,
            prompt=prompt,
            config=types.GenerateVideosConfig(
                person_generation="allow_adult",
                aspect_ratio="16:9",
                number_of_videos=1,
                duration_seconds=8
            )
        )
        
        print("\n⏳ Aguardando a geração do vídeo...")
        
        # Monitora o progresso
        while not operation.done:
            time.sleep(20)
            operation = client.operations.get(operation)
            print(f"Status: {operation}")
        
        print("\n✅ Vídeo gerado com sucesso!")
        print("\nVídeos gerados:")
        for n, generated_video in enumerate(operation.result.generated_videos):
            print(f"\nVídeo {n+1}:")
            print(f"URL: {generated_video.video.uri}")
            
            # Baixa o vídeo
            video_path = f'video{n}.mp4'
            client.files.download(file=generated_video.video)
            generated_video.video.save(video_path)
            print(f"Vídeo salvo em: {video_path}")
        
    except Exception as e:
        print(f"\n❌ Erro na requisição: {str(e)}")

if __name__ == "__main__":
    test_veo() 