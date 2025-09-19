# 📝 Sistema de Prompts VEO

Este diretório contém todos os prompts organizados para geração de vídeos.

## 📁 Estrutura

```
prompts/
├── templates/          # Templates reutilizáveis
├── projects/           # Prompts por projeto
├── examples/           # Exemplos de prompts
└── README.md          # Este arquivo
```

## 🚀 Como Usar

### 1. Prompts Simples

```bash
# Usar prompt direto
python main.py generate "Seu prompt aqui"

# Usar arquivo de prompt
python main.py generate --prompt-file prompts/projects/meu_projeto.txt
```

### 2. Batch Processing

```bash
# Gerar múltiplos vídeos
python main.py batch prompts/projects/lista_prompts.txt --count 2
```

### 3. Templates

```bash
# Usar template com variáveis
python main.py generate --template prompts/templates/cyberpunk.txt --vars "personagem=gato,acao=correndo"
```

## 📋 Convenções

- **Arquivos .txt**: Prompts simples
- **Arquivos .md**: Prompts com formatação
- **Arquivos .json**: Prompts com metadados
- **Prefixo _**: Templates (ex: _cyberpunk.txt)
- **Prefixo example_**: Exemplos (ex: example_sunset.txt)

## 🎯 Dicas

1. **Seja específico**: Descreva cenas, estilos, movimentos
2. **Use referências**: Mencione estilos visuais conhecidos
3. **Organize por projeto**: Crie pastas para cada projeto
4. **Documente**: Adicione comentários nos arquivos
5. **Teste**: Use exemplos para validar prompts
