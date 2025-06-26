from pathlib import Path
from typing import Optional, Dict, List, Any, Set, Union, Callable
import os
import time
import logging
from datetime import datetime
import sqlite3
import shutil

from database import BackupDatabase

class BackupManager:
    """
    Gerenciador de backups usando py7zr.
    
    Esta classe é responsável por criar, gerenciar e excluir backups
    usando o formato 7z. Os backups são armazenados em um diretório
    específico e suas informações são registradas em um banco SQLite.
    
    O gerenciador oferece:
    - Compressão eficiente com py7zr
    - Registro de backups em banco SQLite
    - Monitoramento de progresso em tempo real
    - Exclusão segura de backups antigos
    - Logging detalhado de operações
    
    Attributes:
        backup_dir (Path): Diretório onde os backups são armazenados
        db (BackupDatabase): Interface com o banco de dados
        logger (logging.Logger): Logger para registro de operações
        
    Example:
        >>> manager = BackupManager()
        >>> zip_path = manager.create_backup(
        ...     "caminho/do/diretorio",
        ...     "nome_do_backup",
        ...     lambda f, p, t, s, r: print(f"{p/t*100:.1f}%")
        ... )
        >>> print(f"Backup criado: {zip_path}")
    """
    
    def __init__(self, backup_dir: str = "backups"):
        """Inicializa o gerenciador de backups"""
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configura logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler("backup.log")
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Conecta ao banco
        self.db = BackupDatabase()
        
    def create_backup(self, source_dir: str, name: str) -> str:
        """Cria um backup do diretório"""
        source_path = Path(source_dir)
        if not source_path.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {source_dir}")
            
        # Gera nome único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"{name}_{timestamp}.zip"
        zip_path = self.backup_dir / zip_name
        
        # Cria backup
        shutil.make_archive(
            str(zip_path.with_suffix("")),
            "zip",
            source_dir
        )
        
        return str(zip_path)
        
    def list_backups(self) -> List[Dict]:
        """Lista todos os backups"""
        backups = []
        for file in self.backup_dir.glob("*.zip"):
            stats = file.stat()
            backups.append({
                "name": file.name,
                "created_at": datetime.fromtimestamp(stats.st_ctime).strftime("%d/%m/%Y %H:%M:%S"),
                "size": f"{stats.st_size / 1024 / 1024:.1f} MB"
            })
        return backups
        
    def delete_backups(self, backup_names: List[str]) -> None:
        """Remove backups selecionados"""
        for name in backup_names:
            file = self.backup_dir / name
            if file.exists():
                file.unlink()
        
    def get_backups(self) -> List[Dict[str, Any]]:
        """
        Lista todos os backups registrados.
        
        Returns:
            list: Lista de dicionários com informações dos backups:
                - name: Nome do arquivo
                - source_dir: Diretório fonte
                - size: Tamanho em bytes
                - created_at: Data de criação
                - status: Status do backup
        """
        return self.db.get_all_backups() 