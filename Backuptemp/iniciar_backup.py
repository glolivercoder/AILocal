import tkinter as tk
from tkinter import ttk
import logging
import sys
import os
from pathlib import Path
import traceback

# Adiciona o diretório do sistema ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
backup_system_dir = os.path.join(current_dir, "backup_system")
sys.path.append(backup_system_dir)

def main():
    # Configura logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('backup.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Informações de debug
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    try:
        # Importa módulos
        logger.info("Importando módulos...")
        from backup_system.backup_tab import BackupTab
        
        # Cria janela principal
        logger.info("Criando janela principal...")
        root = tk.Tk()
        root.title("Sistema de Backup")
        root.geometry("800x600")
        
        # Tenta carregar ícone
        try:
            icon_path = Path(backup_system_dir) / "icons" / "save.ico"
            root.iconbitmap(str(icon_path))
        except Exception as e:
            logger.warning(f"Arquivo de ícone não encontrado: {icon_path}")
            
        # Configura tema
        logger.info("Configurando tema...")
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cria interface
        logger.info("Criando interface...")
        backup_tab = BackupTab(root)
        backup_tab.pack(fill=tk.BOTH, expand=True)
        
        # Inicia loop principal
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 