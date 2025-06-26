#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Backup Completo do Sistema AI Agent
Cria backup dos principais arquivos e componentes do sistema
"""

import os
import shutil
import datetime
from pathlib import Path
import zipfile
import json

def criar_backup_sistema():
    """Cria backup completo dos principais arquivos do sistema"""
    
    # Timestamp para o backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backup_sistema_{timestamp}")
    backup_dir.mkdir(exist_ok=True)
    
    print(f"📦 Criando backup do sistema em: {backup_dir}")
    
    # Arquivos principais do sistema
    arquivos_principais = [
        "ai_agent_gui.py",
        "rag_system_functional.py",
        "rag_system_advanced.py",
        "config_manager.py",
        "prompt_manager.py",
        "knowledge_enhancement_system.py",
        "mcp_manager.py",
        "voice_system.py",
        "audio_control_widget.py",
        "iniciar_gui.py",
        "requirements.txt",
        "requirements_mcp.txt",
        "requirements_rag_modern.txt",
        ".env.example",
        "README.md",
        "README_COMPLETO.md"
    ]
    
    # Diretórios importantes
    diretorios_importantes = [
        "config",
        "static",
        "templates",
        "models",
        "advanced"
    ]
    
    # Fazer backup dos arquivos principais
    arquivos_copiados = []
    for arquivo in arquivos_principais:
        arquivo_path = Path(arquivo)
        if arquivo_path.exists():
            destino = backup_dir / arquivo
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(arquivo_path, destino)
            arquivos_copiados.append(arquivo)
            print(f"  ✅ {arquivo}")
        else:
            print(f"  ⚠️  {arquivo} (não encontrado)")
    
    # Fazer backup dos diretórios
    diretorios_copiados = []
    for diretorio in diretorios_importantes:
        dir_path = Path(diretorio)
        if dir_path.exists() and dir_path.is_dir():
            destino = backup_dir / diretorio
            shutil.copytree(dir_path, destino, dirs_exist_ok=True)
            diretorios_copiados.append(diretorio)
            print(f"  📁 {diretorio}/")
        else:
            print(f"  ⚠️  {diretorio}/ (não encontrado)")
    
    # Criar arquivo de metadados do backup
    metadata = {
        "timestamp": timestamp,
        "data_backup": datetime.datetime.now().isoformat(),
        "arquivos_copiados": arquivos_copiados,
        "diretorios_copiados": diretorios_copiados,
        "total_arquivos": len(arquivos_copiados),
        "total_diretorios": len(diretorios_copiados)
    }
    
    with open(backup_dir / "backup_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    # Criar arquivo ZIP do backup
    zip_filename = f"backup_sistema_{timestamp}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(backup_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(backup_dir)
                zipf.write(file_path, arcname)
    
    print(f"\n📦 Backup criado com sucesso!")
    print(f"📁 Diretório: {backup_dir}")
    print(f"🗜️  Arquivo ZIP: {zip_filename}")
    print(f"📊 Total: {len(arquivos_copiados)} arquivos, {len(diretorios_copiados)} diretórios")
    
    return backup_dir, zip_filename

if __name__ == "__main__":
    try:
        backup_dir, zip_file = criar_backup_sistema()
        print("\n✅ Backup concluído com sucesso!")
    except Exception as e:
        print(f"❌ Erro durante o backup: {e}")
        import traceback
        traceback.print_exc()