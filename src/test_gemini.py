import os
import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def test_gemini():
    """Testa a API do Gemini."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Nenhuma GEMINI_API_KEY encontrada nas variáveis de ambiente")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Explique como a IA funciona em poucas palavras"
                    }
                ]
            }
        ]
    }

    print("\n🔄 Enviando requisição para o Gemini...")
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Resposta do Gemini:")
        print(result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", ""))
    else:
        print(f"\n❌ Erro na requisição: {response.text}")

if __name__ == "__main__":
    test_gemini() 