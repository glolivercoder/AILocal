import tkinter as tk
from tkinter import ttk, messagebox
import humanize
from typing import Callable
from .backup_manager import BackupManager

class BackupTab(ttk.Frame):
    def __init__(self, parent, backup_manager: BackupManager):
        super().__init__(parent)
        self.backup_manager = backup_manager
        self.selected_backups = set()
        self._init_ui()
        self.refresh_list()
        
    def _init_ui(self):
        # Frame superior com controles
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Botão de exclusão
        self.delete_btn = ttk.Button(
            control_frame, 
            text="Excluir Selecionados",
            command=self._delete_selected,
            state=tk.DISABLED
        )
        self.delete_btn.pack(side=tk.RIGHT)
        
        # Lista de backups
        self.tree = ttk.Treeview(
            self, 
            columns=("Nome", "Diretório", "Tamanho", "Data"),
            show="headings"
        )
        
        # Configuração das colunas
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Diretório", text="Diretório")
        self.tree.heading("Tamanho", text="Tamanho")
        self.tree.heading("Data", text="Data")
        
        self.tree.column("Nome", width=200)
        self.tree.column("Diretório", width=300)
        self.tree.column("Tamanho", width=100)
        self.tree.column("Data", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Bind eventos
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        
        # Barra de progresso
        self.progress_frame = ttk.Frame(self)
        self.progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack(fill=tk.X)
        
        self.progressbar = ttk.Progressbar(
            self.progress_frame, 
            orient=tk.HORIZONTAL,
            mode='determinate'
        )
        self.progressbar.pack(fill=tk.X)
        
        self.progress_frame.pack_forget()
        
    def _on_select(self, event):
        """Atualiza estado do botão de exclusão baseado na seleção"""
        selected = self.tree.selection()
        self.selected_backups = {
            self.tree.item(item)["values"][0] for item in selected
        }
        self.delete_btn["state"] = tk.NORMAL if selected else tk.DISABLED
        
    def _delete_selected(self):
        """Exclui backups selecionados após confirmação"""
        if not self.selected_backups:
            return
            
        if messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja excluir {len(self.selected_backups)} backup(s)?"
        ):
            self.backup_manager.delete_backups(list(self.selected_backups))
            self.refresh_list()
            
    def refresh_list(self):
        """Atualiza lista de backups"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for backup in self.backup_manager.list_backups():
            self.tree.insert(
                "", 
                tk.END,
                values=(
                    backup["name"],
                    backup["source_dir"],
                    humanize.naturalsize(backup["size"]),
                    backup["created_at"]
                )
            )
            
    def show_progress(self, show: bool = True):
        """Mostra/esconde barra de progresso"""
        if show:
            self.progress_frame.pack(fill=tk.X, padx=5, pady=5)
        else:
            self.progress_frame.pack_forget()
            
    def update_progress(self, filename: str, processed: int, total: int, 
                       speed: float, remaining: float):
        """Atualiza indicadores de progresso"""
        percent = (processed / total * 100) if total > 0 else 0
        self.progressbar["value"] = percent
        
        status = (
            f"Processando: {filename}\n"
            f"Progresso: {processed:,} / {total:,} bytes ({percent:.1f}%)\n"
            f"Velocidade: {humanize.naturalsize(speed)}/s\n"
            f"Tempo restante: {remaining:.1f}s"
        )
        self.progress_label["text"] = status 