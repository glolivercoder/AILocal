#!/usr/bin/env python3
"""
Script de Instalação de Dependências de Áudio
Instala automaticamente PyAudio, pyttsx3 e SpeechRecognition
"""

import subprocess
import sys
import os

def install_package(package):
    """Instala um pacote usando pip"""
    try:
        print(f"📦 Instalando {package}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              capture_output=True, text=True, check=True)
        print(f"✅ {package} instalado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar {package}: {e}")
        print(f"Saída do erro: {e.stderr}")
        return False

def check_package(package):
    """Verifica se um pacote está instalado"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def main():
    """Função principal"""
    print("🎤 Instalador de Dependências de Áudio - AiAgenteMCP")
    print("=" * 50)
    
    # Lista de pacotes necessários
    packages = [
        ("pyaudio", "pyaudio"),
        ("pyttsx3", "pyttsx3"), 
        ("speech_recognition", "SpeechRecognition")
    ]
    
    installed_count = 0
    total_count = len(packages)
    
    for import_name, pip_name in packages:
        print(f"\n🔍 Verificando {pip_name}...")
        
        if check_package(import_name):
            print(f"✅ {pip_name} já está instalado!")
            installed_count += 1
        else:
            print(f"❌ {pip_name} não encontrado. Instalando...")
            if install_package(pip_name):
                installed_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Resumo da Instalação:")
    print(f"   ✅ Instalados: {installed_count}/{total_count}")
    
    if installed_count == total_count:
        print("🎉 Todas as dependências de áudio foram instaladas com sucesso!")
        print("\n💡 Agora você pode:")
        print("   • Usar comando de voz na aplicação")
        print("   • Ouvir respostas em áudio")
        print("   • Configurar dispositivos de entrada e saída")
    else:
        print("⚠️  Algumas dependências não foram instaladas.")
        print("   Você pode tentar instalar manualmente:")
        
        for import_name, pip_name in packages:
            if not check_package(import_name):
                print(f"   pip install {pip_name}")
    
    print("\n🚀 Execute 'python ai_agent_gui.py' para usar a aplicação!")

if __name__ == "__main__":
    main() 