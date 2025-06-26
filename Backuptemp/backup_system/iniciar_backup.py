import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path
import logging
import os
import traceback

# Adiciona o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {current_dir}")

try:
    logger.info("Importando módulos...")
    from backup_manager import BackupManager
    from backup_tab import BackupTab
    logger.info("Módulos importados com sucesso")
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)

def main():
    """Função principal que inicia a aplicação"""
    try:
        logger.info("Criando janela principal...")
        root = tk.Tk()
        root.title("Sistema de Backup")
        root.geometry("800x600")
        
        # Define o ícone da janela
        try:
            icon_path = os.path.join(current_dir, "icons", "save.ico")
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
            else:
                logger.warning(f"Arquivo de ícone não encontrado: {icon_path}")
        except Exception as e:
            logger.warning(f"Erro ao carregar ícone: {str(e)}")
        
        logger.info("Configurando tema...")
        style = ttk.Style()
        style.theme_use("clam")
        
        logger.info("Inicializando gerenciador...")
        backup_manager = BackupManager()
        
        logger.info("Criando interface...")
        backup_tab = BackupTab(root, backup_manager)
        backup_tab.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        logger.info("Iniciando loop principal...")
        root.mainloop()
        logger.info("Aplicação encerrada normalmente.")
        
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 