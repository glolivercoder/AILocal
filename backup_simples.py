#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup Simples do Agente Especialista
"""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def criar_backup():
    """Cria backup dos arquivos principais"""
    print("Iniciando backup...")
    
    # Arquivos principais para backup
    arquivos_principais = [
        "ai_agent_gui.py",
        "integrated_knowledge_interface.py", 
        "prompt_manager_gui.py",
        "app.py",
        "start_main_interface.py",
        "rag_system_functional.py",
        "config_manager.py",
        "mcp_manager.py",
        "requirements.txt",
        "README.md"
    ]
    
    # Diretórios para backup
    diretorios = [
        "static",
        "templates",
        "config",
        "rag_data"
    ]
    
    # Criar nome do backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"agente_backup_{timestamp}"
    
    # Criar diretório de backup
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    backup_path = backup_dir / f"{backup_name}.zip"
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Backup de arquivos
        for arquivo in arquivos_principais:
            if Path(arquivo).exists():
                zipf.write(arquivo)
                print(f"Arquivo adicionado: {arquivo}")
        
        # Backup de diretórios
        for diretorio in diretorios:
            dir_path = Path(diretorio)
            if dir_path.exists():
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = Path(root) / file
                        zipf.write(file_path)
                print(f"Diretório adicionado: {diretorio}")
    
    print(f"Backup criado: {backup_path}")
    return backup_path

if __name__ == "__main__":
    criar_backup()