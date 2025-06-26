import sqlite3
from datetime import datetime
from typing import List, Dict

class BackupDatabase:
    def __init__(self, db_path: str = "backup.db"):
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backups (
                    name TEXT PRIMARY KEY,
                    source_dir TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def add_backup(self, name: str, source_dir: str, size: int) -> None:
        """Adiciona um novo backup ao banco"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO backups (name, source_dir, size) VALUES (?, ?, ?)",
                (name, source_dir, size)
            )
            conn.commit()
    
    def delete_backup(self, name: str) -> None:
        """Remove um backup do banco"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM backups WHERE name = ?", (name,))
            conn.commit()
    
    def get_all_backups(self) -> List[Dict]:
        """Retorna todos os backups ordenados por data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, source_dir, size, created_at 
                FROM backups 
                ORDER BY created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()] 