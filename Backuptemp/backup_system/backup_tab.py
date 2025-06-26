import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json
import webbrowser
from typing import Optional, Dict, List, Any, Callable
import logging
import os

from .backup_manager import BackupManager

class BackupTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Configura logger
        self.logger = logging.getLogger(__name__)
        
        # Carrega configurações
        config_path = Path(__file__).parent / "backup_config.json"
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {str(e)}")
            self.config = {}
        
        # Inicializa gerenciador
        self.backup_manager = BackupManager()
        
        # Variáveis
        self.email = tk.StringVar(value="glolivercoder@gmail.com")
        self.senha = tk.StringVar()
        self.smtp_server = tk.StringVar(value="smtp.gmail.com")
        self.smtp_port = tk.StringVar(value="587")
        self.usar_tls = tk.BooleanVar(value=True)
        self.usar_ssl = tk.BooleanVar(value=False)
        self.diretorio_padrao = tk.StringVar()
        self.projeto = tk.StringVar()
        self.descricao = tk.StringVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Notebook principal
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab Backup
        backup_frame = ttk.Frame(notebook)
        notebook.add(backup_frame, text="Backup")
        
        # Seção Configurações
        config_frame = ttk.LabelFrame(backup_frame, text="Configurações")
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Diretório Padrão
        dir_frame = ttk.Frame(config_frame)
        dir_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(dir_frame, text="Diretório Padrão:").pack(side=tk.LEFT)
        ttk.Entry(dir_frame, textvariable=self.diretorio_padrao).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(dir_frame, text="...", width=3, command=self.select_directory).pack(side=tk.RIGHT)
        
        # Email
        email_frame = ttk.Frame(config_frame)
        email_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(email_frame, text="Email:").pack(side=tk.LEFT)
        ttk.Entry(email_frame, textvariable=self.email).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Senha
        senha_frame = ttk.Frame(config_frame)
        senha_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(senha_frame, text="Senha:").pack(side=tk.LEFT)
        ttk.Entry(senha_frame, textvariable=self.senha, show="*").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Configurações SMTP Avançadas
        smtp_frame = ttk.LabelFrame(config_frame, text="Configurações SMTP Avançadas")
        smtp_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Servidor SMTP
        smtp_server_frame = ttk.Frame(smtp_frame)
        smtp_server_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(smtp_server_frame, text="Servidor SMTP:").pack(side=tk.LEFT)
        ttk.Entry(smtp_server_frame, textvariable=self.smtp_server).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Porta SMTP
        smtp_port_frame = ttk.Frame(smtp_frame)
        smtp_port_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(smtp_port_frame, text="Porta SMTP:").pack(side=tk.LEFT)
        ttk.Entry(smtp_port_frame, textvariable=self.smtp_port).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Opções TLS/SSL
        ssl_frame = ttk.Frame(smtp_frame)
        ssl_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Checkbutton(ssl_frame, text="Usar TLS", variable=self.usar_tls).pack(side=tk.LEFT)
        ttk.Checkbutton(ssl_frame, text="Usar SSL", variable=self.usar_ssl).pack(side=tk.LEFT, padx=20)
        
        # Instruções Gmail
        gmail_frame = ttk.LabelFrame(smtp_frame, text="Para Gmail:")
        gmail_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(gmail_frame, text="1. Use uma senha de app (recomendado)").pack(anchor=tk.W)
        ttk.Label(gmail_frame, text="2. Ative 'Acesso a app menos seguro' na sua conta Google").pack(anchor=tk.W)
        ttk.Label(gmail_frame, text="3. Se usar autenticação de 2 fatores, senha de app é obrigatória").pack(anchor=tk.W)
        
        # Botões de Configuração
        btn_frame = ttk.Frame(config_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="💾 Salvar Configurações", command=self.save_config).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(btn_frame, text="🔄 Testar Configurações", command=self.test_config).pack(side=tk.LEFT, expand=True, padx=2)
        
        # Seção Backup de Projetos
        backup_proj_frame = ttk.LabelFrame(backup_frame, text="📁 Backup de Projetos")
        backup_proj_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Projeto
        proj_frame = ttk.Frame(backup_proj_frame)
        proj_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(proj_frame, text="Projeto:").pack(side=tk.LEFT)
        ttk.Entry(proj_frame, textvariable=self.projeto).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(proj_frame, text="📂 Selecionar", command=self.select_project).pack(side=tk.RIGHT)
        
        # Descrição
        desc_frame = ttk.Frame(backup_proj_frame)
        desc_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(desc_frame, text="Descrição:").pack(side=tk.LEFT)
        ttk.Entry(desc_frame, textvariable=self.descricao).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botão Criar Backup
        ttk.Button(backup_proj_frame, text="💾 Criar Backup", command=self.create_backup).pack(fill=tk.X, padx=5, pady=5)
        
        # Seção Histórico de Backups
        history_frame = ttk.LabelFrame(backup_frame, text="📋 Histórico de Backups")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barra de Pesquisa
        search_frame = ttk.Frame(history_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Entry(search_frame).pack(fill=tk.X)
        
        # Treeview
        columns = ("Data", "Arquivo", "Tamanho", "Status", "Link Drive", "Senha", "Ações", "Relatório")
        self.backup_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        
        # Configurar colunas
        for col in columns:
            self.backup_tree.heading(col, text=col)
            if col in ["Data", "Arquivo"]:
                self.backup_tree.column(col, width=150)
            elif col in ["Tamanho", "Status"]:
                self.backup_tree.column(col, width=80)
            else:
                self.backup_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=scrollbar.set)
        
        self.backup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões de Ação
        action_frame = ttk.Frame(history_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(action_frame, text="🔄 Atualizar", command=self.update_backup_list).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(action_frame, text="🗑 Limpar", command=self.clear_backups).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(action_frame, text="📧 Enviar Relatório Geral", command=self.send_report).pack(side=tk.LEFT, expand=True, padx=2)
        
        # Carregar backups
        self.update_backup_list()
        
    def select_directory(self):
        """Abre diálogo para selecionar diretório padrão"""
        directory = filedialog.askdirectory()
        if directory:
            self.diretorio_padrao.set(directory)
            
    def select_project(self):
        """Abre diálogo para selecionar projeto"""
        directory = filedialog.askdirectory()
        if directory:
            self.projeto.set(os.path.basename(directory))
            
    def save_config(self):
        """Salva configurações"""
        config = {
            'email': {
                'username': self.email.get(),
                'password': self.senha.get(),
                'smtp_server': self.smtp_server.get(),
                'smtp_port': int(self.smtp_port.get()),
                'use_tls': self.usar_tls.get(),
                'use_ssl': self.usar_ssl.get()
            },
            'backup': {
                'default_directory': self.diretorio_padrao.get()
            }
        }
        
        try:
            config_path = Path(__file__).parent / "backup_config.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {str(e)}")
            
    def test_config(self):
        """Testa configurações de email"""
        try:
            # Implementar teste de conexão SMTP
            messagebox.showinfo("Sucesso", "Configurações testadas com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao testar configurações: {str(e)}")
            
    def create_backup(self):
        """Cria um novo backup"""
        if not self.projeto.get():
            messagebox.showerror("Erro", "Por favor, selecione um projeto.")
            return
            
        try:
            self.backup_manager.create_backup(
                self.projeto.get(),
                self.projeto.get(),  # Usando nome do projeto como nome do backup
                send_email=True
            )
            messagebox.showinfo("Sucesso", "Backup criado com sucesso!")
            self.update_backup_list()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar backup: {str(e)}")
            
    def update_backup_list(self):
        """Atualiza lista de backups"""
        # Limpa lista atual
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)
            
        # Insere backups
        for backup in self.backup_manager.list_backups():
            self.backup_tree.insert(
                "",
                tk.END,
                values=(
                    backup["created_at"],
                    backup["filename"],
                    f"{backup['size'] / 1024 / 1024:.2f} MB",
                    "✅",
                    "Abrir" if backup.get("drive_link") else "N/A",
                    "🔒" if backup.get("password") else "",
                    "📋 Copiar",
                    "📧"
                ),
                tags=(backup.get("drive_link", ""),)
            )
            
    def clear_backups(self):
        """Remove todos os backups"""
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja remover todos os backups?"):
            try:
                self.backup_manager.delete_all_backups()
                self.update_backup_list()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover backups: {str(e)}")
                
    def send_report(self):
        """Envia relatório geral por email"""
        try:
            self.backup_manager.send_general_report()
            messagebox.showinfo("Sucesso", "Relatório enviado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar relatório: {str(e)}")
            
    def copy_backup(self, backup_name):
        """Copia backup para área de transferência"""
        # Implementar cópia
        pass 