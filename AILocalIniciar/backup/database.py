import sqlite3
from datetime import datetime
import json
import os

class BackupDatabase:
    def __init__(self, db_path='backup.db'):
        """Inicializa o banco de dados"""
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Cria a tabela se não existir"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    path TEXT NOT NULL,
                    password TEXT NOT NULL,
                    description TEXT,
                    size INTEGER,
                    google_drive_id TEXT,
                    google_drive_link TEXT,
                    status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def add_backup(self, backup_info):
        """Adiciona um novo backup ao banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO backups (
                    timestamp, filename, path, password,
                    description, size, google_drive_id,
                    google_drive_link, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                backup_info['timestamp'],
                backup_info['filename'],
                backup_info['path'],
                backup_info['password'],
                backup_info.get('description', ''),
                backup_info.get('size', 0),
                backup_info.get('google_drive_id'),
                backup_info.get('google_drive_link'),
                backup_info.get('status', 'success')
            ))
            conn.commit()
    
    def get_all_backups(self):
        """Retorna todos os backups ordenados por data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM backups 
                ORDER BY timestamp DESC
            ''')
            columns = [description[0] for description in cursor.description]
            backups = []
            for row in cursor.fetchall():
                backup = dict(zip(columns, row))
                backups.append(backup)
            return backups
    
    def get_backup_by_id(self, backup_id):
        """Retorna um backup específico por ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM backups WHERE id = ?', (backup_id,))
            columns = [description[0] for description in cursor.description]
            row = cursor.fetchone()
            if row:
                return dict(zip(columns, row))
            return None
    
    def update_backup_status(self, backup_id, status):
        """Atualiza o status de um backup"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE backups 
                SET status = ? 
                WHERE id = ?
            ''', (status, backup_id))
            conn.commit()
    
    def update_drive_info(self, backup_id, drive_id, drive_link):
        """Atualiza informações do Google Drive"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE backups 
                SET google_drive_id = ?,
                    google_drive_link = ?
                WHERE id = ?
            ''', (drive_id, drive_link, backup_id))
            conn.commit()
    
    def migrate_from_json(self, json_file):
        """Migra dados do arquivo JSON para o banco de dados"""
        if not os.path.exists(json_file):
            return False
            
        try:
            with open(json_file, 'r') as f:
                backups = json.load(f)
            
            for backup in backups:
                self.add_backup(backup)
            
            return True
        except Exception as e:
            print(f"Erro ao migrar dados: {e}")
            return False
            
    def clear_history(self):
        """Limpa todo o histórico de backups"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM backups')
            conn.commit() 