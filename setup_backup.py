#!/usr/bin/env python3
"""
Script para configurar o ambiente de backup
"""

import os
import shutil
import subprocess
import sys

def setup_environment():
    print("\n🔧 Configurando ambiente de backup...")
    
    # Diretórios
    backup_dir = "AILocalIniciar/backup"
    source_dir = "backup_sistema_20250621_201020"
    
    # Criar diretório se não existir
    os.makedirs(backup_dir, exist_ok=True)
    
    # Arquivos para copiar
    files_to_copy = [
        ("backup_manager.py", f"{source_dir}/backup_manager.py"),
        ("backup_tab.py", f"{source_dir}/backup_tab.py"),
        ("requirements.txt", f"{source_dir}/requirements_backup.txt"),
        ("service_account_credentials.json", "service_account_credentials.json"),
        ("iniciar_backup.py", "AILocalIniciar/backup/iniciar_backup.py")
    ]
    
    # Copiar arquivos
    for dest, source in files_to_copy:
        try:
            shutil.copy2(source, os.path.join(backup_dir, dest))
            print(f"✅ Copiado: {dest}")
        except Exception as e:
            print(f"❌ Erro ao copiar {dest}: {str(e)}")
    
    # Instalar dependências
    print("\n📦 Instalando dependências...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", os.path.join(backup_dir, "requirements.txt")])
        print("✅ Dependências instaladas")
    except Exception as e:
        print(f"❌ Erro ao instalar dependências: {str(e)}")
    
    print("\n✨ Configuração concluída!")
    print("\nPara iniciar o sistema de backup:")
    print(f"1. cd {backup_dir}")
    print("2. python iniciar_backup.py")

if __name__ == "__main__":
    setup_environment() 