import os
import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def check_operation_status(operation_id):
    """Verifica o status da operação do VEO."""
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    location_id = "us-central1"
    api_endpoint = f"https://{location_id}-aiplatform.googleapis.com"
    
    try:
        access_token = os.popen("gcloud auth print-access-token").read().strip()
    except Exception as e:
        print(f"Erro ao obter token de acesso: {str(e)}")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Tenta diferentes endpoints para verificar o status
    endpoints = [
        f"{api_endpoint}/v1/projects/{project_id}/locations/{location_id}/operations/{operation_id}",
        f"{api_endpoint}/v1/projects/{project_id}/locations/{location_id}/publishers/google/models/veo-2.0-generate-001/operations/{operation_id}"
    ]

    for endpoint in endpoints:
        print(f"\nTentando endpoint: {endpoint}")
        response = requests.get(endpoint, headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Resposta: {response.text[:500]}...")  # Mostra os primeiros 500 caracteres

if __name__ == "__main__":
    # Substitua pelo ID da operação que você recebeu
    operation_id = "82c43e02-8946-4c9e-bef3-5bfb48d3199a"
    check_operation_status(operation_id) 