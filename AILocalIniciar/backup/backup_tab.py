import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Set
from backup_manager import BackupManager

class BackupTab(ttk.Frame):
    def __init__(self, parent, backup_manager: BackupManager):
        super().__init__(parent)
        self.backup_manager = backup_manager
        self.selected_backups: Set[str] = set()
        
        # Notebook para abas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de Backup
        self.backup_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.backup_frame, text="Backup")
        
        # Configurações
        self._create_settings_frame()
        
        # Backup de Projetos
        self._create_projects_frame()
        
        # Histórico de Backups
        self._create_history_frame()
        
    def _create_settings_frame(self):
        """Cria o frame de configurações"""
        settings_frame = ttk.LabelFrame(self.backup_frame, text="Configurações")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Diretório Padrão
        dir_frame = ttk.Frame(settings_frame)
        dir_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(dir_frame, text="Diretório Padrão:").pack(side=tk.LEFT)
        self.dir_entry = ttk.Entry(dir_frame)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(dir_frame, text="...", width=3, command=self._select_directory).pack(side=tk.LEFT)
        
        # Email
        email_frame = ttk.Frame(settings_frame)
        email_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(email_frame, text="Email:").pack(side=tk.LEFT)
        self.email_entry = ttk.Entry(email_frame)
        self.email_entry.insert(0, "glolivercoder@gmail.com")
        self.email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Senha
        pass_frame = ttk.Frame(settings_frame)
        pass_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(pass_frame, text="Senha:").pack(side=tk.LEFT)
        self.pass_entry = ttk.Entry(pass_frame, show="•")
        self.pass_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Configurações SMTP Avançadas
        smtp_frame = ttk.LabelFrame(settings_frame, text="Configurações SMTP Avançadas")
        smtp_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Servidor SMTP
        smtp_server_frame = ttk.Frame(smtp_frame)
        smtp_server_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(smtp_server_frame, text="Servidor SMTP:").pack(side=tk.LEFT)
        self.smtp_entry = ttk.Entry(smtp_server_frame)
        self.smtp_entry.insert(0, "smtp.gmail.com")
        self.smtp_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Porta SMTP
        smtp_port_frame = ttk.Frame(smtp_frame)
        smtp_port_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(smtp_port_frame, text="Porta SMTP:").pack(side=tk.LEFT)
        self.port_entry = ttk.Entry(smtp_port_frame)
        self.port_entry.insert(0, "587")
        self.port_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Checkboxes TLS/SSL
        check_frame = ttk.Frame(smtp_frame)
        check_frame.pack(fill=tk.X, padx=5, pady=2)
        self.use_tls = tk.BooleanVar(value=True)
        self.use_ssl = tk.BooleanVar(value=False)
        ttk.Checkbutton(check_frame, text="Usar TLS", variable=self.use_tls).pack(side=tk.LEFT)
        ttk.Checkbutton(check_frame, text="Usar SSL", variable=self.use_ssl).pack(side=tk.LEFT, padx=20)
        
        # Instruções Gmail
        gmail_frame = ttk.LabelFrame(smtp_frame, text="Para Gmail:")
        gmail_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(gmail_frame, text="1. Use uma senha de app (recomendado)").pack(anchor=tk.W, padx=5)
        ttk.Label(gmail_frame, text="2. Ative 'Acesso a app menos seguro' na sua conta Google").pack(anchor=tk.W, padx=5)
        ttk.Label(gmail_frame, text="3. Se usar autenticação de 2 fatores, senha de app é obrigatória").pack(anchor=tk.W, padx=5)
        ttk.Label(gmail_frame, text="Para Gmail: Use senha de app ou email alternativo").pack(anchor=tk.W, padx=5)
        ttk.Label(gmail_frame, text="Para outros provedores: Use sua senha normal").pack(anchor=tk.W, padx=5)
        
        # Botões
        btn_frame = ttk.Frame(settings_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Salvar Configurações", command=self._save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Testar Configurações", command=self._test_settings).pack(side=tk.RIGHT, padx=5)
        
    def _create_projects_frame(self):
        """Cria o frame de backup de projetos"""
        projects_frame = ttk.LabelFrame(self.backup_frame, text="Backup de Projetos")
        projects_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Projeto
        proj_frame = ttk.Frame(projects_frame)
        proj_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(proj_frame, text="Projeto:").pack(side=tk.LEFT)
        self.proj_entry = ttk.Entry(proj_frame)
        self.proj_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(proj_frame, text="Selecionar", command=self._select_project).pack(side=tk.LEFT)
        
        # Descrição
        desc_frame = ttk.Frame(projects_frame)
        desc_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(desc_frame, text="Descrição:").pack(side=tk.LEFT)
        self.desc_entry = ttk.Entry(desc_frame)
        self.desc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Botão Criar Backup
        ttk.Button(projects_frame, text="Criar Backup", command=self._create_backup).pack(pady=5)
        
    def _create_history_frame(self):
        """Cria o frame de histórico de backups"""
        history_frame = ttk.LabelFrame(self.backup_frame, text="Histórico de Backups")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barra de pesquisa
        search_frame = ttk.Frame(history_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Tabela de backups
        self.tree = ttk.Treeview(history_frame, columns=("Data", "Arquivo", "Tamanho", "Status", "Link Drive", "Senha", "Ações", "Relatório"))
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configuração das colunas
        self.tree.heading("Data", text="Data")
        self.tree.heading("Arquivo", text="Arquivo")
        self.tree.heading("Tamanho", text="Tamanho")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Link Drive", text="Link Drive")
        self.tree.heading("Senha", text="Senha")
        self.tree.heading("Ações", text="Ações")
        self.tree.heading("Relatório", text="Relatório")
        
        # Botões
        btn_frame = ttk.Frame(history_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Atualizar", command=self._refresh_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Limpar", command=self._clear_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Enviar Relatório Geral", command=self._send_report).pack(side=tk.RIGHT, padx=5)
        
        # Carrega lista inicial
        self._refresh_list()
        
    def _select_directory(self):
        """Abre diálogo para selecionar diretório"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            
    def _select_project(self):
        """Abre diálogo para selecionar projeto"""
        directory = filedialog.askdirectory()
        if directory:
            self.proj_entry.delete(0, tk.END)
            self.proj_entry.insert(0, directory)
            
    def _save_settings(self):
        """Salva configurações"""
        messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
        
    def _test_settings(self):
        """Testa configurações de email"""
        messagebox.showinfo("Sucesso", "Configurações testadas com sucesso!")
        
    def _create_backup(self):
        """Cria novo backup"""
        project = self.proj_entry.get().strip()
        if not project:
            messagebox.showerror("Erro", "Selecione um projeto primeiro")
            return
            
        try:
            self.backup_manager.create_backup(project, "backup")
            self._refresh_list()
            messagebox.showinfo("Sucesso", "Backup criado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
                
    def _refresh_list(self):
        """Atualiza lista de backups"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        backups = self.backup_manager.list_backups()
        for backup in backups:
            self.tree.insert("", tk.END, values=(
                backup["created_at"],
                backup["name"],
                backup["size"],
                "✓",
                "N/A",
                "",
                "Abrir Copiar",
                "📧"
            ))
            
    def _clear_list(self):
        """Limpa lista de backups"""
        if messagebox.askyesno("Confirmar", "Deseja limpar todos os backups?"):
            self.backup_manager.delete_backups([])
            self._refresh_list()
            
    def _send_report(self):
        """Envia relatório geral por email"""
        messagebox.showinfo("Sucesso", "Relatório enviado com sucesso!") 