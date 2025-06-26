import os
import py7zr
import time
import threading
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime
from .database import BackupDatabase

class BackupManager:
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = backup_dir
        self.db = BackupDatabase()
        os.makedirs(backup_dir, exist_ok=True)
        
    def create_backup(self, source_dir: str, name: str, 
                     progress_callback: Optional[Callable[[str, int, int, float, float], None]] = None) -> str:
        """
        Cria um backup compactado do diretório fonte
        
        Args:
            source_dir: Diretório a ser compactado
            name: Nome do backup
            progress_callback: Callback para atualizar progresso (arquivo, bytes_processados, total_bytes, velocidade, tempo_restante)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{name}_{timestamp}.7z"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # Calcula tamanho total
        total_size = sum(f.stat().st_size for f in Path(source_dir).rglob('*') if f.is_file())
        processed_size = 0
        start_time = time.time()
        
        def progress_update(filename: str):
            nonlocal processed_size
            file_size = os.path.getsize(filename)
            processed_size += file_size
            
            if progress_callback:
                elapsed_time = time.time() - start_time
                speed = processed_size / elapsed_time if elapsed_time > 0 else 0
                remaining_time = (total_size - processed_size) / speed if speed > 0 else 0
                progress_callback(filename, processed_size, total_size, speed, remaining_time)
        
        with py7zr.SevenZipFile(backup_path, 'w') as archive:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    archive.write(filepath, os.path.relpath(filepath, source_dir))
                    progress_update(filepath)
        
        # Registra backup no banco
        self.db.add_backup(backup_name, source_dir, total_size)
        return backup_path
    
    def delete_backups(self, backup_names: list[str]) -> None:
        """Exclui múltiplos backups"""
        for name in backup_names:
            backup_path = os.path.join(self.backup_dir, name)
            if os.path.exists(backup_path):
                os.remove(backup_path)
                self.db.delete_backup(name)
    
    def list_backups(self) -> list[dict]:
        """Retorna lista de backups com metadados"""
        return self.db.get_all_backups() 