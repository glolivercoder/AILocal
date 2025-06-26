import sqlite3
import os
from pathlib import Path

def read_database():
    """Lê e exibe o conteúdo do banco de dados"""
    try:
        # Tenta encontrar o arquivo do banco
        db_paths = [
            "backup.db",
            "backups.db",
            os.path.join("backups", "backup.db")
        ]
        
        db_file = None
        for path in db_paths:
            if os.path.exists(path):
                db_file = path
                break
                
        if not db_file:
            print("Banco de dados não encontrado")
            return
            
        # Conecta ao banco
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Lista todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\nBanco de dados: {db_file}")
        print("\nTabelas encontradas:")
        for table in tables:
            print(f"\n{'-'*50}")
            print(f"Tabela: {table[0]}")
            
            # Lista estrutura da tabela
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            print("\nColunas:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
                
            # Lista conteúdo
            cursor.execute(f"SELECT * FROM {table[0]}")
            rows = cursor.fetchall()
            print(f"\nRegistros ({len(rows)}):")
            for row in rows:
                print(f"  {row}")
                
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Erro ao ler banco de dados: {str(e)}")
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    read_database() 