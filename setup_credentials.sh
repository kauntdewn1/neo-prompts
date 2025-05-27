#!/bin/bash

# Exporta a API Key como variável de ambiente
export GOOGLE_API_KEY="AIzaSyBYVsQyXR8j6qUhPux8w_EpipssurAexbU"

# Opcional: salva no .env também
echo "GOOGLE_API_KEY=$GOOGLE_API_KEY" > .env

echo "✅ API Key configurada como variável de ambiente."
