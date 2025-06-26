#!/usr/bin/env python3
"""
Backup do Sistema RAG Moderno
Cria backup completo dos arquivos RAG antes de substituições
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import zipfile

def create_rag_backup():
    """Cria backup completo dos sistemas RAG"""
    print("🔄 Iniciando backup dos sistemas RAG...")
    
    # Diretório de backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backups_rag_sistemas/rag_backup_{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Arquivos RAG para backup
    rag_files = [
        "rag_system_modern.py",
        "rag_system_functional.py",
        "rag_system_langchain.py",
        "rag_system_simple.py",
        "rag_system_simple_fixed.py",
        "rag_ultra_simple.py",
        "requirements_rag_modern.txt",
        "test_rag_modern.py",
        "test_dependencies_simple.py",
        "test_basic_rag.py",
        "GUIA_RAG_FUNCIONAL.md",
        "SISTEMA_RAG_FUNCIONAL_IMPLEMENTADO.md"
    ]
    
    # Diretórios RAG para backup
    rag_dirs = [
        "rag_data",
        "rag_data_robust",
        "rag_data_simple",
        "rag_storage_simple",
        "test_rag_chromadb",
        "test_rag_simple"
    ]
    
    backed_up_files = []
    backed_up_dirs = []
    
    # Backup dos arquivos
    print("📄 Fazendo backup dos arquivos...")
    for file_name in rag_files:
        source_file = Path(file_name)
        if source_file.exists():
            dest_file = backup_dir / file_name
            shutil.copy2(source_file, dest_file)
            backed_up_files.append(file_name)
            print(f"  ✅ {file_name}")
        else:
            print(f"  ⚠️ {file_name} não encontrado")
    
    # Backup dos diretórios
    print("\n📁 Fazendo backup dos diretórios...")
    for dir_name in rag_dirs:
        source_dir = Path(dir_name)
        if source_dir.exists() and source_dir.is_dir():
            dest_dir = backup_dir / dir_name
            shutil.copytree(source_dir, dest_dir)
            backed_up_dirs.append(dir_name)
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ⚠️ {dir_name}/ não encontrado")
    
    # Cria arquivo ZIP
    print("\n📦 Criando arquivo ZIP...")
    zip_file = backup_dir.parent / f"rag_backup_{timestamp}.zip"
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(backup_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(backup_dir)
                zipf.write(file_path, arcname)
    
    # Cria relatório de backup
    report_file = backup_dir / "BACKUP_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# Relatório de Backup RAG - {timestamp}\n\n")
        f.write(f"**Data/Hora:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        
        f.write("## Arquivos Salvos\n\n")
        for file_name in backed_up_files:
            f.write(f"- ✅ {file_name}\n")
        
        f.write("\n## Diretórios Salvos\n\n")
        for dir_name in backed_up_dirs:
            f.write(f"- ✅ {dir_name}/\n")
        
        f.write(f"\n## Localização\n\n")
        f.write(f"- **Diretório:** {backup_dir}\n")
        f.write(f"- **Arquivo ZIP:** {zip_file}\n")
        
        f.write("\n## Próximos Passos\n\n")
        f.write("1. Commit e push para repositório\n")
        f.write("2. Substituição do sistema funcional\n")
        f.write("3. Testes do novo sistema\n")
    
    print(f"\n✅ Backup concluído!")
    print(f"📁 Diretório: {backup_dir}")
    print(f"📦 Arquivo ZIP: {zip_file}")
    print(f"📊 Arquivos salvos: {len(backed_up_files)}")
    print(f"📊 Diretórios salvos: {len(backed_up_dirs)}")
    
    return backup_dir, zip_file

if __name__ == "__main__":
    try:
        backup_dir, zip_file = create_rag_backup()
        print("\n🎉 Backup realizado com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro no backup: {e}")
        import traceback
        traceback.print_exc()