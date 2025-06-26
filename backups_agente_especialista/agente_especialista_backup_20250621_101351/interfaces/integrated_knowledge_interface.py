#!/usr/bin/env python3
"""
Interface Integrada de Sistema de Conhecimento
Combina LangChain, TensorFlow, Docker e N8N
"""

import sys
import os
import json
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# PyQt5 para interface gráfica
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget,
        QTableWidget, QTableWidgetItem, QGroupBox, QComboBox,
        QSpinBox, QCheckBox, QProgressBar, QMessageBox, QFileDialog,
        QSplitter, QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
        QFrame, QScrollArea, QInputDialog
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot, QThread
    from PyQt5.QtGui import QFont, QIcon, QColor, QPixmap
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    print("⚠️ PyQt5 não disponível")

# Importar componentes do sistema
try:
    from knowledge_enhancement_system import KnowledgeEnhancementSystem
    from docker_n8n_interface import DockerManager, N8NManager, MCPIntegration
    KNOWLEDGE_SYSTEM_AVAILABLE = True
except ImportError as e:
    KNOWLEDGE_SYSTEM_AVAILABLE = False
    print(f"⚠️ Sistema de conhecimento não disponível: {e}")

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeWorker(QThread):
    """Worker para processamento de conhecimento em background"""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    result_ready = pyqtSignal(dict)
    
    def __init__(self, system, task_type, data):
        super().__init__()
        self.system = system
        self.task_type = task_type
        self.data = data
    
    def run(self):
        """Executa tarefa em background"""
        try:
            self.status_updated.emit("Iniciando processamento...")
            
            if self.task_type == "add_document":
                result = self.system.add_document(self.data)
                self.result_ready.emit(result)
            
            elif self.task_type == "query_knowledge":
                result = self.system.query_knowledge(self.data)
                self.result_ready.emit(result)
            
            elif self.task_type == "analyze_documents":
                result = self.system.analyze_documents(self.data)
                self.result_ready.emit(result)
            
            self.status_updated.emit("Processamento concluído")
            
        except Exception as e:
            self.status_updated.emit(f"Erro: {e}")
            self.result_ready.emit({"error": str(e)})

