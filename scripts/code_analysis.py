#!/usr/bin/env python3
"""
Script de Análise de Código VEO
Analisa o código real do projeto e gera relatórios baseados no estado atual
"""

import os
import re
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

# Cores para output
class Colors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Configurações
CONFIG = {
    'src_dir': './veo',
    'exclude_dirs': ['__pycache__', '.git', 'node_modules', 'dist', 'coverage'],
    'file_extensions': ['.py'],
    'max_file_size': 500,  # linhas
    'max_function_length': 50,  # linhas
    'max_class_length': 200,  # linhas
}

@dataclass
class Issue:
    file: str
    issue: str
    suggestion: str
    severity: str = 'warning'

class CodeAnalyzer:
    def __init__(self):
        self.stats = {
            'files': {
                'total': 0,
                'by_type': defaultdict(int),
                'by_size': {'small': 0, 'medium': 0, 'large': 0, 'xlarge': 0}
            },
            'classes': {
                'total': 0,
                'with_docstrings': 0,
                'with_type_hints': 0,
                'with_async_methods': 0
            },
            'functions': {
                'total': 0,
                'long': 0,
                'with_docstrings': 0,
                'with_type_hints': 0,
                'async': 0
            },
            'imports': {
                'google': 0,
                'torch': 0,
                'pandas': 0,
                'numpy': 0,
                'external': 0,
                'internal': 0
            },
            'issues': {
                'naming': [],
                'performance': [],
                'security': [],
                'structure': [],
                'documentation': []
            }
        }

    def log(self, message: str, color: str = 'white') -> None:
        """Log com cores"""
        color_code = getattr(Colors, color.upper(), Colors.WHITE)
        print(f"{color_code}{message}{Colors.RESET}")

    def log_section(self, title: str) -> None:
        """Log de seção com formatação"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{title}{Colors.RESET}")
        print(f"{Colors.YELLOW}{'=' * len(title)}{Colors.RESET}")

    def log_success(self, message: str) -> None:
        self.log(f"✓ {message}", 'green')

    def log_warning(self, message: str) -> None:
        self.log(f"⚠ {message}", 'yellow')

    def log_error(self, message: str) -> None:
        self.log(f"✗ {message}", 'red')

    def get_all_files(self, directory: str) -> List[str]:
        """Recupera todos os arquivos Python do diretório"""
        files = []
        
        for root, dirs, filenames in os.walk(directory):
            # Remove diretórios excluídos
            dirs[:] = [d for d in dirs if d not in CONFIG['exclude_dirs']]
            
            for filename in filenames:
                if any(filename.endswith(ext) for ext in CONFIG['file_extensions']):
                    files.append(os.path.join(root, filename))
        
        return files

    def analyze_file(self, file_path: str) -> None:
        """Analisa um arquivo Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            file_name = os.path.basename(file_path)
            file_type = os.path.splitext(file_name)[1]
            
            self.stats['files']['total'] += 1
            self.stats['files']['by_type'][file_type] += 1
            
            # Classificar por tamanho
            line_count = len(lines)
            if line_count < 50:
                self.stats['files']['by_size']['small'] += 1
            elif line_count < 200:
                self.stats['files']['by_size']['medium'] += 1
            elif line_count < 500:
                self.stats['files']['by_size']['large'] += 1
            else:
                self.stats['files']['by_size']['xlarge'] += 1
            
            # Análise específica
            self.analyze_classes(content, file_path)
            self.analyze_functions(content, file_path)
            self.analyze_imports(content)
            self.analyze_issues(content, file_path, line_count)
            
        except Exception as e:
            self.log_error(f"Erro ao analisar {file_path}: {str(e)}")

    def analyze_classes(self, content: str, file_path: str) -> None:
        """Analisa classes Python"""
        class_pattern = r'^class\s+(\w+).*:'
        classes = re.findall(class_pattern, content, re.MULTILINE)
        
        for class_name in classes:
            self.stats['classes']['total'] += 1
            
            # Verificar docstring
            if f'class {class_name}' in content:
                class_start = content.find(f'class {class_name}')
                class_section = content[class_start:class_start + 500]
                if '"""' in class_section or "'''" in class_section:
                    self.stats['classes']['with_docstrings'] += 1
            
            # Verificar type hints
            if '->' in content or ':' in content:
                self.stats['classes']['with_type_hints'] += 1
            
            # Verificar métodos async
            if 'async def' in content:
                self.stats['classes']['with_async_methods'] += 1

    def analyze_functions(self, content: str, file_path: str) -> None:
        """Analisa funções Python"""
        function_pattern = r'^def\s+(\w+).*:'
        functions = re.findall(function_pattern, content, re.MULTILINE)
        
        for func_name in functions:
            self.stats['functions']['total'] += 1
            
            # Verificar se é async
            if f'async def {func_name}' in content:
                self.stats['functions']['async'] += 1
            
            # Verificar docstring
            if f'def {func_name}' in content:
                func_start = content.find(f'def {func_name}')
                func_section = content[func_start:func_start + 200]
                if '"""' in func_section or "'''" in func_section:
                    self.stats['functions']['with_docstrings'] += 1
            
            # Verificar type hints
            if '->' in content or ':' in content:
                self.stats['functions']['with_type_hints'] += 1
            
            # Verificar se é muito longa
            if self.get_function_length(content, func_name) > CONFIG['max_function_length']:
                self.stats['functions']['long'] += 1

    def get_function_length(self, content: str, func_name: str) -> int:
        """Calcula o comprimento de uma função"""
        pattern = rf'^def\s+{func_name}.*:\n(.*?)(?=^def|\Z)'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            return len(match.group(1).split('\n'))
        return 0

    def analyze_imports(self, content: str) -> None:
        """Analisa imports"""
        import_lines = [line for line in content.split('\n') if line.strip().startswith('import') or line.strip().startswith('from')]
        
        for line in import_lines:
            if 'google' in line:
                self.stats['imports']['google'] += 1
            elif 'torch' in line:
                self.stats['imports']['torch'] += 1
            elif 'pandas' in line:
                self.stats['imports']['pandas'] += 1
            elif 'numpy' in line:
                self.stats['imports']['numpy'] += 1
            elif 'from ..' in line or 'from .' in line:
                self.stats['imports']['internal'] += 1
            else:
                self.stats['imports']['external'] += 1

    def analyze_issues(self, content: str, file_path: str, line_count: int) -> None:
        """Analisa problemas no código"""
        file_name = os.path.basename(file_path)
        
        # Problemas de nomenclatura
        if file_name != file_name.lower() and not file_name.startswith('__'):
            self.stats['issues']['naming'].append(Issue(
                file=file_path,
                issue='Nome de arquivo não segue snake_case',
                suggestion='Renomeie para snake_case (ex: my_module.py)'
            ))
        
        # Problemas de performance
        if 'print(' in content and 'console.print(' not in content and 'test' not in file_path:
            self.stats['issues']['performance'].append(Issue(
                file=file_path,
                issue='print() encontrado em código de produção',
                suggestion='Use o sistema de logging apropriado'
            ))
        
        # Problemas de segurança
        if 'eval(' in content or 'exec(' in content:
            self.stats['issues']['security'].append(Issue(
                file=file_path,
                issue='Uso de eval() ou exec() detectado',
                suggestion='Evite eval() e exec() por questões de segurança'
            ))
        
        # Problemas de estrutura
        if line_count > CONFIG['max_file_size']:
            self.stats['issues']['structure'].append(Issue(
                file=file_path,
                issue=f'Arquivo muito grande ({line_count} linhas)',
                suggestion='Considere quebrar em arquivos menores'
            ))
        
        # Problemas de documentação
        if not any(keyword in content for keyword in ['"""', "'''", '# TODO', '# FIXME']):
            self.stats['issues']['documentation'].append(Issue(
                file=file_path,
                issue='Falta de documentação',
                suggestion='Adicione docstrings e comentários'
            ))

    def analyze_dependencies(self) -> Optional[Dict[str, Any]]:
        """Analisa dependências do requirements.txt"""
        try:
            with open('requirements.txt', 'r') as f:
                content = f.read()
            
            dependencies = [line.split('==')[0].split('>=')[0].split('<=')[0] 
                          for line in content.split('\n') if line.strip() and not line.startswith('#')]
            
            return {
                'total': len(dependencies),
                'google': any('google' in dep for dep in dependencies),
                'torch': any('torch' in dep for dep in dependencies),
                'pandas': any('pandas' in dep for dep in dependencies),
                'numpy': any('numpy' in dep for dep in dependencies),
                'dependencies': dependencies
            }
        except FileNotFoundError:
            self.log_error("requirements.txt não encontrado")
            return None

    def analyze_structure(self) -> Dict[str, Any]:
        """Analisa estrutura de diretórios"""
        structure = {}
        
        for root, dirs, files in os.walk('.'):
            if any(exclude in root for exclude in CONFIG['exclude_dirs']):
                continue
            
            rel_path = os.path.relpath(root, '.')
            if rel_path == '.':
                continue
            
            py_files = [f for f in files if f.endswith('.py')]
            if py_files:
                structure[rel_path] = {
                    'files': len(py_files),
                    'directories': len(dirs)
                }
        
        return structure

    def generate_report(self) -> None:
        """Gera relatório completo"""
        self.log_section('📊 ANÁLISE DE CÓDIGO VEO 2025')
        
        self.report_files()
        self.report_classes()
        self.report_functions()
        self.report_imports()
        self.report_dependencies()
        self.report_structure()
        self.report_issues()
        self.report_recommendations()

    def report_files(self) -> None:
        """Relatório de arquivos"""
        self.log_section('📁 ARQUIVOS')
        self.log(f"Total de arquivos analisados: {self.stats['files']['total']}", 'white')
        
        self.log('\nPor tipo:', 'yellow')
        for file_type, count in self.stats['files']['by_type'].items():
            self.log(f"  {file_type}: {count}", 'cyan')
        
        self.log('\nPor tamanho:', 'yellow')
        self.log(f"  Pequenos (<50 linhas): {self.stats['files']['by_size']['small']}", 'green')
        self.log(f"  Médios (50-200 linhas): {self.stats['files']['by_size']['medium']}", 'yellow')
        self.log(f"  Grandes (200-500 linhas): {self.stats['files']['by_size']['large']}", 'orange')
        self.log(f"  Muito grandes (>500 linhas): {self.stats['files']['by_size']['xlarge']}", 'red')

    def report_classes(self) -> None:
        """Relatório de classes"""
        self.log_section('🏗️ CLASSES')
        self.log(f"Total de classes: {self.stats['classes']['total']}", 'white')
        self.log(f"Com docstrings: {self.stats['classes']['with_docstrings']}", 'cyan')
        self.log(f"Com type hints: {self.stats['classes']['with_type_hints']}", 'cyan')
        self.log(f"Com métodos async: {self.stats['classes']['with_async_methods']}", 'cyan')
        
        if self.stats['classes']['total'] > 0:
            docstring_rate = (self.stats['classes']['with_docstrings'] / self.stats['classes']['total']) * 100
            self.log(f"Taxa de documentação: {docstring_rate:.1f}%", 'yellow')

    def report_functions(self) -> None:
        """Relatório de funções"""
        self.log_section('🔧 FUNÇÕES')
        self.log(f"Total de funções: {self.stats['functions']['total']}", 'white')
        self.log(f"Async: {self.stats['functions']['async']}", 'cyan')
        self.log(f"Com docstrings: {self.stats['functions']['with_docstrings']}", 'cyan')
        self.log(f"Com type hints: {self.stats['functions']['with_type_hints']}", 'cyan')
        self.log(f"Muito longas: {self.stats['functions']['long']}", 'red')
        
        if self.stats['functions']['total'] > 0:
            docstring_rate = (self.stats['functions']['with_docstrings'] / self.stats['functions']['total']) * 100
            self.log(f"Taxa de documentação: {docstring_rate:.1f}%", 'yellow')

    def report_imports(self) -> None:
        """Relatório de imports"""
        self.log_section('📦 IMPORTS')
        self.log(f"Google: {self.stats['imports']['google']}", 'cyan')
        self.log(f"Torch: {self.stats['imports']['torch']}", 'cyan')
        self.log(f"Pandas: {self.stats['imports']['pandas']}", 'cyan')
        self.log(f"Numpy: {self.stats['imports']['numpy']}", 'cyan')
        self.log(f"Externos: {self.stats['imports']['external']}", 'cyan')
        self.log(f"Internos: {self.stats['imports']['internal']}", 'cyan')

    def report_dependencies(self) -> None:
        """Relatório de dependências"""
        deps = self.analyze_dependencies()
        if not deps:
            return
        
        self.log_section('📚 DEPENDÊNCIAS')
        self.log(f"Total: {deps['total']}", 'white')
        
        self.log('\nTecnologias principais:', 'yellow')
        self.log(f"  Google: {'✓' if deps['google'] else '✗'}", 'green' if deps['google'] else 'red')
        self.log(f"  Torch: {'✓' if deps['torch'] else '✗'}", 'green' if deps['torch'] else 'red')
        self.log(f"  Pandas: {'✓' if deps['pandas'] else '✗'}", 'green' if deps['pandas'] else 'red')
        self.log(f"  Numpy: {'✓' if deps['numpy'] else '✗'}", 'green' if deps['numpy'] else 'red')

    def report_structure(self) -> None:
        """Relatório de estrutura"""
        structure = self.analyze_structure()
        
        self.log_section('🏗️ ESTRUTURA')
        for path, info in structure.items():
            self.log(f"{path}/: {info['files']} arquivos, {info['directories']} diretórios", 'cyan')

    def report_issues(self) -> None:
        """Relatório de problemas"""
        total_issues = sum(len(issues) for issues in self.stats['issues'].values())
        
        self.log_section('⚠️ PROBLEMAS ENCONTRADOS')
        self.log(f"Total: {total_issues}", 'red' if total_issues > 0 else 'green')
        
        for category, issues in self.stats['issues'].items():
            if issues:
                self.log(f"\n{category.title()} ({len(issues)}):", 'yellow')
                for issue in issues:
                    self.log(f"  {issue.file}: {issue.issue}", 'red')
                    self.log(f"    → {issue.suggestion}", 'cyan')

    def report_recommendations(self) -> None:
        """Relatório de recomendações"""
        self.log_section('💡 RECOMENDAÇÕES')
        
        recommendations = []
        
        # Recomendações baseadas nos dados
        if self.stats['classes']['with_docstrings'] < self.stats['classes']['total'] * 0.5:
            recommendations.append('Documente mais classes com docstrings')
        
        if self.stats['functions']['with_docstrings'] < self.stats['functions']['total'] * 0.5:
            recommendations.append('Documente mais funções com docstrings')
        
        if self.stats['files']['by_size']['xlarge'] > 0:
            recommendations.append('Refatore arquivos muito grandes para melhor organização')
        
        if self.stats['issues']['performance']:
            recommendations.append('Remova prints e otimize código de performance')
        
        if self.stats['issues']['security']:
            recommendations.append('Revise código por questões de segurança')
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                self.log(f"{i}. {rec}", 'yellow')
        else:
            self.log('Parabéns! O código está seguindo boas práticas.', 'green')

    def run(self) -> None:
        """Executa a análise completa"""
        self.log('🔍 Iniciando análise de código...', 'blue')
        
        # Analisar arquivos
        files = self.get_all_files(CONFIG['src_dir'])
        self.log(f"Analisando {len(files)} arquivos em {CONFIG['src_dir']}/...", 'yellow')
        
        for file_path in files:
            self.analyze_file(file_path)
        
        self.log_success('Análise concluída!')
        self.generate_report()

def main():
    """Função principal"""
    analyzer = CodeAnalyzer()
    analyzer.run()

if __name__ == '__main__':
    main()
