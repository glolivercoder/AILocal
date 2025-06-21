#!/usr/bin/env python3
"""
Script de Inicialização do AiAgenteMCP
Executa a interface gráfica com configuração da API e sistema RAG
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    required_packages = [
        'PyQt5',
        'requests', 
        'PyPDF2',
        'faiss',
        'sentence_transformers',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Dependências faltando:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nExecute: pip install -r requirements_mcp.txt")
        return False
    
    print("✅ Todas as dependências estão instaladas")
    return True

def create_directories():
    """Cria diretórios necessários"""
    directories = [
        "config",
        "rag_data", 
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Diretórios criados/verificados")

def main():
    """Função principal"""
    print("🚀 Iniciando AiAgenteMCP...")
    print("=" * 50)
    
    # Verificar dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Criar diretórios
    create_directories()
    
    # Importar e executar interface gráfica
    try:
        from ai_agent_gui import main as run_gui
        print("✅ Interface gráfica carregada")
        print("🎯 Iniciando interface...")
        run_gui()
        
    except ImportError as e:
        print(f"❌ Erro ao importar interface gráfica: {e}")
        print("Certifique-se de que ai_agent_gui.py está no diretório")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao executar interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 