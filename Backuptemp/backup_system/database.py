import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import logging

class BackupDatabase:
    """
    Interface com o banco de dados SQLite para armazenar informações dos backups.
    
    Attributes:
        db_path (str): Caminho para o arquivo do banco de dados
    """
    
    def __init__(self, db_path: str = "backups.db"):
        """Inicializa a conexão com o banco"""
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        
        # Cria tabela se não existir
        self._create_tables()
        
    def _create_tables(self):
        """Cria tabelas necessárias"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS backups (
                        name TEXT PRIMARY KEY,
                        filename TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        size INTEGER NOT NULL,
                        drive_link TEXT,
                        password BOOLEAN DEFAULT FALSE
                    )
                """)
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erro ao criar tabela: {str(e)}")
            
    def add_backup(self, backup_info: Dict[str, Any]):
        """Adiciona um novo backup"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO backups
                    (name, filename, created_at, size, drive_link, password)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        backup_info["name"],
                        backup_info["filename"],
                        backup_info["created_at"],
                        backup_info["size"],
                        backup_info.get("drive_link"),
                        backup_info.get("password", False)
                    )
                )
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erro ao adicionar backup: {str(e)}")
            
    def get_backup(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de um backup"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM backups WHERE name = ?",
                    (name,)
                )
                row = cursor.fetchone()
                
                if row:
                    return {
                        "name": row[0],
                        "filename": row[1],
                        "created_at": row[2],
                        "size": row[3],
                        "drive_link": row[4],
                        "password": bool(row[5])
                    }
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao obter backup: {str(e)}")
            return None
            
    def list_backups(self) -> List[Dict[str, Any]]:
        """Lista todos os backups"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM backups ORDER BY created_at DESC")
                
                backups = []
                for row in cursor.fetchall():
                    backups.append({
                        "name": row[0],
                        "filename": row[1],
                        "created_at": row[2],
                        "size": row[3],
                        "drive_link": row[4],
                        "password": bool(row[5])
                    })
                return backups
                
        except Exception as e:
            self.logger.error(f"Erro ao listar backups: {str(e)}")
            return []
            
    def delete_backup(self, name: str):
        """Remove um backup do banco"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM backups WHERE name = ?",
                    (name,)
                )
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erro ao remover backup: {str(e)}")
            
    def update_backup(self, name: str, **kwargs):
        """Atualiza informações de um backup"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Monta query dinâmica
                fields = []
                values = []
                for key, value in kwargs.items():
                    fields.append(f"{key} = ?")
                    values.append(value)
                    
                if not fields:
                    return
                    
                query = f"UPDATE backups SET {', '.join(fields)} WHERE name = ?"
                values.append(name)
                
                cursor.execute(query, values)
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar backup: {str(e)}")
            
    def clear(self):
        """Remove todos os backups"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM backups")
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erro ao limpar banco: {str(e)}") 