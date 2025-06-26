#!/usr/bin/env python3
"""
Script para copiar arquivos para a estrutura AILocalIniciar
"""

import shutil
import os
from pathlib import Path

def copiar_arquivos():
    # Criar estrutura de pastas
    base_dir = Path("AILocalIniciar")
    dirs = ["google_drive", "backup", "config", "utils"]
    
    for dir_name in dirs:
        (base_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    # Copiar arquivos do Google Drive
    google_drive_files = [
        "google_service_account.py",
        "service_account_credentials.json",
        "testar_google_service.py"
    ]
    
    for file in google_drive_files:
        if Path(file).exists():
            shutil.copy2(file, base_dir / "google_drive" / file)
            print(f"✅ Copiado: {file}")
    
    # Copiar arquivos de backup
    backup_files = [
        ("backup_sistema_20250621_201020/backup_manager.py", "backup/backup_manager.py"),
        ("backup_sistema_20250621_201020/backup_tab.py", "backup/backup_tab.py"),
        ("backup_sistema_20250621_201020/requirements_backup.txt", "backup/requirements_backup.txt")
    ]
    
    for src, dst in backup_files:
        if Path(src).exists():
            shutil.copy2(src, base_dir / dst)
            print(f"✅ Copiado: {src}")
    
    # Copiar arquivos de configuração
    config_files = [
        ("config_env.py", "config/config_env.py"),
        ("config_manager.py", "config/config_manager.py")
    ]
    
    for src, dst in config_files:
        if Path(src).exists():
            shutil.copy2(src, base_dir / dst)
            print(f"✅ Copiado: {src}")
    
    print("\n✅ Arquivos copiados com sucesso!")

if __name__ == "__main__":
    copiar_arquivos() 