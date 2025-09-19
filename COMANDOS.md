# 🚀 VEO - Guia Completo de Comandos

**Referência rápida para todos os comandos do sistema VEO.**

## 📋 **ÍNDICE**

- [Comandos Principais](#comandos-principais)
- [Gerenciamento de Prompts](#gerenciamento-de-prompts)
- [Comandos Make](#comandos-make)
- [Exemplos Práticos](#exemplos-práticos)
- [Troubleshooting](#troubleshooting)

---

## 🎬 **COMANDOS PRINCIPAIS**

### **Gerar Vídeo Simples**
```bash
# Geração básica
python main.py generate "Seu prompt aqui"

# Com parâmetros específicos
python main.py generate "Seu prompt aqui" --aspect 16:9 --duration 8 --count 2

# Com imagem
python main.py generate "Seu prompt aqui" --image input/sua_imagem.jpg

# Modo verbose (logs detalhados)
python main.py generate "Seu prompt aqui" --verbose
```

### **Geração em Lote**
```bash
# Criar arquivo de prompts
echo "Prompt 1" > prompts.txt
echo "Prompt 2" >> prompts.txt
echo "Prompt 3" >> prompts.txt

# Gerar vídeos em lote
python main.py batch prompts.txt --count 2 --max-concurrent 3
```

### **Configuração e Status**
```bash
# Ver configuração atual
python main.py config

# Limpar arquivos antigos
python main.py cleanup --days 7

# Dry run (ver o que seria deletado)
python main.py cleanup --days 7 --dry-run
```

---

## 📝 **GERENCIAMENTO DE PROMPTS**

### **Listar Prompts**
```bash
# Listar todos os prompts
python scripts/prompt_manager.py list

# Listar por categoria
python scripts/prompt_manager.py list --category projects
python scripts/prompt_manager.py list --category templates
python scripts/prompt_manager.py list --category examples
```

### **Visualizar Prompts**
```bash
# Ver conteúdo de um prompt
python scripts/prompt_manager.py show prompts/examples/example_sunset.txt
python scripts/prompt_manager.py show prompts/projects/meu_projeto.txt
python scripts/prompt_manager.py show prompts/templates/_cyberpunk.txt
```

### **Criar Prompts**
```bash
# Criar prompt simples
python scripts/prompt_manager.py create "meu_prompt" --content "Seu prompt aqui" --category projects

# Criar template
python scripts/prompt_manager.py create "_meu_template" --content "Template com {variavel}" --category templates

# Criar exemplo
python scripts/prompt_manager.py create "example_meu_exemplo" --content "Exemplo de prompt" --category examples
```

### **Gerar Vídeos a Partir de Prompts**
```bash
# Gerar vídeo de um prompt específico
python scripts/prompt_manager.py generate prompts/examples/example_sunset.txt

# Com parâmetros personalizados
python scripts/prompt_manager.py generate prompts/projects/meu_projeto.txt --aspect 9:16 --duration 6 --count 3

# Gerar todos os prompts de uma categoria
python scripts/prompt_manager.py batch --category projects --count 2
python scripts/prompt_manager.py batch --category examples --count 1
```

---

## ⚙️ **COMANDOS MAKE**

### **Setup e Instalação**
```bash
# Instalar dependências
make install

# Instalar dependências de desenvolvimento
make dev-install

# Setup completo (cria .env, instala deps)
make setup

# Limpar arquivos temporários
make clean
```

### **Desenvolvimento**
```bash
# Executar testes
make test

# Formatar código
make format

# Lint do código
make lint

# Teste rápido
make quick-test
```

### **Geração de Vídeos**
```bash
# Gerar vídeo de exemplo
make generate

# Gerar vídeos em lote de exemplo
make batch

# Executar CLI
make run
```

### **Gerenciamento de Prompts**
```bash
# Listar prompts
make prompts

# Mostrar prompt específico
make show-prompt PROMPT=prompts/examples/example_sunset.txt

# Criar novo prompt
make create-prompt NAME="meu_prompt" CONTENT="Seu prompt aqui"

# Gerar vídeo de prompt
make generate-prompt PROMPT=prompts/projects/interbox_emotivo.txt

# Gerar vídeos em lote
make batch-prompts
```

---

## 🎯 **EXEMPLOS PRÁTICOS**

### **Workflow Completo**
```bash
# 1. Setup inicial
make setup

# 2. Verificar configuração
python main.py config

# 3. Listar prompts disponíveis
python scripts/prompt_manager.py list

# 4. Ver um prompt específico
python scripts/prompt_manager.py show prompts/examples/example_sunset.txt

# 5. Gerar vídeo
python scripts/prompt_manager.py generate prompts/examples/example_sunset.txt

# 6. Gerar vídeos em lote
python scripts/prompt_manager.py batch --category projects --count 2
```

### **Criar Novo Projeto**
```bash
# 1. Criar prompt do projeto
python scripts/prompt_manager.py create "meu_novo_projeto" --content "Seu prompt detalhado aqui" --category projects

# 2. Verificar o prompt criado
python scripts/prompt_manager.py show prompts/projects/meu_novo_projeto.txt

# 3. Gerar vídeos do projeto
python scripts/prompt_manager.py generate prompts/projects/meu_novo_projeto.txt --count 1

# 4. Limpar arquivos antigos
python main.py cleanup --days 7
```

### **Desenvolvimento e Testes**
```bash
# 1. Instalar dependências de desenvolvimento
make dev-install

# 2. Executar testes
make test

# 3. Formatar código
make format

# 4. Verificar lint
make lint

# 5. Teste rápido
make quick-test
```

---

## 🔧 **TROUBLESHOOTING**

### **Problemas Comuns**

#### **Erro de API Key**
```bash
# Verificar configuração
python main.py config

# Se API Key não estiver configurada:
# Editar arquivo .env e adicionar:
# GOOGLE_API_KEY=sua_chave_aqui
```

#### **Erro de Permissão**
```bash
# Verificar permissões do diretório
ls -la output/

# Corrigir permissões se necessário
chmod 755 output/
```

#### **Erro de Dependências**
```bash
# Reinstalar dependências
make clean
make install

# Ou instalar manualmente
pip install -r requirements.txt
```

#### **Erro de Prompts**
```bash
# Verificar se o arquivo existe
python scripts/prompt_manager.py list

# Verificar conteúdo do prompt
python scripts/prompt_manager.py show prompts/examples/example_sunset.txt
```

### **Comandos de Debug**

```bash
# Modo verbose para debug
python main.py generate "teste" --verbose

# Ver logs detalhados
python scripts/prompt_manager.py generate prompts/examples/example_sunset.txt --verbose

# Verificar configuração
python main.py config
```

---

## 📚 **ESTRUTURA DE ARQUIVOS**

```
VEO/
├── main.py                    # Entry point principal
├── scripts/
│   └── prompt_manager.py     # Gerenciador de prompts
├── prompts/
│   ├── templates/            # Templates reutilizáveis
│   ├── projects/             # Seus projetos
│   └── examples/             # Exemplos
├── output/
│   └── videos/               # Vídeos gerados
├── input/                    # Imagens de entrada
├── veo/                      # Código principal
├── tests/                    # Testes
├── .env                      # Configurações
├── requirements.txt          # Dependências
├── Makefile                  # Comandos make
└── COMANDOS.md              # Este arquivo
```

---

## 🚀 **DICAS RÁPIDAS**

### **Performance**
- Use `--max-concurrent` para controlar concorrência
- Use `--count` para gerar múltiplos vídeos por prompt
- Use `cleanup` regularmente para limpar arquivos antigos

### **Organização**
- Organize prompts por projeto em `prompts/projects/`
- Use templates em `prompts/templates/` para reutilização
- Documente seus prompts com comentários

### **Desenvolvimento**
- Use `make format` antes de commitar
- Use `make test` para verificar funcionalidade
- Use `--verbose` para debug detalhado

---

## 📞 **SUPORTE**

Se encontrar problemas:

1. **Verifique os logs** com `--verbose`
2. **Execute testes** com `make test`
3. **Verifique configuração** com `python main.py config`
4. **Consulte este guia** para comandos corretos

---

**Feito com ❤️ por Mellø**
