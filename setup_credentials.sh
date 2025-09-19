#!/bin/bash

# Exporta a API Key como variável de ambiente
export GOOGLE_API_KEY="${GOOGLE_API_KEY:-your_api_key_here}"

# Opcional: salva no .env também
echo "GOOGLE_API_KEY=$GOOGLE_API_KEY" > .env

echo "✅ API Key configurada como variável de ambiente."
