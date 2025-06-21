#!/usr/bin/env python3
"""
Script de instalação automática de dependências
para o AiAgenteMCP
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Executa um comando e mostra o progresso"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Sucesso")
            return True
        else:
            print(f"❌ {description} - Erro: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Erro: {e}")
        return False

def check_python_version():
    """Verifica a versão do Python"""
    print("🐍 Verificando versão do Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detectado")
        print("   Python 3.8+ é necessário")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True

def check_nodejs():
    """Verifica se Node.js está instalado"""
    print("\n📦 Verificando Node.js...")
    if run_command("node --version", "Verificando Node.js"):
        return True
    else:
        print("\n⚠️  Node.js não encontrado!")
        print("   Instale Node.js de: https://nodejs.org/")
        print("   Ou use:")
        if platform.system() == "Windows":
            print("   winget install OpenJS.NodeJS")
        elif platform.system() == "Darwin":  # macOS
            print("   brew install node")
        else:  # Linux
            print("   sudo apt install nodejs npm")
        return False

def install_python_dependencies():
    """Instala dependências Python"""
    print("\n📚 Instalando dependências Python...")
    
    # Atualizar pip
    run_command("python -m pip install --upgrade pip", "Atualizando pip")
    
    # Instalar dependências
    requirements_file = "requirements_mcp.txt"
    if Path(requirements_file).exists():
        return run_command(f"pip install -r {requirements_file}", "Instalando dependências Python")
    else:
        print(f"❌ Arquivo {requirements_file} não encontrado")
        return False

def install_ollama():
    """Instala Ollama se solicitado"""
    print("\n🦙 Verificando Ollama...")
    
    # Verificar se já está instalado
    if run_command("ollama --version", "Verificando Ollama"):
        print("✅ Ollama já está instalado")
        return True
    
    # Perguntar se quer instalar
    response = input("\n❓ Ollama não encontrado. Deseja instalar? (s/n): ").lower()
    if response in ['s', 'sim', 'y', 'yes']:
        system = platform.system()
        if system == "Windows":
            return run_command("winget install Ollama.Ollama", "Instalando Ollama (Windows)")
        elif system == "Darwin":  # macOS
            return run_command("brew install ollama", "Instalando Ollama (macOS)")
        else:  # Linux
            return run_command("curl -fsSL https://ollama.ai/install.sh | sh", "Instalando Ollama (Linux)")
    else:
        print("⚠️  Ollama não será instalado. Você pode instalá-lo manualmente depois.")
        return True

def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando diretórios...")
    
    directories = [
        "config",
        "logs", 
        "rag_data",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Diretório {directory}/ criado")
    
    return True

def create_config_file():
    """Cria arquivo de configuração inicial"""
    print("\n⚙️  Criando configuração inicial...")
    
    config_file = Path("config/agent_config.json")
    if not config_file.exists():
        config_content = {
            "openrouter_api_key": "",
            "default_model": "google/gemini-1.5-flash",
            "max_tokens": 2048,
            "temperature": 0.7,
            "cache_ttl": 3600,
            "rag_enabled": True,
            "mcp_enabled": True
        }
        
        import json
        with open(config_file, 'w') as f:
            json.dump(config_content, f, indent=2)
        
        print("✅ Arquivo de configuração criado")
    else:
        print("✅ Arquivo de configuração já existe")
    
    return True

def test_installation():
    """Testa a instalação"""
    print("\n🧪 Testando instalação...")
    
    tests = [
        ("import openai", "OpenAI"),
        ("import requests", "Requests"),
        ("import PyPDF2", "PyPDF2"),
        ("import faiss", "FAISS"),
        ("import sentence_transformers", "Sentence Transformers"),
        ("import numpy", "NumPy")
    ]
    
    all_passed = True
    for import_statement, module_name in tests:
        try:
            exec(import_statement)
            print(f"✅ {module_name} - OK")
        except ImportError:
            print(f"❌ {module_name} - Falha")
            all_passed = False
    
    return all_passed

def main():
    """Função principal"""
    print("🚀 Instalador do AiAgenteMCP")
    print("=" * 50)
    
    # Verificar Python
    if not check_python_version():
        print("\n❌ Instalação cancelada - Python 3.8+ necessário")
        return False
    
    # Verificar Node.js
    if not check_nodejs():
        print("\n⚠️  Node.js é necessário para MCPs")
        print("   Continue a instalação e instale Node.js depois")
    
    # Instalar dependências Python
    if not install_python_dependencies():
        print("\n❌ Erro na instalação das dependências Python")
        return False
    
    # Instalar Ollama
    install_ollama()
    
    # Criar diretórios
    if not create_directories():
        print("\n❌ Erro ao criar diretórios")
        return False
    
    # Criar configuração
    if not create_config_file():
        print("\n❌ Erro ao criar configuração")
        return False
    
    # Testar instalação
    if not test_installation():
        print("\n⚠️  Alguns módulos falharam no teste")
        print("   Tente reinstalar as dependências")
    
    print("\n" + "=" * 50)
    print("🎉 Instalação concluída!")
    print("\n📋 Próximos passos:")
    print("1. Configure sua API key do OpenRouter")
    print("2. Execute: python run_ai_agent.py")
    print("3. Instale Node.js se ainda não tiver")
    print("4. Instale Ollama se quiser usar modelos locais")
    
    print("\n📚 Documentação:")
    print("- README_AI_AGENT.md - Guia completo")
    print("- MCPAGENTMODE.md - Configuração do agente")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Instalação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1) 