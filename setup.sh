#!/bin/bash
# Script de setup para ambiente do projeto VEO

# Mostra a versão do Python
python --version

# Instala as dependências
pip install -r requirements.txt

# Executa os testes
pytest tests/ -v -s 