import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

class BackupDatabase:
    """
    Interface com o banco de dados SQLite para backups.
    
    Esta classe gerencia o armazenamento persistente das informações
    dos backups em um banco SQLite, incluindo:
    - Nome do arquivo
    - Diretório fonte
    - Tamanho
    - Data de criação
    - Status
    
    O banco é criado automaticamente se não existir.
    """
    
    def __init__(self, db_path: str = "backup.db"):
        """
        Inicializa a conexão com o banco.
        
        Args:
            db_path: Caminho do arquivo do banco SQLite
        """
        self.db_path = Path(db_path)
        self._create_tables()
        
    def _create_tables(self):
        """Cria as tabelas necessárias se não existirem"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de backups
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    source_dir TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    status TEXT NOT NULL
                )
            """)
            
            conn.commit()
            
    def add_backup(self, backup: Dict[str, Any]) -> int:
        """
        Adiciona um novo backup ao banco.
        
        Args:
            backup: Dicionário com informações do backup
            
        Returns:
            int: ID do backup inserido
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO backups (name, source_dir, size, created_at, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                backup["name"],
                backup["source_dir"],
                backup["size"],
                backup["created_at"],
                backup["status"]
            ))
            
            conn.commit()
            return cursor.lastrowid
            
    def get_all_backups(self) -> List[Dict[str, Any]]:
        """
        Retorna todos os backups registrados.
        
        Returns:
            list: Lista de dicionários com informações dos backups
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM backups ORDER BY created_at DESC")
            
            return [{
                "id": row["id"],
                "name": row["name"],
                "source_dir": row["source_dir"],
                "size": row["size"],
                "created_at": row["created_at"],
                "status": row["status"]
            } for row in cursor.fetchall()]
            
    def delete_backup(self, backup_id: int) -> bool:
        """
        Remove um backup do banco.
        
        Args:
            backup_id: ID do backup a ser removido
            
        Returns:
            bool: True se removido com sucesso
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM backups WHERE id = ?", (backup_id,))
            conn.commit()
            
            return cursor.rowcount > 0
            
    def update_backup_status(self, backup_id: int, status: str) -> bool:
        """
        Atualiza o status de um backup.
        
        Args:
            backup_id: ID do backup
            status: Novo status
            
        Returns:
            bool: True se atualizado com sucesso
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE backups
                SET status = ?
                WHERE id = ?
            """, (status, backup_id))
            
            conn.commit()
            return cursor.rowcount > 0 