class IntegratedKnowledgeInterface(QMainWindow):
    """Interface integrada principal"""
    
    def __init__(self):
        super().__init__()
        
        # Inicializar sistemas
        self.knowledge_system = None
        self.docker_manager = None
        self.n8n_manager = None
        self.mcp_integration = None
        
        if KNOWLEDGE_SYSTEM_AVAILABLE:
            self.knowledge_system = KnowledgeEnhancementSystem()
            self.docker_manager = DockerManager()
            self.n8n_manager = N8NManager()
            self.mcp_integration = MCPIntegration()
        
        # Configurar interface
        self.init_ui()
        self.setup_timers()
        
        # Carregar dados iniciais
        self.refresh_all_data()
    
    def init_ui(self):
        """Inicializa a interface gráfica"""
        self.setWindowTitle("Sistema Integrado de Conhecimento - LangChain + TensorFlow + Docker + N8N")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Barra de status superior
        self.create_status_bar()
        main_layout.addWidget(self.status_frame)
        
        # Criar abas principais
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Aba de Conhecimento
        self.create_knowledge_tab()
        
        # Aba de Docker
        self.create_docker_tab()
        
        # Aba de N8N
        self.create_n8n_tab()
        
        # Aba de MCPs
        self.create_mcps_tab()
        
        # Aba de Análise
        self.create_analysis_tab()
        
        # Aba de Configuração
        self.create_config_tab()
        
        # Nova aba Projects Manager
        self.create_projects_manager_tab()
        
        # Status bar inferior
        self.statusBar().showMessage("Sistema Integrado de Conhecimento - Pronto")
    
    def create_status_bar(self):
        """Cria barra de status superior"""
        self.status_frame = QFrame()
        self.status_frame.setFrameStyle(QFrame.StyledPanel)
        status_layout = QHBoxLayout(self.status_frame)
        
        # Status do sistema
        self.system_status_label = QLabel("Status: Inicializando...")
        status_layout.addWidget(self.system_status_label)
        
        # Progress bar
        self.global_progress = QProgressBar()
        self.global_progress.setMaximumWidth(200)
        status_layout.addWidget(self.global_progress)
        
        # Botões de ação rápida
        self.quick_refresh_btn = QPushButton("🔄 Atualizar")
        self.quick_refresh_btn.clicked.connect(self.refresh_all_data)
        status_layout.addWidget(self.quick_refresh_btn)
        
        self.quick_analyze_btn = QPushButton("📊 Analisar")
        self.quick_analyze_btn.clicked.connect(self.quick_analysis)
        status_layout.addWidget(self.quick_analyze_btn)
        
        status_layout.addStretch()
    
    def create_knowledge_tab(self):
        """Cria aba de gerenciamento de conhecimento"""
        knowledge_widget = QWidget()
        layout = QVBoxLayout(knowledge_widget)
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)
        
        # Painel esquerdo - Upload e gerenciamento
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Grupo de upload
        upload_group = QGroupBox("📄 Upload de Documentos")
        upload_layout = QVBoxLayout(upload_group)
        
        # Botões de upload
        upload_buttons_layout = QHBoxLayout()
        
        self.upload_file_btn = QPushButton("📁 Selecionar Arquivo")
        self.upload_file_btn.clicked.connect(self.upload_file)
        upload_buttons_layout.addWidget(self.upload_file_btn)
        
        self.upload_folder_btn = QPushButton("📂 Selecionar Pasta")
        self.upload_folder_btn.clicked.connect(self.upload_folder)
        upload_buttons_layout.addWidget(self.upload_folder_btn)
        
        upload_layout.addLayout(upload_buttons_layout)
        
        # Lista de documentos processados
        upload_layout.addWidget(QLabel("Documentos Processados:"))
        self.documents_list = QListWidget()
        upload_layout.addWidget(self.documents_list)
        
        left_layout.addWidget(upload_group)
        
        # Grupo de consulta
        query_group = QGroupBox("🔍 Consulta de Conhecimento")
        query_layout = QVBoxLayout(query_group)
        
        query_layout.addWidget(QLabel("Pergunta:"))
        self.query_input = QTextEdit()
        self.query_input.setMaximumHeight(100)
        query_layout.addWidget(self.query_input)
        
        self.query_btn = QPushButton("🔍 Consultar")
        self.query_btn.clicked.connect(self.query_knowledge)
        query_layout.addWidget(self.query_btn)
        
        left_layout.addWidget(query_group)
        
        # Painel direito - Resultados e visualização
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Resultados da consulta
        results_group = QGroupBox("📋 Resultados")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        right_layout.addWidget(results_group)
        
        # Adicionar painéis ao splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([600, 1000])
        
        # Adicionar aba
        self.tab_widget.addTab(knowledge_widget, "🧠 Conhecimento")
    
    def create_docker_tab(self):
        """Cria aba de gerenciamento Docker"""
        docker_widget = QWidget()
        layout = QVBoxLayout(docker_widget)
        
        # Splitter para containers e imagens
        docker_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(docker_splitter)
        
        # Painel de containers
        containers_panel = QWidget()
        containers_layout = QVBoxLayout(containers_panel)
        
        containers_group = QGroupBox("🐳 Containers Docker")
        containers_layout.addWidget(containers_group)
        
        containers_inner_layout = QVBoxLayout(containers_group)
        
        # Botões de containers
        containers_buttons_layout = QHBoxLayout()
        
        self.refresh_containers_btn = QPushButton("🔄 Atualizar")
        self.refresh_containers_btn.clicked.connect(self.refresh_containers)
        containers_buttons_layout.addWidget(self.refresh_containers_btn)
        
        self.start_container_btn = QPushButton("▶️ Iniciar")
        self.start_container_btn.clicked.connect(self.start_container)
        containers_buttons_layout.addWidget(self.start_container_btn)
        
        self.stop_container_btn = QPushButton("⏹️ Parar")
        self.stop_container_btn.clicked.connect(self.stop_container)
        containers_buttons_layout.addWidget(self.stop_container_btn)
        
        containers_inner_layout.addLayout(containers_buttons_layout)
        
        # Tabela de containers
        self.containers_table = QTableWidget()
        self.containers_table.setColumnCount(5)
        self.containers_table.setHorizontalHeaderLabels([
            "ID", "Nome", "Status", "Imagem", "Portas"
        ])
        containers_inner_layout.addWidget(self.containers_table)
        
        # Painel de imagens
        images_panel = QWidget()
        images_layout = QVBoxLayout(images_panel)
        
        images_group = QGroupBox("🖼️ Imagens Docker")
        images_layout.addWidget(images_group)
        
        images_inner_layout = QVBoxLayout(images_group)
        
        # Botões de imagens
        images_buttons_layout = QHBoxLayout()
        
        self.refresh_images_btn = QPushButton("🔄 Atualizar")
        self.refresh_images_btn.clicked.connect(self.refresh_images)
        images_buttons_layout.addWidget(self.refresh_images_btn)
        
        self.run_image_btn = QPushButton("🚀 Executar")
        self.run_image_btn.clicked.connect(self.run_image)
        images_buttons_layout.addWidget(self.run_image_btn)
        
        images_inner_layout.addLayout(images_buttons_layout)
        
        # Tabela de imagens
        self.images_table = QTableWidget()
        self.images_table.setColumnCount(4)
        self.images_table.setHorizontalHeaderLabels([
            "ID", "Tags", "Tamanho", "Criado"
        ])
        images_inner_layout.addWidget(self.images_table)
        
        # Adicionar painéis ao splitter
        docker_splitter.addWidget(containers_panel)
        docker_splitter.addWidget(images_panel)
        docker_splitter.setSizes([800, 800])
        
        # Adicionar aba
        self.tab_widget.addTab(docker_widget, "🐳 Docker")
    
    def create_n8n_tab(self):
        """Cria aba de gerenciamento N8N"""
        n8n_widget = QWidget()
        layout = QVBoxLayout(n8n_widget)
        
        # Configuração N8N
        config_group = QGroupBox("⚙️ Configuração N8N")
        config_layout = QHBoxLayout(config_group)
        
        config_layout.addWidget(QLabel("URL:"))
        self.n8n_url_input = QLineEdit("http://localhost:5678")
        config_layout.addWidget(self.n8n_url_input)
        
        config_layout.addWidget(QLabel("Token:"))
        self.n8n_token_input = QLineEdit()
        self.n8n_token_input.setEchoMode(QLineEdit.Password)
        config_layout.addWidget(self.n8n_token_input)
        
        self.connect_n8n_btn = QPushButton("🔗 Conectar")
        self.connect_n8n_btn.clicked.connect(self.connect_n8n)
        config_layout.addWidget(self.connect_n8n_btn)
        
        layout.addWidget(config_group)
        
        # Workflows
        workflows_group = QGroupBox("🔄 Workflows")
        workflows_layout = QVBoxLayout(workflows_group)
        
        # Botões de workflows
        workflows_buttons_layout = QHBoxLayout()
        
        self.refresh_workflows_btn = QPushButton("🔄 Atualizar")
        self.refresh_workflows_btn.clicked.connect(self.refresh_workflows)
        workflows_buttons_layout.addWidget(self.refresh_workflows_btn)
        
        self.create_workflow_btn = QPushButton("➕ Criar")
        self.create_workflow_btn.clicked.connect(self.create_workflow)
        workflows_buttons_layout.addWidget(self.create_workflow_btn)
        
        self.activate_workflow_btn = QPushButton("▶️ Ativar")
        self.activate_workflow_btn.clicked.connect(self.activate_workflow)
        workflows_buttons_layout.addWidget(self.activate_workflow_btn)
        
        workflows_layout.addLayout(workflows_buttons_layout)
        
        # Lista de workflows
        self.workflows_list = QListWidget()
        workflows_layout.addWidget(self.workflows_list)
        
        layout.addWidget(workflows_group)
        
        # Adicionar aba
        self.tab_widget.addTab(n8n_widget, "🔄 N8N")
    
    def create_mcps_tab(self):
        """Cria aba de integração MCPs"""
        mcps_widget = QWidget()
        layout = QVBoxLayout(mcps_widget)
        
        # MCPs disponíveis
        mcps_group = QGroupBox("🔌 MCPs Disponíveis")
        mcps_layout = QVBoxLayout(mcps_group)
        
        self.mcps_tree = QTreeWidget()
        self.mcps_tree.setHeaderLabel("MCPs")
        mcps_layout.addWidget(self.mcps_tree)
        
        layout.addWidget(mcps_group)
        
        # Criação de workflows MCP
        workflow_creation_group = QGroupBox("⚡ Criação de Workflows MCP")
        workflow_creation_layout = QVBoxLayout(workflow_creation_group)
        
        # Tipo de workflow
        workflow_type_layout = QHBoxLayout()
        workflow_type_layout.addWidget(QLabel("Tipo:"))
        self.workflow_type_combo = QComboBox()
        self.workflow_type_combo.addItems([
            "Webhook",
            "Data Architecture",
            "Knowledge Processing",
            "Custom"
        ])
        workflow_type_layout.addWidget(self.workflow_type_combo)
        
        self.create_mcp_workflow_btn = QPushButton("⚡ Criar Workflow MCP")
        self.create_mcp_workflow_btn.clicked.connect(self.create_mcp_workflow)
        workflow_type_layout.addWidget(self.create_mcp_workflow_btn)
        
        workflow_creation_layout.addLayout(workflow_type_layout)
        
        layout.addWidget(workflow_creation_group)
        
        # Adicionar aba
        self.tab_widget.addTab(mcps_widget, "🔌 MCPs")
    
    def create_analysis_tab(self):
        """Cria aba de análise de dados"""
        analysis_widget = QWidget()
        layout = QVBoxLayout(analysis_widget)
        
        # Splitter para diferentes tipos de análise
        analysis_splitter = QSplitter(Qt.Vertical)
        layout.addWidget(analysis_splitter)
        
        # Análise de documentos
        docs_analysis_panel = QWidget()
        docs_analysis_layout = QVBoxLayout(docs_analysis_panel)
        
        docs_analysis_group = QGroupBox("📊 Análise de Documentos")
        docs_analysis_layout.addWidget(docs_analysis_group)
        
        docs_analysis_inner_layout = QVBoxLayout(docs_analysis_group)
        
        # Controles de análise
        analysis_controls_layout = QHBoxLayout()
        
        analysis_controls_layout.addWidget(QLabel("Número de Clusters:"))
        self.clusters_spin = QSpinBox()
        self.clusters_spin.setRange(2, 20)
        self.clusters_spin.setValue(5)
        analysis_controls_layout.addWidget(self.clusters_spin)
        
        self.analyze_docs_btn = QPushButton("📊 Analisar Documentos")
        self.analyze_docs_btn.clicked.connect(self.analyze_documents)
        analysis_controls_layout.addWidget(self.analyze_docs_btn)
        
        docs_analysis_inner_layout.addLayout(analysis_controls_layout)
        
        # Resultados da análise
        self.analysis_results_text = QTextEdit()
        self.analysis_results_text.setReadOnly(True)
        docs_analysis_inner_layout.addWidget(self.analysis_results_text)
        
        # Análise de sentimento
        sentiment_analysis_panel = QWidget()
        sentiment_analysis_layout = QVBoxLayout(sentiment_analysis_panel)
        
        sentiment_analysis_group = QGroupBox("😊 Análise de Sentimento")
        sentiment_analysis_layout.addWidget(sentiment_analysis_group)
        
        sentiment_analysis_inner_layout = QVBoxLayout(sentiment_analysis_group)
        
        self.analyze_sentiment_btn = QPushButton("😊 Analisar Sentimento")
        self.analyze_sentiment_btn.clicked.connect(self.analyze_sentiment)
        sentiment_analysis_inner_layout.addWidget(self.analyze_sentiment_btn)
        
        self.sentiment_results_text = QTextEdit()
        self.sentiment_results_text.setReadOnly(True)
        sentiment_analysis_inner_layout.addWidget(self.sentiment_results_text)
        
        # Adicionar painéis ao splitter
        analysis_splitter.addWidget(docs_analysis_panel)
        analysis_splitter.addWidget(sentiment_analysis_panel)
        analysis_splitter.setSizes([500, 500])
        
        # Adicionar aba
        self.tab_widget.addTab(analysis_widget, "📊 Análise")
    
    def create_config_tab(self):
        """Cria aba de configuração completa com todas as credenciais"""
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)
        
        # Scroll area para comportar todas as configurações
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 1. Configurações OpenAI/LangChain
        openai_group = QGroupBox("🤖 OpenAI & LangChain")
        openai_layout = QVBoxLayout(openai_group)
        
        openai_layout.addWidget(QLabel("OpenAI API Key:"))
        self.openai_key_input = QLineEdit()
        self.openai_key_input.setEchoMode(QLineEdit.Password)
        openai_layout.addWidget(self.openai_key_input)
        
        openai_layout.addWidget(QLabel("Modelo:"))
        self.model_name_combo = QComboBox()
        self.model_name_combo.addItems(["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"])
        openai_layout.addWidget(self.model_name_combo)
        
        scroll_layout.addWidget(openai_group)
        
        # 2. Configurações de E-mail
        email_group = QGroupBox("📧 Configurações de E-mail")
        email_layout = QVBoxLayout(email_group)
        
        email_layout.addWidget(QLabel("E-mail (SMTP):"))
        self.email_smtp_input = QLineEdit()
        email_layout.addWidget(self.email_smtp_input)
        
        email_layout.addWidget(QLabel("Senha do E-mail:"))
        self.email_password_input = QLineEdit()
        self.email_password_input.setEchoMode(QLineEdit.Password)
        email_layout.addWidget(self.email_password_input)
        
        email_layout.addWidget(QLabel("Servidor SMTP:"))
        self.smtp_server_input = QLineEdit("smtp.gmail.com")
        email_layout.addWidget(self.smtp_server_input)
        
        email_layout.addWidget(QLabel("Porta SMTP:"))
        self.smtp_port_input = QSpinBox()
        self.smtp_port_input.setRange(1, 65535)
        self.smtp_port_input.setValue(587)
        email_layout.addWidget(self.smtp_port_input)
        
        scroll_layout.addWidget(email_group)
        
        # 3. Configurações Google Drive
        gdrive_group = QGroupBox("☁️ Google Drive")
        gdrive_layout = QVBoxLayout(gdrive_group)
        
        gdrive_layout.addWidget(QLabel("Client ID:"))
        self.gdrive_client_id_input = QLineEdit()
        gdrive_layout.addWidget(self.gdrive_client_id_input)
        
        gdrive_layout.addWidget(QLabel("Client Secret:"))
        self.gdrive_client_secret_input = QLineEdit()
        self.gdrive_client_secret_input.setEchoMode(QLineEdit.Password)
        gdrive_layout.addWidget(self.gdrive_client_secret_input)
        
        gdrive_layout.addWidget(QLabel("Refresh Token:"))
        self.gdrive_refresh_token_input = QLineEdit()
        self.gdrive_refresh_token_input.setEchoMode(QLineEdit.Password)
        gdrive_layout.addWidget(self.gdrive_refresh_token_input)
        
        self.gdrive_auth_btn = QPushButton("🔐 Autenticar Google Drive")
        self.gdrive_auth_btn.clicked.connect(self.authenticate_gdrive)
        gdrive_layout.addWidget(self.gdrive_auth_btn)
        
        scroll_layout.addWidget(gdrive_group)
        
        # 4. Configurações Terabox
        terabox_group = QGroupBox("📦 Terabox")
        terabox_layout = QVBoxLayout(terabox_group)
        
        terabox_layout.addWidget(QLabel("Token de Acesso:"))
        self.terabox_token_input = QLineEdit()
        self.terabox_token_input.setEchoMode(QLineEdit.Password)
        terabox_layout.addWidget(self.terabox_token_input)
        
        terabox_layout.addWidget(QLabel("Username:"))
        self.terabox_username_input = QLineEdit()
        terabox_layout.addWidget(self.terabox_username_input)
        
        terabox_layout.addWidget(QLabel("Password:"))
        self.terabox_password_input = QLineEdit()
        self.terabox_password_input.setEchoMode(QLineEdit.Password)
        terabox_layout.addWidget(self.terabox_password_input)
        
        self.terabox_auth_btn = QPushButton("🔐 Autenticar Terabox")
        self.terabox_auth_btn.clicked.connect(self.authenticate_terabox)
        terabox_layout.addWidget(self.terabox_auth_btn)
        
        scroll_layout.addWidget(terabox_group)
        
        # 5. Configurações N8N
        n8n_group = QGroupBox("🔄 N8N")
        n8n_layout = QVBoxLayout(n8n_group)
        
        n8n_layout.addWidget(QLabel("URL do N8N:"))
        self.n8n_url_input = QLineEdit("http://localhost:5678")
        n8n_layout.addWidget(self.n8n_url_input)
        
        n8n_layout.addWidget(QLabel("Token de Acesso:"))
        self.n8n_token_input = QLineEdit()
        self.n8n_token_input.setEchoMode(QLineEdit.Password)
        n8n_layout.addWidget(self.n8n_token_input)
        
        n8n_layout.addWidget(QLabel("Webhook Path:"))
        self.n8n_webhook_input = QLineEdit("/webhook")
        n8n_layout.addWidget(self.n8n_webhook_input)
        
        scroll_layout.addWidget(n8n_group)
        
        # 6. Configurações Docker
        docker_group = QGroupBox("🐳 Docker")
        docker_layout = QVBoxLayout(docker_group)
        
        docker_layout.addWidget(QLabel("Socket Docker:"))
        self.docker_socket_input = QLineEdit("/var/run/docker.sock")
        docker_layout.addWidget(self.docker_socket_input)
        
        docker_layout.addWidget(QLabel("Auto Refresh (segundos):"))
        self.docker_refresh_input = QSpinBox()
        self.docker_refresh_input.setRange(10, 300)
        self.docker_refresh_input.setValue(30)
        docker_layout.addWidget(self.docker_refresh_input)
        
        scroll_layout.addWidget(docker_group)
        
        # 7. Configurações do Sistema de Conhecimento
        knowledge_group = QGroupBox("🧠 Sistema de Conhecimento")
        knowledge_layout = QVBoxLayout(knowledge_group)
        
        knowledge_layout.addWidget(QLabel("Chunk Size:"))
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(100, 5000)
        self.chunk_size_spin.setValue(1000)
        knowledge_layout.addWidget(self.chunk_size_spin)
        
        knowledge_layout.addWidget(QLabel("Chunk Overlap:"))
        self.chunk_overlap_spin = QSpinBox()
        self.chunk_overlap_spin.setRange(0, 1000)
        self.chunk_overlap_spin.setValue(200)
        knowledge_layout.addWidget(self.chunk_overlap_spin)
        
        knowledge_layout.addWidget(QLabel("Vectorstore Path:"))
        self.vectorstore_path_input = QLineEdit("vectorstore")
        knowledge_layout.addWidget(self.vectorstore_path_input)
        
        knowledge_layout.addWidget(QLabel("Max Documents:"))
        self.max_documents_spin = QSpinBox()
        self.max_documents_spin.setRange(100, 10000)
        self.max_documents_spin.setValue(1000)
        knowledge_layout.addWidget(self.max_documents_spin)
        
        scroll_layout.addWidget(knowledge_group)
        
        # 8. Configurações de Projetos
        projects_group = QGroupBox("📁 Projects Manager")
        projects_layout = QVBoxLayout(projects_group)
        
        projects_layout.addWidget(QLabel("Diretório de Projetos:"))
        self.projects_dir_input = QLineEdit("projects")
        projects_layout.addWidget(self.projects_dir_input)
        
        projects_layout.addWidget(QLabel("Diretório de Backups:"))
        self.backups_dir_input = QLineEdit("backups")
        projects_layout.addWidget(self.backups_dir_input)
        
        projects_layout.addWidget(QLabel("E-mails para Notificação:"))
        self.notification_emails_input = QLineEdit()
        self.notification_emails_input.setPlaceholderText("email1@exemplo.com, email2@exemplo.com")
        projects_layout.addWidget(self.notification_emails_input)
        
        scroll_layout.addWidget(projects_group)
        
        # 9. Configurações de Segurança
        security_group = QGroupBox("🔒 Segurança")
        security_layout = QVBoxLayout(security_group)
        
        self.encrypt_config_checkbox = QCheckBox("Criptografar configurações salvas")
        security_layout.addWidget(self.encrypt_config_checkbox)
        
        self.auto_backup_checkbox = QCheckBox("Backup automático de configurações")
        security_layout.addWidget(self.auto_backup_checkbox)
        
        self.log_actions_checkbox = QCheckBox("Log de ações do usuário")
        security_layout.addWidget(self.log_actions_checkbox)
        
        scroll_layout.addWidget(security_group)
        
        # Botões de ação
        config_buttons_layout = QHBoxLayout()
        
        self.save_config_btn = QPushButton("💾 Salvar Configuração")
        self.save_config_btn.clicked.connect(self.save_configuration)
        config_buttons_layout.addWidget(self.save_config_btn)
        
        self.load_config_btn = QPushButton("📂 Carregar Configuração")
        self.load_config_btn.clicked.connect(self.load_configuration)
        config_buttons_layout.addWidget(self.load_config_btn)
        
        self.test_config_btn = QPushButton("🧪 Testar Configurações")
        self.test_config_btn.clicked.connect(self.test_configurations)
        config_buttons_layout.addWidget(self.test_config_btn)
        
        self.reset_config_btn = QPushButton("🔄 Resetar Configurações")
        self.reset_config_btn.clicked.connect(self.reset_configurations)
        config_buttons_layout.addWidget(self.reset_config_btn)
        
        scroll_layout.addLayout(config_buttons_layout)
        
        # Status dos componentes
        status_group = QGroupBox("📋 Status dos Componentes")
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        status_layout.addWidget(self.status_text)
        
        scroll_layout.addWidget(status_group)
        
        # Configurar scroll area
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Adicionar aba
        self.tab_widget.addTab(config_widget, "⚙️ Configuração")
        
        # Carregar configurações salvas
        self.load_saved_configuration()
    
    def authenticate_gdrive(self):
        """Autentica Google Drive"""
        try:
            from pydrive2.auth import GoogleAuth
            from pydrive2.drive import GoogleDrive
            
            gauth = GoogleAuth()
            
            # Configurar credenciais
            if self.gdrive_client_id_input.text() and self.gdrive_client_secret_input.text():
                gauth.settings['client_config_file'] = 'client_secrets.json'
                # Criar arquivo de configuração temporário
                import json
                client_config = {
                    "web": {
                        "client_id": self.gdrive_client_id_input.text(),
                        "client_secret": self.gdrive_client_secret_input.text(),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                }
                with open('client_secrets.json', 'w') as f:
                    json.dump(client_config, f)
            
            gauth.LocalWebserverAuth()
            gauth.SaveCredentialsFile("gdrive_creds.txt")
            
            QMessageBox.information(self, "Sucesso", "Google Drive autenticado com sucesso!")
            
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro na autenticação Google Drive: {e}")
    
    def authenticate_terabox(self):
        """Autentica Terabox"""
        try:
            from terabox import Terabox
            
            username = self.terabox_username_input.text()
            password = self.terabox_password_input.text()
            
            if not username or not password:
                QMessageBox.warning(self, "Erro", "Digite username e password do Terabox")
                return
            
            terabox = Terabox()
            token = terabox.login(username, password)
            
            if token:
                self.terabox_token_input.setText(token)
                QMessageBox.information(self, "Sucesso", "Terabox autenticado com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Falha na autenticação Terabox")
                
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro na autenticação Terabox: {e}")
    
    def load_saved_configuration(self):
        """Carrega configurações salvas"""
        try:
            config_file = Path("config/system_config.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Aplicar configurações aos campos
                self.openai_key_input.setText(config.get("openai_api_key", ""))
                self.model_name_combo.setCurrentText(config.get("model_name", "gpt-3.5-turbo"))
                
                self.email_smtp_input.setText(config.get("email_smtp", ""))
                self.email_password_input.setText(config.get("email_password", ""))
                self.smtp_server_input.setText(config.get("smtp_server", "smtp.gmail.com"))
                self.smtp_port_input.setValue(config.get("smtp_port", 587))
                
                self.gdrive_client_id_input.setText(config.get("gdrive_client_id", ""))
                self.gdrive_client_secret_input.setText(config.get("gdrive_client_secret", ""))
                self.gdrive_refresh_token_input.setText(config.get("gdrive_refresh_token", ""))
                
                self.terabox_token_input.setText(config.get("terabox_token", ""))
                self.terabox_username_input.setText(config.get("terabox_username", ""))
                self.terabox_password_input.setText(config.get("terabox_password", ""))
                
                self.n8n_url_input.setText(config.get("n8n_url", "http://localhost:5678"))
                self.n8n_token_input.setText(config.get("n8n_token", ""))
                self.n8n_webhook_input.setText(config.get("n8n_webhook", "/webhook"))
                
                self.docker_socket_input.setText(config.get("docker_socket", "/var/run/docker.sock"))
                self.docker_refresh_input.setValue(config.get("docker_refresh", 30))
                
                self.chunk_size_spin.setValue(config.get("chunk_size", 1000))
                self.chunk_overlap_spin.setValue(config.get("chunk_overlap", 200))
                self.vectorstore_path_input.setText(config.get("vectorstore_path", "vectorstore"))
                self.max_documents_spin.setValue(config.get("max_documents", 1000))
                
                self.projects_dir_input.setText(config.get("projects_dir", "projects"))
                self.backups_dir_input.setText(config.get("backups_dir", "backups"))
                self.notification_emails_input.setText(config.get("notification_emails", ""))
                
                self.encrypt_config_checkbox.setChecked(config.get("encrypt_config", False))
                self.auto_backup_checkbox.setChecked(config.get("auto_backup", True))
                self.log_actions_checkbox.setChecked(config.get("log_actions", True))
                
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
    
    def save_configuration(self):
        """Salva configuração completa do sistema"""
        try:
            config = {
                "openai_api_key": self.openai_key_input.text(),
                "model_name": self.model_name_combo.currentText(),
                
                "email_smtp": self.email_smtp_input.text(),
                "email_password": self.email_password_input.text(),
                "smtp_server": self.smtp_server_input.text(),
                "smtp_port": self.smtp_port_input.value(),
                
                "gdrive_client_id": self.gdrive_client_id_input.text(),
                "gdrive_client_secret": self.gdrive_client_secret_input.text(),
                "gdrive_refresh_token": self.gdrive_refresh_token_input.text(),
                
                "terabox_token": self.terabox_token_input.text(),
                "terabox_username": self.terabox_username_input.text(),
                "terabox_password": self.terabox_password_input.text(),
                
                "n8n_url": self.n8n_url_input.text(),
                "n8n_token": self.n8n_token_input.text(),
                "n8n_webhook": self.n8n_webhook_input.text(),
                
                "docker_socket": self.docker_socket_input.text(),
                "docker_refresh": self.docker_refresh_input.value(),
                
                "chunk_size": self.chunk_size_spin.value(),
                "chunk_overlap": self.chunk_overlap_spin.value(),
                "vectorstore_path": self.vectorstore_path_input.text(),
                "max_documents": self.max_documents_spin.value(),
                
                "projects_dir": self.projects_dir_input.text(),
                "backups_dir": self.backups_dir_input.text(),
                "notification_emails": self.notification_emails_input.text(),
                
                "encrypt_config": self.encrypt_config_checkbox.isChecked(),
                "auto_backup": self.auto_backup_checkbox.isChecked(),
                "log_actions": self.log_actions_checkbox.isChecked(),
                
                "saved_at": datetime.now().isoformat()
            }
            
            # Criar diretório de configuração
            config_dir = Path("config")
            config_dir.mkdir(exist_ok=True)
            
            # Salvar configuração
            config_file = config_dir / "system_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "Sucesso", "Configuração salva com sucesso!")
            
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao salvar configuração: {e}")
    
    def load_configuration(self):
        """Carrega configuração de arquivo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Carregar Configuração", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Aplicar configurações (similar ao load_saved_configuration)
                self.openai_key_input.setText(config.get("openai_api_key", ""))
                # ... aplicar todas as outras configurações
                
                QMessageBox.information(self, "Sucesso", "Configuração carregada")
                
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao carregar configuração: {e}")
    
    def test_configurations(self):
        """Testa todas as configurações"""
        results = []
        
        # Testar OpenAI
        if self.openai_key_input.text():
            results.append("✅ OpenAI API Key configurada")
        else:
            results.append("❌ OpenAI API Key não configurada")
        
        # Testar E-mail
        if self.email_smtp_input.text() and self.email_password_input.text():
            results.append("✅ Configurações de e-mail configuradas")
        else:
            results.append("❌ Configurações de e-mail incompletas")
        
        # Testar Google Drive
        if self.gdrive_client_id_input.text() and self.gdrive_client_secret_input.text():
            results.append("✅ Google Drive configurado")
        else:
            results.append("❌ Google Drive não configurado")
        
        # Testar Terabox
        if self.terabox_token_input.text():
            results.append("✅ Terabox configurado")
        else:
            results.append("❌ Terabox não configurado")
        
        # Testar N8N
        if self.n8n_url_input.text():
            results.append("✅ N8N URL configurada")
        else:
            results.append("❌ N8N URL não configurada")
        
        # Exibir resultados
        result_text = "\n".join(results)
        self.status_text.setPlainText(f"Teste de Configurações:\n\n{result_text}")
        
        QMessageBox.information(self, "Teste Concluído", f"Resultados:\n\n{result_text}")
    
    def reset_configurations(self):
        """Reseta todas as configurações"""
        reply = QMessageBox.question(
            self, "Confirmar Reset", 
            "Tem certeza que deseja resetar todas as configurações?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Limpar todos os campos
            self.openai_key_input.clear()
            self.email_smtp_input.clear()
            self.email_password_input.clear()
            self.gdrive_client_id_input.clear()
            self.gdrive_client_secret_input.clear()
            self.terabox_token_input.clear()
            self.n8n_token_input.clear()
            # ... limpar outros campos
            
            QMessageBox.information(self, "Sucesso", "Configurações resetadas")
    
    def create_projects_manager_tab(self):
        """Cria aba Projects Manager para exportação, backup e upload"""
        from projects_manager import ProjectsManager
        projects_widget = QWidget()
        layout = QVBoxLayout(projects_widget)
        # Header de busca
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Buscar Projeto:"))
        self.projects_search_input = QLineEdit()
        search_layout.addWidget(self.projects_search_input)
        self.projects_search_btn = QPushButton("Buscar")
        self.projects_search_btn.clicked.connect(self.search_projects_manager)
        search_layout.addWidget(self.projects_search_btn)
        layout.addLayout(search_layout)
        # Explorer de projetos
        self.projects_list = QListWidget()
        layout.addWidget(self.projects_list)
        # Botões de ação
        actions_layout = QHBoxLayout()
        self.export_project_btn = QPushButton("Exportar e Enviar")
        self.export_project_btn.clicked.connect(self.export_selected_project)
        actions_layout.addWidget(self.export_project_btn)
        self.restore_project_btn = QPushButton("Restaurar Backup")
        actions_layout.addWidget(self.restore_project_btn)
        self.refresh_projects_btn = QPushButton("Atualizar Lista")
        self.refresh_projects_btn.clicked.connect(self.refresh_projects_manager)
        actions_layout.addWidget(self.refresh_projects_btn)
        layout.addLayout(actions_layout)
        # Histórico de backups
        self.backup_history_list = QListWidget()
        layout.addWidget(QLabel("Histórico de Backups:"))
        layout.addWidget(self.backup_history_list)
        # Adicionar aba
        self.tab_widget.addTab(projects_widget, "📁 Projects Manager")
        # Inicializar ProjectsManager
        self.projects_manager = ProjectsManager()
        self.refresh_projects_manager()
    
    def refresh_projects_manager(self):
        """Atualiza lista de projetos e backups"""
        # Listar projetos locais (exemplo: ./projects)
        projects_dir = Path("projects")
        if not projects_dir.exists():
            projects_dir.mkdir()
        self.projects_list.clear()
        for p in projects_dir.iterdir():
            if p.is_dir():
                self.projects_list.addItem(p.name)
        # Listar backups
        self.backup_history_list.clear()
        for entry in self.projects_manager.list_backups():
            self.backup_history_list.addItem(f"{entry['project']} - {entry['date']}")
    
    def search_projects_manager(self):
        """Busca projetos pelo header"""
        query = self.projects_search_input.text().strip()
        self.projects_list.clear()
        for entry in self.projects_manager.search_projects(query):
            self.projects_list.addItem(Path(entry['project']).name)
    
    def export_selected_project(self):
        """Exporta e envia projeto selecionado"""
        current_item = self.projects_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Erro", "Selecione um projeto para exportar")
            return
        project_name = current_item.text()
        projects_dir = Path("projects")
        project_path = projects_dir / project_name
        # Solicitar e-mail destino
        email, ok = QInputDialog.getText(self, "E-mail", "Digite o(s) e-mail(s) para receber a senha (separados por vírgula):")
        if not ok or not email:
            return
        emails = [e.strip() for e in email.split(",") if e.strip()]
        try:
            entry = self.projects_manager.export_project(str(project_path), emails)
            QMessageBox.information(self, "Sucesso", f"Projeto exportado e enviado!\nRelatório: {entry['report']}")
            self.refresh_projects_manager()
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao exportar projeto: {e}")
    
    def setup_timers(self):
        """Configura timers para atualização automática"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all_data)
        self.refresh_timer.start(60000)  # Atualizar a cada 1 minuto
    
    def refresh_all_data(self):
        """Atualiza todos os dados"""
        self.refresh_containers()
        self.refresh_images()
        self.refresh_workflows()
        self.refresh_mcps()
        self.update_status()
    
    def update_status(self):
        """Atualiza status do sistema"""
        if self.knowledge_system:
            status = self.knowledge_system.get_system_status()
            self.system_status_label.setText(f"Status: {status['processed_documents']} docs, {status['queue_size']} na fila")
            
            # Atualizar texto de status
            status_text = f"""
Sistema de Conhecimento:
- Documentos processados: {status['processed_documents']}
- Base de conhecimento: {status['knowledge_base_size']} itens
- Análises realizadas: {len(status['analysis_results'])}
- Fila de processamento: {status['queue_size']}

Componentes:
- TensorFlow: {'✅' if status['tensorflow_available'] else '❌'}
- LangChain: {'✅' if status['langchain_available'] else '❌'}
- Processamento de documentos: {'✅' if status['document_processing_available'] else '❌'}
            """
            self.status_text.setPlainText(status_text)
    
    def upload_file(self):
        """Upload de arquivo individual"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo", "",
            "Todos os Arquivos (*);;PDF (*.pdf);;Word (*.docx *.doc);;Excel (*.xlsx *.xls);;PowerPoint (*.pptx *.ppt);;E-book (*.epub *.mobi);;Texto (*.txt *.md)"
        )
        
        if file_path and self.knowledge_system:
            # Adicionar à fila de processamento
            result = self.knowledge_system.add_document(file_path)
            
            # Adicionar à lista
            item = QListWidgetItem(f"📄 {Path(file_path).name}")
            item.setData(Qt.UserRole, result)
            self.documents_list.addItem(item)
            
            QMessageBox.information(self, "Sucesso", f"Arquivo adicionado: {Path(file_path).name}")
    
    def upload_folder(self):
        """Upload de pasta inteira"""
        folder_path = QFileDialog.getExistingDirectory(self, "Selecionar Pasta")
        
        if folder_path and self.knowledge_system:
            folder = Path(folder_path)
            supported_extensions = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.epub', '.txt', '.md']
            
            files_added = 0
            for file_path in folder.rglob("*"):
                if file_path.suffix.lower() in supported_extensions:
                    result = self.knowledge_system.add_document(str(file_path))
                    
                    item = QListWidgetItem(f"📄 {file_path.name}")
                    item.setData(Qt.UserRole, result)
                    self.documents_list.addItem(item)
                    
                    files_added += 1
            
            QMessageBox.information(self, "Sucesso", f"{files_added} arquivos adicionados da pasta")
    
    def query_knowledge(self):
        """Consulta a base de conhecimento"""
        question = self.query_input.toPlainText().strip()
        
        if not question:
            QMessageBox.warning(self, "Erro", "Digite uma pergunta")
            return
        
        if not self.knowledge_system:
            QMessageBox.warning(self, "Erro", "Sistema de conhecimento não disponível")
            return
        
        # Executar consulta em background
        self.worker = KnowledgeWorker(self.knowledge_system, "query_knowledge", question)
        self.worker.result_ready.connect(self.handle_query_result)
        self.worker.status_updated.connect(self.statusBar().showMessage)
        self.worker.start()
    
    def handle_query_result(self, result):
        """Processa resultado da consulta"""
        if "error" in result:
            self.results_text.setPlainText(f"Erro: {result['error']}")
        else:
            response = f"""
Pergunta: {result.get('question', 'N/A')}

Resposta: {result.get('answer', 'N/A')}

Documentos de referência:
{chr(10).join([f"- {doc}" for doc in result.get('source_documents', [])])}
            """
            self.results_text.setPlainText(response)
    
    def analyze_documents(self):
        """Analisa documentos com TensorFlow"""
        if not self.knowledge_system:
            QMessageBox.warning(self, "Erro", "Sistema de conhecimento não disponível")
            return
        
        n_clusters = self.clusters_spin.value()
        
        # Executar análise em background
        self.worker = KnowledgeWorker(self.knowledge_system, "analyze_documents", n_clusters)
        self.worker.result_ready.connect(self.handle_analysis_result)
        self.worker.status_updated.connect(self.statusBar().showMessage)
        self.worker.start()
    
    def handle_analysis_result(self, result):
        """Processa resultado da análise"""
        if "error" in result:
            self.analysis_results_text.setPlainText(f"Erro: {result['error']}")
        else:
            analysis_text = f"""
Análise de Documentos:
- Total de documentos: {result.get('total_documents', 0)}
- Número de clusters: {result.get('n_clusters', 0)}

Clusters encontrados:
"""
            for cluster_name, cluster_data in result.get('clusters', {}).items():
                analysis_text += f"\n{cluster_name}:\n"
                for doc in cluster_data:
                    analysis_text += f"  - {doc['text']}\n"
            
            self.analysis_results_text.setPlainText(analysis_text)
    
    def analyze_sentiment(self):
        """Analisa sentimento dos documentos"""
        if not self.knowledge_system or not self.knowledge_system.knowledge_base:
            QMessageBox.warning(self, "Erro", "Nenhum documento disponível para análise")
            return
        
        # Usar TensorFlow para análise de sentimento
        if hasattr(self.knowledge_system, 'tensorflow_analyzer'):
            results = self.knowledge_system.tensorflow_analyzer.analyze_sentiment(
                self.knowledge_system.knowledge_base[:10]  # Primeiros 10 documentos
            )
            
            sentiment_text = "Análise de Sentimento:\n\n"
            for result in results:
                sentiment_text += f"Texto: {result.get('text', 'N/A')}\n"
                sentiment_text += f"Sentimento: {result.get('sentiment', 'N/A')}\n"
                sentiment_text += f"Score: {result.get('score', 0):.2f}\n"
                sentiment_text += f"Palavras positivas: {result.get('positive_words', 0)}\n"
                sentiment_text += f"Palavras negativas: {result.get('negative_words', 0)}\n"
                sentiment_text += "-" * 50 + "\n"
            
            self.sentiment_results_text.setPlainText(sentiment_text)
    
    def refresh_containers(self):
        """Atualiza lista de containers"""
        if not self.docker_manager:
            return
        
        containers = self.docker_manager.get_containers()
        
        self.containers_table.setRowCount(len(containers))
        for i, container in enumerate(containers):
            self.containers_table.setItem(i, 0, QTableWidgetItem(container['id'][:12]))
            self.containers_table.setItem(i, 1, QTableWidgetItem(container['name']))
            self.containers_table.setItem(i, 2, QTableWidgetItem(container['status']))
            self.containers_table.setItem(i, 3, QTableWidgetItem(container['image']))
            self.containers_table.setItem(i, 4, QTableWidgetItem(str(container['ports'])))
    
    def refresh_images(self):
        """Atualiza lista de imagens"""
        if not self.docker_manager:
            return
        
        images = self.docker_manager.get_images()
        
        self.images_table.setRowCount(len(images))
        for i, image in enumerate(images):
            self.images_table.setItem(i, 0, QTableWidgetItem(image['id'][:12]))
            self.images_table.setItem(i, 1, QTableWidgetItem(', '.join(image['tags'])))
            self.images_table.setItem(i, 2, QTableWidgetItem(f"{image['size'] / 1024 / 1024:.1f} MB"))
            self.images_table.setItem(i, 3, QTableWidgetItem(image['created'][:10]))
    
    def refresh_workflows(self):
        """Atualiza lista de workflows"""
        if not self.n8n_manager or not self.n8n_manager.test_connection():
            return
        
        workflows = self.n8n_manager.get_workflows()
        
        self.workflows_list.clear()
        for workflow in workflows:
            item = QListWidgetItem(f"🔄 {workflow.get('name', 'Unnamed')} ({workflow.get('id', 'N/A')})")
            item.setData(Qt.UserRole, workflow)
            self.workflows_list.addItem(item)
    
    def refresh_mcps(self):
        """Atualiza lista de MCPs"""
        if not self.mcp_integration:
            return
        
        self.mcps_tree.clear()
        
        for mcp_id, mcp_name in self.mcp_integration.available_mcps.items():
            item = QTreeWidgetItem(self.mcps_tree)
            item.setText(0, f"🔌 {mcp_name} ({mcp_id})")
            item.setData(0, Qt.UserRole, mcp_id)
    
    def start_container(self):
        """Inicia container selecionado"""
        current_row = self.containers_table.currentRow()
        if current_row >= 0 and self.docker_manager:
            container_id = self.containers_table.item(current_row, 0).text()
            if self.docker_manager.start_container(container_id):
                QMessageBox.information(self, "Sucesso", "Container iniciado")
                self.refresh_containers()
    
    def stop_container(self):
        """Para container selecionado"""
        current_row = self.containers_table.currentRow()
        if current_row >= 0 and self.docker_manager:
            container_id = self.containers_table.item(current_row, 0).text()
            if self.docker_manager.stop_container(container_id):
                QMessageBox.information(self, "Sucesso", "Container parado")
                self.refresh_containers()
    
    def run_image(self):
        """Executa imagem selecionada"""
        current_row = self.images_table.currentRow()
        if current_row >= 0 and self.docker_manager:
            image_tags = self.images_table.item(current_row, 1).text()
            if image_tags:
                image_name = image_tags.split(',')[0]
                container_id = self.docker_manager.run_container(image_name)
                if container_id:
                    QMessageBox.information(self, "Sucesso", f"Container executado: {container_id}")
                    self.refresh_containers()
    
    def connect_n8n(self):
        """Conecta ao N8N"""
        if not self.n8n_manager:
            return
        
        url = self.n8n_url_input.text()
        token = self.n8n_token_input.text()
        
        self.n8n_manager = N8NManager(url, token)
        
        if self.n8n_manager.test_connection():
            QMessageBox.information(self, "Sucesso", "Conectado ao N8N")
            self.refresh_workflows()
        else:
            QMessageBox.warning(self, "Erro", "Falha ao conectar com N8N")
    
    def create_workflow(self):
        """Cria novo workflow"""
        QMessageBox.information(self, "Info", "Funcionalidade em desenvolvimento")
    
    def activate_workflow(self):
        """Ativa workflow selecionado"""
        current_item = self.workflows_list.currentItem()
        if current_item and self.n8n_manager:
            workflow = current_item.data(Qt.UserRole)
            if self.n8n_manager.activate_workflow(workflow['id']):
                QMessageBox.information(self, "Sucesso", "Workflow ativado")
                self.refresh_workflows()
    
    def create_mcp_workflow(self):
        """Cria workflow com integração MCP"""
        if not self.mcp_integration:
            return
        
        workflow_type = self.workflow_type_combo.currentText()
        
        if workflow_type == "Webhook":
            workflow = self.mcp_integration.create_webhook_workflow(
                "http://localhost:5678/webhook",
                {"test": "data"}
            )
        elif workflow_type == "Data Architecture":
            workflow = self.mcp_integration.create_data_architecture_workflow(
                "postgres", "filesystem"
            )
        elif workflow_type == "Knowledge Processing":
            workflow = {
                "name": "Knowledge Processing Workflow",
                "nodes": [
                    {
                        "id": "knowledge_input",
                        "type": "n8n-nodes-base.webhook",
                        "position": [240, 300],
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "knowledge",
                            "responseMode": "responseNode"
                        }
                    },
                    {
                        "id": "knowledge_processor",
                        "type": "n8n-nodes-base.function",
                        "position": [460, 300],
                        "parameters": {
                            "functionCode": """
                            // Processar conhecimento com MCPs
                            const data = $input.first().json;
                            
                            // Integrar com sistema de conhecimento
                            // Aqui você pode chamar APIs do sistema
                            
                            return {
                                json: {
                                    processed: true,
                                    knowledge_enhanced: true,
                                    timestamp: new Date().toISOString(),
                                    data: data
                                }
                            };
                            """
                        }
                    }
                ],
                "connections": {
                    "knowledge_input": {
                        "main": [
                            [
                                {
                                    "node": "knowledge_processor",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                }
            }
        else:
            workflow = {"name": "Custom Workflow", "nodes": []}
        
        QMessageBox.information(self, "Sucesso", f"Workflow MCP '{workflow_type}' criado")
    
    def quick_analysis(self):
        """Análise rápida do sistema"""
        if not self.knowledge_system:
            return
        
        # Executar análise rápida
        self.analyze_documents()
        self.analyze_sentiment()
        
        QMessageBox.information(self, "Análise", "Análise rápida iniciada")

def main():
    """Função principal"""
    if not PYQT5_AVAILABLE:
        print("❌ PyQt5 não disponível. Instale com: pip install PyQt5")
        return
    
    if not KNOWLEDGE_SYSTEM_AVAILABLE:
        print("❌ Sistema de conhecimento não disponível")
        return
    
    app = QApplication(sys.argv)
    
    # Configurar estilo
    app.setStyle('Fusion')
    
    # Criar e mostrar interface
    interface = IntegratedKnowledgeInterface()
    interface.show()
    
    # Executar aplicação
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 