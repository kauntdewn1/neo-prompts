import os
import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def list_models():
    """Lista os modelos disponíveis no Vertex AI."""
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    if not project_id:
        raise ValueError("Nenhum GOOGLE_PROJECT_ID encontrado nas variáveis de ambiente")

    location_id = "us-central1"
    api_endpoint = f"https://{location_id}-aiplatform.googleapis.com"
    
    try:
        access_token = os.popen("gcloud auth print-access-token").read().strip()
    except Exception as e:
        raise ValueError(f"Erro ao obter token de acesso: {str(e)}")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Lista os modelos
    response = requests.get(
        f"{api_endpoint}/v1/projects/{project_id}/locations/{location_id}/models",
        headers=headers
    )

    if response.status_code == 200:
        models = response.json().get("models", [])
        print("\n📋 Modelos disponíveis:")
        for model in models:
            print(f"\nNome: {model.get('name')}")
            print(f"Versão: {model.get('versionId')}")
            print(f"Descrição: {model.get('description')}")
            print(f"Suporta geração de vídeo: {'generate-video' in model.get('supportedGenerationMethods', [])}")
            print("-" * 50)
    else:
        print(f"❌ Erro ao listar modelos: {response.text}")

if __name__ == "__main__":
    list_models() 