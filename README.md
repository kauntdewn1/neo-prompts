# VEO - Geração de Vídeos com IA

Este projeto utiliza a API do Google VEO para gerar vídeos a partir de imagens e prompts textuais.

## Requisitos

- Python 3.8+
- Conta no Google Cloud com acesso à API do VEO
- Chave de API do Google

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/kauntdewn1/vertexai.git
cd vertexai
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Crie um arquivo `.env` na raiz do projeto com sua chave de API:
```
GOOGLE_API_KEY=sua_chave_aqui
```

## Uso

### Gerar vídeo a partir de uma imagem

1. Coloque sua imagem na pasta `input/`
2. Execute o script:
```bash
python scripts/generate_video_from_image.py
```

O vídeo gerado será salvo na pasta `output/videos/`.

### Configurações

Você pode personalizar a geração do vídeo ajustando os seguintes parâmetros:

- `prompt`: Descrição do vídeo a ser gerado
- `aspect_ratio`: Proporção do vídeo ("16:9" ou "9:16")
- `duration`: Duração em segundos (5-8)
- `number_of_videos`: Número de vídeos a gerar (1-4)
- `person_generation`: Configuração de geração de pessoas ("allow_adult" ou "dont_allow")

## Estrutura do Projeto

```
.
├── scripts/
│   ├── generate_video_from_image.py
│   └── generate_video.py
├── input/
│   └── (suas imagens aqui)
├── output/
│   └── videos/
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

## Licença

MIT 