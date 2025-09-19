# Scripts VEO

Este diretório contém scripts utilitários para o projeto VEO.

## 📊 Análise de Código

### `code_analysis.py`

Script de análise de código que gera relatórios detalhados sobre a qualidade do código Python.

**Uso:**
```bash
# Via Makefile (recomendado)
make analyze-code

# Ou diretamente
python scripts/code_analysis.py
```

**Funcionalidades:**
- ✅ Análise de arquivos Python
- ✅ Contagem de classes e funções
- ✅ Verificação de documentação (docstrings)
- ✅ Análise de type hints
- ✅ Detecção de problemas de performance
- ✅ Verificação de segurança
- ✅ Análise de estrutura de diretórios
- ✅ Relatório de dependências

**Métricas Analisadas:**
- 📁 **Arquivos**: Total, por tipo, por tamanho
- 🏗️ **Classes**: Total, documentação, type hints, métodos async
- 🔧 **Funções**: Total, documentação, type hints, comprimento
- 📦 **Imports**: Google, Torch, Pandas, Numpy, externos, internos
- 📚 **Dependências**: Análise do requirements.txt
- ⚠️ **Problemas**: Nomenclatura, performance, segurança, estrutura

**Exemplo de Saída:**
```
📊 ANÁLISE DE CÓDIGO VEO 2025
============================

📁 ARQUIVOS
==========
Total de arquivos analisados: 9
Por tipo:
  .py: 9
Por tamanho:
  Pequenos (<50 linhas): 1
  Médios (50-200 linhas): 3
  Grandes (200-500 linhas): 5
  Muito grandes (>500 linhas): 0

🏗️ CLASSES
==========
Total de classes: 10
Com docstrings: 10
Com type hints: 10
Com métodos async: 6
Taxa de documentação: 100.0%
```

## 🎯 Gerenciamento de Prompts

### `prompt_manager.py`

Script para gerenciar prompts de geração de vídeo.

**Uso:**
```bash
# Listar prompts
python scripts/prompt_manager.py list

# Mostrar prompt específico
python scripts/prompt_manager.py show interbox_emotivo

# Gerar vídeo a partir de prompt
python scripts/prompt_manager.py generate interbox_emotivo

# Criar novo prompt
python scripts/prompt_manager.py create meu_prompt --content "Conteúdo do prompt"
```

## 🚀 Comandos Makefile

Todos os scripts podem ser executados via Makefile:

```bash
# Análise de código
make analyze-code

# Gerenciamento de prompts
make prompts
make show-prompt PROMPT=interbox_emotivo
make generate-prompt PROMPT=interbox_emotivo
make create-prompt NAME=meu_prompt CONTENT="Conteúdo"
make batch-prompts
```

## 📋 Requisitos

- Python 3.8+
- Dependências do projeto (requirements.txt)
- Acesso aos diretórios do projeto

## 🔧 Configuração

Os scripts usam as configurações padrão do projeto VEO. Para personalizar:

1. Edite as constantes no início do `code_analysis.py`
2. Ajuste os diretórios de análise
3. Modifique os critérios de avaliação

## 📈 Interpretação dos Resultados

### Classificação de Arquivos
- **Pequenos**: <50 linhas (✅ Bom)
- **Médios**: 50-200 linhas (✅ Ideal)
- **Grandes**: 200-500 linhas (⚠️ Atenção)
- **Muito grandes**: >500 linhas (❌ Refatorar)

### Taxa de Documentação
- **100%**: Excelente (✅)
- **80-99%**: Muito bom (✅)
- **60-79%**: Bom (⚠️)
- **<60%**: Precisa melhorar (❌)

### Problemas Comuns
- **Performance**: `print()` em produção, loops ineficientes
- **Segurança**: `eval()`, `exec()`, validação insuficiente
- **Estrutura**: Arquivos muito grandes, organização inadequada
- **Nomenclatura**: Convenções não seguidas

## 🎯 Objetivos de Qualidade

- ✅ Taxa de documentação > 80%
- ✅ Arquivos < 500 linhas
- ✅ Funções < 50 linhas
- ✅ Zero problemas de segurança
- ✅ Nomenclatura consistente
- ✅ Type hints em 100% das funções públicas
