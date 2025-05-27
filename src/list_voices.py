from google.cloud import texttospeech
from google.api_core.client_options import ClientOptions
import os
import pygame
import time

# Substitua aqui com sua API KEY real
api_key = "AIzaSyBYVsQyXR8j6qUhPux8w_EpipssurAexbU"

# Crie um cliente usando a API Key como parâmetro de endpoint
client_options = ClientOptions(api_key=api_key)
client = texttospeech.TextToSpeechClient(client_options=client_options)


# Lista todas as vozes disponíveis para português do Brasil
voices = client.list_voices(language_code="pt-BR")

print("Vozes disponíveis para português do Brasil:\n")
print("Nome | Gênero | Idiomas\n")
print("-" * 50)

for voice in voices.voices:
    print(f"{voice.name} | {voice.ssml_gender} | {', '.join(voice.language_codes)}")

def play_audio(file_path):
    """Reproduz um arquivo de áudio."""
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)

# Função para testar uma voz
def test_voice(voice_name, text):
    """Testa uma voz específica com um texto."""
    # Configuração da síntese
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="pt-BR",
        name=voice_name
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Realiza a síntese
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Salva o áudio
    output_file = f"teste_{voice_name}.mp3"
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
    
    print(f"\nÁudio salvo em: {output_file}")
    return output_file

# Testa uma voz específica
if __name__ == "__main__":
    texto_teste = "Olá! Este é um teste da voz do Google Cloud Text-to-Speech."
    arquivo_audio = test_voice("pt-BR-Standard-E", 'Fala meus recrutas')
    
    # Reproduz o áudio
    print("\nReproduzindo áudio...")
    play_audio(arquivo_audio) 