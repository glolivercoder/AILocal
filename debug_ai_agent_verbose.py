#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico Verbose para ai_agent_gui.py
Detecta problemas de importação e carregamento
"""

import sys
import os
import traceback
import importlib.util
from pathlib import Path

def print_separator(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def check_python_environment():
    print_separator("AMBIENTE PYTHON")
    print(f"Versão Python: {sys.version}")
    print(f"Executável: {sys.executable}")
    print(f"Diretório atual: {os.getcwd()}")
    print(f"PYTHONPATH: {sys.path[:3]}...")  # Primeiros 3 caminhos

def check_file_exists():
    print_separator("VERIFICAÇÃO DE ARQUIVO")
    ai_agent_path = Path("ai_agent_gui.py")
    if ai_agent_path.exists():
        print(f"✅ Arquivo encontrado: {ai_agent_path.absolute()}")
        print(f"Tamanho: {ai_agent_path.stat().st_size} bytes")
        return True
    else:
        print(f"❌ Arquivo não encontrado: {ai_agent_path.absolute()}")
        return False

def check_dependencies():
    print_separator("VERIFICAÇÃO DE DEPENDÊNCIAS")
    
    # Lista de dependências comuns do ai_agent_gui
    dependencies = [
        'PyQt5', 'PyQt6', 'PySide2', 'PySide6',  # GUI frameworks
        'requests', 'json', 'os', 'sys', 'pathlib',  # Básicas
        'threading', 'subprocess', 'logging',  # Sistema
        'config_manager', 'mcp_manager', 'projects_manager'  # Módulos locais
    ]
    
    missing_deps = []
    
    for dep in dependencies:
        try:
            if dep in ['json', 'os', 'sys', 'pathlib', 'threading', 'subprocess', 'logging']:
                # Módulos built-in
                __import__(dep)
                print(f"✅ {dep} (built-in)")
            else:
                # Módulos externos ou locais
                spec = importlib.util.find_spec(dep)
                if spec is not None:
                    print(f"✅ {dep}")
                else:
                    print(f"❌ {dep} - não encontrado")
                    missing_deps.append(dep)
        except Exception as e:
            print(f"❌ {dep} - erro: {e}")
            missing_deps.append(dep)
    
    return missing_deps

def analyze_import_errors():
    print_separator("ANÁLISE DE IMPORTAÇÃO")
    
    try:
        print("Tentando importar ai_agent_gui...")
        
        # Método 1: Importação direta
        import ai_agent_gui
        print("✅ Importação direta bem-sucedida")
        
        # Verificar classes principais
        if hasattr(ai_agent_gui, 'AiAgentGUI'):
            print("✅ Classe AiAgentGUI encontrada")
        else:
            print("❌ Classe AiAgentGUI não encontrada")
            
        return True
        
    except ImportError as e:
        print(f"❌ Erro de ImportError: {e}")
        print("\nTraceback detalhado:")
        traceback.print_exc()
        return False
        
    except SyntaxError as e:
        print(f"❌ Erro de Sintaxe: {e}")
        print(f"Arquivo: {e.filename}")
        print(f"Linha: {e.lineno}")
        print(f"Texto: {e.text}")
        return False
        
    except Exception as e:
        print(f"❌ Erro geral: {type(e).__name__}: {e}")
        print("\nTraceback completo:")
        traceback.print_exc()
        return False

def check_syntax():
    print_separator("VERIFICAÇÃO DE SINTAXE")
    
    try:
        with open('ai_agent_gui.py', 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Compilar para verificar sintaxe
        compile(source_code, 'ai_agent_gui.py', 'exec')
        print("✅ Sintaxe válida")
        return True
        
    except SyntaxError as e:
        print(f"❌ Erro de sintaxe:")
        print(f"  Linha {e.lineno}: {e.text.strip() if e.text else 'N/A'}")
        print(f"  Erro: {e.msg}")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False

def suggest_solutions(missing_deps, syntax_ok, import_ok):
    print_separator("SUGESTÕES DE SOLUÇÃO")
    
    if not syntax_ok:
        print("🔧 PRIORIDADE ALTA: Corrigir erros de sintaxe primeiro")
        print("   - Verificar parênteses, colchetes e chaves")
        print("   - Verificar indentação")
        print("   - Verificar aspas não fechadas")
    
    if missing_deps:
        print("🔧 Instalar dependências faltantes:")
        for dep in missing_deps:
            if dep in ['PyQt5', 'PyQt6', 'PySide2', 'PySide6']:
                print(f"   pip install {dep}")
            elif dep == 'requests':
                print(f"   pip install {dep}")
            elif dep in ['config_manager', 'mcp_manager', 'projects_manager']:
                print(f"   Verificar se {dep}.py existe no diretório")
    
    if not import_ok:
        print("🔧 Problemas de importação:")
        print("   - Verificar se todos os módulos locais existem")
        print("   - Verificar PYTHONPATH")
        print("   - Executar: python -c 'import ai_agent_gui'")
    
    print("\n🔧 Comandos de diagnóstico adicionais:")
    print("   python -v ai_agent_gui.py  # Modo verbose")
    print("   python -X importtime ai_agent_gui.py  # Tempo de importação")
    print("   python -c 'import py_compile; py_compile.compile(\"ai_agent_gui.py\")'  # Verificar sintaxe")

def main():
    print("🔍 DIAGNÓSTICO VERBOSE - ai_agent_gui.py")
    print(f"Executado em: {os.getcwd()}")
    
    # Verificações sequenciais
    check_python_environment()
    
    file_exists = check_file_exists()
    if not file_exists:
        print("\n❌ ERRO CRÍTICO: Arquivo ai_agent_gui.py não encontrado!")
        return
    
    syntax_ok = check_syntax()
    missing_deps = check_dependencies()
    import_ok = analyze_import_errors()
    
    # Resumo final
    print_separator("RESUMO DO DIAGNÓSTICO")
    print(f"Arquivo existe: {'✅' if file_exists else '❌'}")
    print(f"Sintaxe válida: {'✅' if syntax_ok else '❌'}")
    print(f"Dependências OK: {'✅' if not missing_deps else '❌'}")
    print(f"Importação OK: {'✅' if import_ok else '❌'}")
    
    if syntax_ok and not missing_deps and import_ok:
        print("\n🎉 SUCESSO: ai_agent_gui.py está funcionando corretamente!")
    else:
        suggest_solutions(missing_deps, syntax_ok, import_ok)

if __name__ == "__main__":
    main()