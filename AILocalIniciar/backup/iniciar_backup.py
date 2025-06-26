import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .backup_manager import BackupManager
from .backup_tab import BackupTab

class BackupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Sistema de Backup")
        self.geometry("800x600")
        
        # Inicializa gerenciador
        self.backup_manager = BackupManager()
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controles superiores
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="Diretório:").pack(side=tk.LEFT)
        
        self.dir_entry = ttk.Entry(control_frame, width=50)
        self.dir_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="Selecionar",
            command=self._select_dir
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            control_frame,
            text="Criar Backup",
            command=self._create_backup
        ).pack(side=tk.LEFT, padx=5)
        
        # Tab de backups
        self.backup_tab = BackupTab(main_frame, self.backup_manager)
        self.backup_tab.pack(fill=tk.BOTH, expand=True)
        
    def _select_dir(self):
        """Abre diálogo para selecionar diretório"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            
    def _create_backup(self):
        """Inicia processo de backup"""
        directory = self.dir_entry.get().strip()
        if not directory:
            messagebox.showerror(
                "Erro",
                "Selecione um diretório para backup"
            )
            return
            
        # Mostra progresso
        self.backup_tab.show_progress(True)
        
        try:
            # Cria backup com callback de progresso
            self.backup_manager.create_backup(
                directory,
                "backup",
                self.backup_tab.update_progress
            )
            
            # Atualiza lista
            self.backup_tab.refresh_list()
            
            messagebox.showinfo(
                "Sucesso",
                "Backup criado com sucesso!"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao criar backup: {str(e)}"
            )
            
        finally:
            self.backup_tab.show_progress(False)

if __name__ == "__main__":
    app = BackupApp()
    app.mainloop() 