#!/usr/bin/env python3
"""
Interface Gráfica Integrada para AiAgenteMCP
Configuração da API OpenRouter e Sistema RAG
"""

import sys
import os
import json
import threading
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QTextEdit, QTabWidget, QFileDialog, QMessageBox,
                           QGroupBox, QComboBox, QTableWidget, QTableWidgetItem,
                           QHeaderView, QProgressBar, QCheckBox, QSpinBox,
                           QSplitter, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QPixmap, QPainter, QBrush
from datetime import datetime

# Importar o gerenciador de configurações
try:
    from config_manager import ConfigManager
    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    print("⚠️  Aviso: Módulo ConfigManager não encontrado. Funcionalidades de backup estarão desabilitadas.")
    CONFIG_MANAGER_AVAILABLE = False
    ConfigManager = None

# Importar o novo widget da aba de configurações
try:
    from config_ui import ConfigBackupTab
    CONFIG_UI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Aviso: Módulo config_ui não encontrado. A aba de configurações não estará disponível. Erro: {e}")
    CONFIG_UI_AVAILABLE = False
    ConfigBackupTab = None

# Importar o agente e sistema RAG com LangChain
try:
    from ai_agente_mcp import AiAgenteMCP
    from rag_system_langchain import RAGSystemLangChain as RAGSystem
    LANGCHAIN_AVAILABLE = True
    print("✅ Sistema RAG com LangChain carregado com sucesso")
except ImportError as e:
    print(f"⚠️  Aviso: LangChain não disponível: {e}")
    print("Tentando carregar sistema RAG original...")
    try:
        from rag_system import RAGSystem
        LANGCHAIN_AVAILABLE = False
        print("✅ Sistema RAG original carregado (modo de compatibilidade)")
    except ImportError as e2:
        print(f"❌ Erro: Nenhum sistema RAG disponível: {e2}")
        print("A interface funcionará em modo limitado")
        LANGCHAIN_AVAILABLE = False
        AiAgenteMCP = None
        RAGSystem = None

class DarkTheme:
    """Tema escuro para programadores - Mesmo tema do Editor UI/UX"""
    
    # Cores principais
    BLACK = QColor(18, 18, 18)           # Preto profundo
    DARK_GRAY = QColor(30, 30, 30)       # Cinza grafite escuro
    GRAY = QColor(45, 45, 45)            # Cinza grafite médio
    LIGHT_GRAY = QColor(60, 60, 60)      # Cinza grafite claro
    WHITE = QColor(255, 255, 255)        # Branco
    GREEN = QColor(0, 255, 127)          # Verde
    BLUE = QColor(0, 191, 255)           # Azul
    YELLOW = QColor(255, 255, 0)         # Amarelo
    ORANGE = QColor(255, 165, 0)         # Laranja
    CYAN = QColor(0, 255, 255)           # Ciano
    
    # Cores de botões (mais escuros)
    BUTTON_DARK = QColor(25, 25, 25)
    BUTTON_HOVER = QColor(40, 40, 40)
    BUTTON_PRESSED = QColor(20, 20, 20)
    
    @staticmethod
    def apply_theme(app):
        """Aplicar tema escuro à aplicação"""
        palette = QPalette()
        
        # Cores principais
        palette.setColor(QPalette.Window, DarkTheme.BLACK)
        palette.setColor(QPalette.WindowText, DarkTheme.WHITE)
        palette.setColor(QPalette.Base, DarkTheme.DARK_GRAY)
        palette.setColor(QPalette.AlternateBase, DarkTheme.GRAY)
        palette.setColor(QPalette.ToolTipBase, DarkTheme.BLACK)
        palette.setColor(QPalette.ToolTipText, DarkTheme.WHITE)
        palette.setColor(QPalette.Text, DarkTheme.WHITE)
        palette.setColor(QPalette.Button, DarkTheme.BUTTON_DARK)
        palette.setColor(QPalette.ButtonText, DarkTheme.WHITE)
        palette.setColor(QPalette.BrightText, DarkTheme.GREEN)
        palette.setColor(QPalette.Link, DarkTheme.BLUE)
        palette.setColor(QPalette.Highlight, DarkTheme.BLUE)
        palette.setColor(QPalette.HighlightedText, DarkTheme.WHITE)
        
        app.setPalette(palette)
        
        # Estilo CSS adicional
        app.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
                color: white;
            }
            
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #1e1e1e;
            }
            
            QTabBar::tab {
                background-color: #2d2d2d;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #007acc;
                color: white;
            }
            
            QTabBar::tab:hover {
                background-color: #404040;
            }
            
            QPushButton {
                background-color: #191919;
                border: 1px solid #404040;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #282828;
                border-color: #007acc;
            }
            
            QPushButton:pressed {
                background-color: #141414;
            }
            
            QPushButton:disabled {
                background-color: #1a1a1a;
                color: #666666;
            }
            
            QLineEdit, QTextEdit, QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                color: white;
                padding: 6px;
                border-radius: 4px;
            }
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #007acc;
            }
            
            QListWidget, QTreeWidget, QTableWidget {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                color: white;
                alternate-background-color: #252525;
            }
            
            QListWidget::item, QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #333333;
            }
            
            QListWidget::item:selected, QTreeWidget::item:selected {
                background-color: #007acc;
                color: white;
            }
            
            QListWidget::item:hover, QTreeWidget::item:hover {
                background-color: #404040;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #00ff7f;
            }
            
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #404040;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #007acc;
            }
            
            QStatusBar {
                background-color: #1e1e1e;
                color: white;
                border-top: 1px solid #404040;
            }
            
            QMenuBar {
                background-color: #1e1e1e;
                color: white;
                border-bottom: 1px solid #404040;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
            }
            
            QMenuBar::item:selected {
                background-color: #007acc;
            }
            
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 4px;
                text-align: center;
                background-color: #2d2d2d;
                color: white;
            }
            
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 3px;
            }
            
            QSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                color: white;
                padding: 4px;
                border-radius: 4px;
            }
            
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 2px;
            }
            
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #007acc;
            }
            
            QCheckBox {
                color: white;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #404040;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
            
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border-color: #007acc;
            }
            
            QCheckBox::indicator:hover {
                border-color: #007acc;
            }
            
            QHeaderView::section {
                background-color: #2d2d2d;
                color: white;
                padding: 6px;
                border: 1px solid #404040;
                font-weight: bold;
            }
            
            QHeaderView::section:hover {
                background-color: #404040;
            }
        """)

class AiAgentGUI(QMainWindow):
    """Interface gráfica principal do AiAgenteMCP"""
    
    def __init__(self):
        super().__init__()
        self.agent = None
        self.rag_system = None
        self.init_ui()
        self.load_agent()
        self.load_rag_system()
        self.load_mcp_manager()
    
    def init_ui(self):
        """Inicializa a interface gráfica"""
        self.setWindowTitle("🤖 AiAgenteMCP - Sistema Integrado de Conhecimento")
        self.setGeometry(100, 100, 1400, 900)
        
        # Definir ícone da aplicação (robô)
        self.setWindowIcon(self.create_robot_icon())
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Criar abas
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Aba do sistema RAG
        self.create_rag_tab()
        
        # Aba de gerenciamento de MCPs
        self.create_mcp_management_tab()
        
        # Aba de teste do agente
        self.create_agent_test_tab()
        
        # Aba de gerenciamento do Cursor
        self.create_cursor_mcp_tab()
        
        # Aba de Prompt Manager
        self.create_prompt_manager_tab()
        
        # Aba de Configurações Gerais e Backup
        self.create_settings_backup_tab()
        
        # Status bar
        self.statusBar().showMessage("🤖 Sistema Integrado de Conhecimento - Pronto")
    
    def create_robot_icon(self):
        """Cria um ícone de robô simples para a aplicação"""
        # Criar um pixmap 32x32
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Cabeça do robô (círculo cinza)
        painter.setBrush(QBrush(DarkTheme.LIGHT_GRAY))
        painter.drawEllipse(4, 4, 24, 24)
        
        # Olhos (círculos azuis)
        painter.setBrush(QBrush(DarkTheme.BLUE))
        painter.drawEllipse(10, 12, 4, 4)
        painter.drawEllipse(18, 12, 4, 4)
        
        # Boca (retângulo verde)
        painter.setBrush(QBrush(DarkTheme.GREEN))
        painter.drawRect(12, 18, 8, 2)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def create_api_config_tab(self):
        """
        Esta função foi descontinuada. A configuração de API agora está na aba 'Configurações e Backup'.
        Retorna um QWidget vazio.
        """
        return QWidget()
    
    def create_rag_tab(self):
        """Cria a aba do sistema RAG"""
        rag_widget = QWidget()
        layout = QVBoxLayout(rag_widget)
        
        # Splitter para dividir a interface
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Painel esquerdo - Upload e gerenciamento de documentos
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Grupo de upload
        upload_group = QGroupBox("📄 Upload de Documentos")
        upload_layout = QVBoxLayout(upload_group)
        
        # Botão para selecionar PDF
        self.select_pdf_btn = QPushButton("📁 Selecionar PDF")
        self.select_pdf_btn.clicked.connect(self.select_pdf_file)
        upload_layout.addWidget(self.select_pdf_btn)
        
        # Progress bar para upload
        self.upload_progress = QProgressBar()
        self.upload_progress.setVisible(False)
        upload_layout.addWidget(self.upload_progress)
        
        # Lista de documentos
        docs_group = QGroupBox("📚 Documentos Processados")
        docs_layout = QVBoxLayout(docs_group)
        
        self.documents_list = QListWidget()
        docs_layout.addWidget(self.documents_list)
        
        # Botões de gerenciamento
        docs_buttons_layout = QHBoxLayout()
        
        self.refresh_docs_btn = QPushButton("🔄 Atualizar Lista")
        self.refresh_docs_btn.clicked.connect(self.refresh_documents_list)
        docs_buttons_layout.addWidget(self.refresh_docs_btn)
        
        self.remove_doc_btn = QPushButton("🗑️ Remover Selecionado")
        self.remove_doc_btn.clicked.connect(self.remove_selected_document)
        docs_buttons_layout.addWidget(self.remove_doc_btn)
        
        self.clear_all_btn = QPushButton("🧹 Limpar Todos")
        self.clear_all_btn.clicked.connect(self.clear_all_documents)
        docs_buttons_layout.addWidget(self.clear_all_btn)
        
        docs_layout.addLayout(docs_buttons_layout)
        
        left_layout.addWidget(upload_group)
        left_layout.addWidget(docs_group)
        
        # Painel direito - Busca e resultados
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Grupo de busca
        search_group = QGroupBox("🔍 Busca Semântica")
        search_layout = QVBoxLayout(search_group)
        
        # Campo de busca
        search_layout.addWidget(QLabel("❓ Query:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite sua pergunta...")
        search_layout.addWidget(self.search_input)
        
        # Configurações de busca
        search_config_layout = QHBoxLayout()
        search_config_layout.addWidget(QLabel("📊 Resultados:"))
        self.top_k_spin = QSpinBox()
        self.top_k_spin.setRange(1, 20)
        self.top_k_spin.setValue(5)
        search_config_layout.addWidget(self.top_k_spin)
        search_config_layout.addStretch()
        
        self.search_btn = QPushButton("🔍 Buscar")
        self.search_btn.clicked.connect(self.perform_search)
        search_config_layout.addWidget(self.search_btn)
        
        search_layout.addLayout(search_config_layout)
        
        # Resultados da busca
        search_layout.addWidget(QLabel("📋 Resultados:"))
        self.search_results = QTextEdit()
        self.search_results.setReadOnly(True)
        search_layout.addWidget(self.search_results)
        
        right_layout.addWidget(search_group)
        
        # Adicionar painéis ao splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        # Adicionar aba
        self.tab_widget.addTab(rag_widget, "🧠 Sistema RAG")
    
    def create_agent_test_tab(self):
        """Cria a aba de teste do agente"""
        test_widget = QWidget()
        layout = QVBoxLayout(test_widget)
        
        # Status do agente
        status_group = QGroupBox("🤖 Status do Agente")
        status_layout = QVBoxLayout(status_group)
        
        self.agent_status_text = QTextEdit()
        self.agent_status_text.setMaximumHeight(150)
        self.agent_status_text.setReadOnly(True)
        status_layout.addWidget(self.agent_status_text)
        
        self.refresh_status_btn = QPushButton("🔄 Atualizar Status")
        self.refresh_status_btn.clicked.connect(self.refresh_agent_status)
        status_layout.addWidget(self.refresh_status_btn)
        
        layout.addWidget(status_group)
        
        # Chat com o agente
        chat_group = QGroupBox("💬 Chat com o Agente")
        chat_layout = QVBoxLayout(chat_group)
        
        # Área de chat
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        chat_layout.addWidget(self.chat_area)
        
        # Input de mensagem
        message_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Digite sua mensagem...")
        self.message_input.returnPressed.connect(self.send_message)
        message_layout.addWidget(self.message_input)
        
        self.send_btn = QPushButton("📤 Enviar")
        self.send_btn.clicked.connect(self.send_message)
        message_layout.addWidget(self.send_btn)
        
        chat_layout.addLayout(message_layout)
        
        layout.addWidget(chat_group)
        
        # Adicionar aba
        self.tab_widget.addTab(test_widget, "🧪 Teste do Agente")
    
    def create_mcp_management_tab(self):
        """Cria a aba de gerenciamento de MCPs"""
        mcp_widget = QWidget()
        layout = QVBoxLayout(mcp_widget)
        
        # Splitter para dividir a interface
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Painel esquerdo - Lista de MCPs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Grupo de MCPs
        mcps_group = QGroupBox("🔌 MCPs Disponíveis")
        mcps_layout = QVBoxLayout(mcps_group)
        
        # Tabela de MCPs
        self.mcps_table = QTableWidget()
        self.mcps_table.setColumnCount(6)
        self.mcps_table.setHorizontalHeaderLabels([
            "Nome", "Status", "Porta", "Categoria", "Método", "Descrição"
        ])
        mcps_layout.addWidget(self.mcps_table)
        
        # Botões de controle
        mcp_buttons_layout = QHBoxLayout()
        
        self.install_mcp_btn = QPushButton("📦 Instalar Selecionado")
        self.install_mcp_btn.clicked.connect(self.install_selected_mcp)
        mcp_buttons_layout.addWidget(self.install_mcp_btn)
        
        self.start_mcp_btn = QPushButton("▶️ Iniciar Selecionado")
        self.start_mcp_btn.clicked.connect(self.start_selected_mcp)
        mcp_buttons_layout.addWidget(self.start_mcp_btn)
        
        self.stop_mcp_btn = QPushButton("⏹️ Parar Selecionado")
        self.stop_mcp_btn.clicked.connect(self.stop_selected_mcp)
        mcp_buttons_layout.addWidget(self.stop_mcp_btn)
        
        self.refresh_mcps_btn = QPushButton("🔄 Atualizar")
        self.refresh_mcps_btn.clicked.connect(self.refresh_mcps_list)
        mcp_buttons_layout.addWidget(self.refresh_mcps_btn)
        
        mcps_layout.addLayout(mcp_buttons_layout)
        
        # Botões de instalação avançada
        advanced_buttons_layout = QHBoxLayout()
        
        self.install_github_btn = QPushButton("🐙 Instalar do GitHub")
        self.install_github_btn.clicked.connect(self.install_from_github)
        advanced_buttons_layout.addWidget(self.install_github_btn)
        
        self.search_alternatives_btn = QPushButton("🔍 Buscar Alternativas")
        self.search_alternatives_btn.clicked.connect(self.search_mcp_alternatives)
        advanced_buttons_layout.addWidget(self.search_alternatives_btn)
        
        self.install_custom_btn = QPushButton("⚙️ Instalar Customizado")
        self.install_custom_btn.clicked.connect(self.install_custom_mcp)
        advanced_buttons_layout.addWidget(self.install_custom_btn)
        
        mcps_layout.addLayout(advanced_buttons_layout)
        
        left_layout.addWidget(mcps_group)
        
        # Painel direito - Ollama e análise
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Grupo Ollama
        ollama_group = QGroupBox("🦙 Modelos Ollama")
        ollama_layout = QVBoxLayout(ollama_group)
        
        # Lista de modelos
        self.ollama_list = QListWidget()
        ollama_layout.addWidget(self.ollama_list)
        
        # Botões Ollama
        ollama_buttons_layout = QHBoxLayout()
        
        self.install_ollama_btn = QPushButton("📥 Instalar Modelo")
        self.install_ollama_btn.clicked.connect(self.install_ollama_model)
        ollama_buttons_layout.addWidget(self.install_ollama_btn)
        
        self.remove_ollama_btn = QPushButton("🗑️ Remover Modelo")
        self.remove_ollama_btn.clicked.connect(self.remove_ollama_model)
        ollama_buttons_layout.addWidget(self.remove_ollama_btn)
        
        self.refresh_ollama_btn = QPushButton("🔄 Atualizar")
        self.refresh_ollama_btn.clicked.connect(self.load_ollama_models)
        ollama_buttons_layout.addWidget(self.refresh_ollama_btn)
        
        ollama_layout.addLayout(ollama_buttons_layout)
        
        right_layout.addWidget(ollama_group)
        
        # Grupo de análise
        analysis_group = QGroupBox("📊 Análise e Gerenciamento")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.analyze_mcps_btn = QPushButton("🔍 Analisar MCPs")
        self.analyze_mcps_btn.clicked.connect(self.analyze_and_manage_mcps)
        analysis_layout.addWidget(self.analyze_mcps_btn)
        
        right_layout.addWidget(analysis_group)
        right_layout.addStretch()
        
        # Adicionar painéis ao splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([800, 400])
        
        # Adicionar aba
        self.tab_widget.addTab(mcp_widget, "🔌 Gerenciamento MCPs")
        
        # Carregar dados iniciais
        self.load_mcp_manager()
        self.refresh_mcps_list()
        self.load_ollama_models()
    
    def create_cursor_mcp_tab(self):
        """Cria a aba de gerenciamento do Cursor"""
        cursor_widget = QWidget()
        layout = QVBoxLayout(cursor_widget)
        
        # Grupo de configuração do Cursor
        cursor_group = QGroupBox("🎯 Configuração do Cursor")
        cursor_layout = QVBoxLayout(cursor_group)
        
        cursor_layout.addWidget(QLabel("⚙️ Configuração do Cursor:"))
        self.cursor_config_input = QTextEdit()
        self.cursor_config_input.setMaximumHeight(100)
        cursor_layout.addWidget(self.cursor_config_input)
        
        # Botões de ação
        cursor_buttons_layout = QHBoxLayout()
        
        self.save_cursor_config_btn = QPushButton("💾 Salvar Configuração")
        self.save_cursor_config_btn.clicked.connect(self.save_cursor_configuration)
        cursor_buttons_layout.addWidget(self.save_cursor_config_btn)
        
        self.load_cursor_config_btn = QPushButton("📂 Carregar Configuração")
        self.load_cursor_config_btn.clicked.connect(self.load_cursor_config)
        cursor_buttons_layout.addWidget(self.load_cursor_config_btn)
        
        cursor_layout.addLayout(cursor_buttons_layout)
        
        # Adicionar grupo ao layout principal
        layout.addWidget(cursor_group)
        
        # Adicionar aba
        self.tab_widget.addTab(cursor_widget, "🎯 Gerenciamento do Cursor")
    
    def create_prompt_manager_tab(self):
        """Cria a aba de gerenciamento de Prompt Manager"""
        prompt_manager_widget = QWidget()
        layout = QVBoxLayout(prompt_manager_widget)
        
        # Splitter para dividir a interface
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Painel esquerdo - Categorias e Prompts
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Grupo de categorias
        categories_group = QGroupBox("📂 Categorias de Prompts")
        categories_layout = QVBoxLayout(categories_group)
        
        # Dropdown de categorias
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("🔖 Categoria:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Lovable",
            "Leonardo AI", 
            "V03 Google",
            "Cursor",
            "VS Code",
            "Wandsurf",
            "Trae",
            "GitHub Copilot Pro"
        ])
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        category_layout.addWidget(self.category_combo)
        
        # Botões de categoria
        self.add_category_btn = QPushButton("➕ Nova Categoria")
        self.add_category_btn.clicked.connect(self.add_new_category)
        category_layout.addWidget(self.add_category_btn)
        
        categories_layout.addLayout(category_layout)
        
        # Lista de prompts da categoria
        categories_layout.addWidget(QLabel("📝 Prompts da Categoria:"))
        self.prompts_list = QListWidget()
        self.prompts_list.itemClicked.connect(self.on_prompt_selected)
        categories_layout.addWidget(self.prompts_list)
        
        # Botões de prompt
        prompt_buttons_layout = QHBoxLayout()
        
        self.add_prompt_btn = QPushButton("➕ Novo Prompt")
        self.add_prompt_btn.clicked.connect(self.add_new_prompt)
        prompt_buttons_layout.addWidget(self.add_prompt_btn)
        
        self.edit_prompt_btn = QPushButton("✏️ Editar")
        self.edit_prompt_btn.clicked.connect(self.edit_selected_prompt)
        prompt_buttons_layout.addWidget(self.edit_prompt_btn)
        
        self.delete_prompt_btn = QPushButton("🗑️ Excluir")
        self.delete_prompt_btn.clicked.connect(self.delete_selected_prompt)
        prompt_buttons_layout.addWidget(self.delete_prompt_btn)
        
        categories_layout.addLayout(prompt_buttons_layout)
        
        left_layout.addWidget(categories_group)
        
        # Painel direito - Conteúdo e Busca
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Grupo de conteúdo do prompt
        content_group = QGroupBox("📄 Conteúdo do Prompt")
        content_layout = QVBoxLayout(content_group)
        
        self.prompt_content = QTextEdit()
        self.prompt_content.setPlaceholderText("Selecione um prompt para ver seu conteúdo...")
        content_layout.addWidget(self.prompt_content)
        
        # Botões de ação do prompt
        content_buttons_layout = QHBoxLayout()
        
        self.copy_prompt_btn = QPushButton("📋 Copiar")
        self.copy_prompt_btn.clicked.connect(self.copy_prompt_content)
        content_buttons_layout.addWidget(self.copy_prompt_btn)
        
        self.export_prompt_btn = QPushButton("📤 Exportar")
        self.export_prompt_btn.clicked.connect(self.export_prompt)
        content_buttons_layout.addWidget(self.export_prompt_btn)
        
        self.rate_prompt_btn = QPushButton("⭐ Avaliar")
        self.rate_prompt_btn.clicked.connect(self.rate_selected_prompt)
        content_buttons_layout.addWidget(self.rate_prompt_btn)
        
        content_layout.addLayout(content_buttons_layout)
        
        right_layout.addWidget(content_group)
        
        # Grupo de busca de documentação
        docs_group = QGroupBox("🔍 Busca de Documentação")
        docs_layout = QVBoxLayout(docs_group)
        
        # Campo de busca
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Buscar:"))
        self.docs_search_input = QLineEdit()
        self.docs_search_input.setPlaceholderText("Digite o que buscar na documentação...")
        search_layout.addWidget(self.docs_search_input)
        
        self.search_docs_btn = QPushButton("🔍 Buscar Docs")
        self.search_docs_btn.clicked.connect(self.search_documentation)
        search_layout.addWidget(self.search_docs_btn)
        
        docs_layout.addLayout(search_layout)
        
        # Resultados da busca
        docs_layout.addWidget(QLabel("📚 Documentos Encontrados:"))
        self.docs_results = QTextEdit()
        self.docs_results.setReadOnly(True)
        self.docs_results.setMaximumHeight(150)
        docs_layout.addWidget(self.docs_results)
        
        # Botão de melhoria
        self.improve_prompt_btn = QPushButton("✨ Melhorar Prompt com Docs")
        self.improve_prompt_btn.clicked.connect(self.improve_prompt_with_docs)
        docs_layout.addWidget(self.improve_prompt_btn)
        
        right_layout.addWidget(docs_group)
        
        # Grupo de estatísticas
        stats_group = QGroupBox("📊 Estatísticas")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("• Total de prompts: 0\n• Categorias: 8\n• Prompt mais usado: N/A\n• Melhor avaliado: N/A")
        stats_layout.addWidget(self.stats_label)
        
        right_layout.addWidget(stats_group)
        right_layout.addStretch()
        
        # Adicionar painéis ao splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        # Adicionar aba
        self.tab_widget.addTab(prompt_manager_widget, "💬 Prompt Manager")
        
        # Carregar dados iniciais
        self.load_prompt_categories()
        self.on_category_changed(self.category_combo.currentText())
    
    def create_settings_backup_tab(self):
        """Cria a aba de Configurações Gerais e Backup - Versão Expandida"""
        try:
            # Usar a versão expandida com todas as funcionalidades
            from config_ui_expanded import ConfigBackupTabExpanded
            self.config_backup_tab = ConfigBackupTabExpanded()
            
            # Conectar sinais corretos
            self.config_backup_tab.agent_reload_needed.connect(self.on_agent_reload_needed)
            self.config_backup_tab.backup_finished.connect(self.on_backup_finished)
            
            # Conectar sinais internos do ConfigBackupTab
            self.config_backup_tab.connect_signals()
            
            # Adicionar aba
            self.tab_widget.addTab(self.config_backup_tab, "⚙️ Configurações & Backup")
            
        except ImportError as e:
            # Fallback se ConfigBackupTabExpanded não estiver disponível
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Título
            title = QLabel("⚙️ Configurações Gerais e Backup")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff7f; margin: 10px;")
            layout.addWidget(title)
            
            # Aviso
            warning = QLabel(f"⚠️ Interface expandida não disponível: {e}\nUsando modo simplificado.")
            warning.setStyleSheet("color: #ff6b6b; margin: 10px;")
            layout.addWidget(warning)
            
            # Botão EditorUiUX como fallback
            editor_btn = QPushButton("🎨 Abrir Editor UI/UX")
            editor_btn.clicked.connect(self.open_editor_uiux)
            editor_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #005a9e;
                }
            """)
            layout.addWidget(editor_btn)
            
            layout.addStretch()
            
            # Adicionar aba
            self.tab_widget.addTab(tab, "⚙️ Configurações & Backup")
    
    def add_editor_uiux_button(self):
        """Adiciona o botão EditorUiUX à aba de configurações"""
        if hasattr(self, 'config_backup_tab') and self.config_backup_tab:
            # Adicionar botão EditorUiUX à interface do ConfigBackupTab
            editor_group = QGroupBox("🎨 Editor UI/UX")
            editor_layout = QVBoxLayout(editor_group)
            
            editor_info = QLabel("Interface para design e prototipagem de UI/UX")
            editor_info.setStyleSheet("color: #888; margin-bottom: 10px;")
            editor_layout.addWidget(editor_info)
            
            editor_btn = QPushButton("🎨 Abrir Editor UI/UX")
            editor_btn.clicked.connect(self.open_editor_uiux)
            editor_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #005a9e;
                }
            """)
            editor_layout.addWidget(editor_btn)
            
            # Adicionar ao layout principal do ConfigBackupTab
            if hasattr(self.config_backup_tab, 'layout'):
                self.config_backup_tab.layout().addWidget(editor_group)
    
    def on_agent_reload_needed(self):
        """Callback quando o agente precisa ser recarregado"""
        self.statusBar().showMessage("✅ Configuração salva - Recarregando agente...")
        self.load_agent()
    
    def on_backup_finished(self, result):
        """Callback quando backup é completado"""
        if result.get('status') == 'Success':
            password = result.get('password', 'N/A')
            self.statusBar().showMessage(f"✅ Backup concluído com sucesso")
        else:
            error_msg = result.get('error', 'Erro desconhecido')
            self.statusBar().showMessage(f"❌ Erro no backup: {error_msg}")
    
    def load_agent(self):
        """Carrega o agente"""
        try:
            if LANGCHAIN_AVAILABLE and AiAgenteMCP:
                self.agent = AiAgenteMCP()
                self.statusBar().showMessage("🤖 Agente carregado com sucesso")
            else:
                self.agent = None
                self.statusBar().showMessage("⚠️  Agente não disponível - modo limitado")
        except Exception as e:
            self.agent = None
            QMessageBox.warning(self, "Aviso", f"⚠️  Agente não disponível: {e}\nA interface funcionará em modo limitado")
    
    def load_rag_system(self):
        """Carrega o sistema RAG"""
        try:
            if LANGCHAIN_AVAILABLE and RAGSystem:
                self.rag_system = RAGSystem()
                self.refresh_documents_list()
                self.statusBar().showMessage("🧠 Sistema RAG carregado")
            else:
                self.rag_system = None
                self.statusBar().showMessage("⚠️  Sistema RAG não disponível - modo limitado")
        except Exception as e:
            self.rag_system = None
            QMessageBox.warning(self, "Aviso", f"⚠️  Sistema RAG não disponível: {e}\nA interface funcionará em modo limitado")
    
    def toggle_api_key_visibility(self):
        """Alterna visibilidade da API key"""
        if self.api_key_input.echoMode() == QLineEdit.Password:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.show_api_key_btn.setText("👁️ Mostrar")
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.show_api_key_btn.setText("👁️ Ocultar")
    
    def save_api_config(self):
        """
        Esta função é mantida para compatibilidade com a aba RAG (legado).
        A funcionalidade principal de salvar agora está em config_ui.py.
        """
        api_key = self.api_key_input.text()
        site_url = self.site_referrer_input.text()
        
        if not api_key:
            QMessageBox.warning(self, "Chave da API Faltando", "Por favor, insira sua chave da API OpenRouter.")
            return

        config_data = {
            "OPENROUTER_API_KEY": api_key,
            "YOUR_SITE_URL": site_url
        }
        
        config_path = Path("config/agent_config.json")
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
            
        QMessageBox.information(self, "Configuração Salva", f"Configuração da API salva em {config_path}")
        self.load_agent()
    
    def load_api_config(self):
        config_path = Path("config/agent_config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def test_api_connection(self):
        """Testa conexão com a API"""
        try:
            if not self.agent:
                QMessageBox.warning(self, "Erro", "Agente não carregado")
                return
            
            if not self.agent.openrouter_client:
                QMessageBox.warning(self, "Erro", "OpenRouter não configurado")
                return
            
            # Testar com uma mensagem simples
            response = self.agent.process_message("Teste de conexão")
            
            if response.success:
                QMessageBox.information(self, "Sucesso", 
                    f"Conexão testada com sucesso!\nModelo: {response.model_used}\n"
                    f"Tokens usados: {response.tokens_used}\n"
                    f"Tempo: {response.response_time:.2f}s")
            else:
                QMessageBox.warning(self, "Erro", f"Erro na conexão: {response.error_message}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao testar conexão: {e}")
    
    def select_pdf_file(self):
        """Seleciona arquivo PDF para upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar PDF", "", "PDF Files (*.pdf)")
        
        if file_path:
            self.upload_pdf_file(file_path)
    
    def upload_pdf_file(self, file_path):
        """Faz upload de um arquivo PDF"""
        try:
            if not self.rag_system:
                QMessageBox.warning(self, "Aviso", "⚠️  Sistema RAG não disponível")
                return
                
            self.upload_progress.setVisible(True)
            self.upload_progress.setValue(0)
            
            # Executar em thread separada para não travar a interface
            def upload_thread():
                try:
                    success = self.rag_system.add_document(file_path)
                    
                    # Atualizar interface na thread principal
                    self.upload_progress.setVisible(False)
                    
                    if success:
                        self.refresh_documents_list()
                        QMessageBox.information(self, "Sucesso", 
                            f"PDF processado com sucesso: {os.path.basename(file_path)}")
                    else:
                        QMessageBox.warning(self, "Erro", 
                            f"Erro ao processar PDF: {os.path.basename(file_path)}")
                        
                except Exception as e:
                    self.upload_progress.setVisible(False)
                    QMessageBox.critical(self, "Erro", f"Erro no upload: {e}")
            
            thread = threading.Thread(target=upload_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.upload_progress.setVisible(False)
            QMessageBox.critical(self, "Erro", f"Erro ao iniciar upload: {e}")
    
    def refresh_documents_list(self):
        """Atualiza lista de documentos"""
        try:
            if not self.rag_system:
                self.documents_list.clear()
                self.documents_list.addItem("⚠️  Sistema RAG não disponível")
                return
            
            self.documents_list.clear()
            documents = self.rag_system.get_document_list()
            
            for doc in documents:
                item_text = f"{doc['filename']} ({doc['chunks']} chunks, páginas {doc['pages']})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, doc)
                self.documents_list.addItem(item)
                
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao atualizar lista: {e}")
    
    def remove_selected_document(self):
        """Remove documento selecionado"""
        try:
            if not self.rag_system:
                QMessageBox.warning(self, "Aviso", "⚠️  Sistema RAG não disponível")
                return
                
            current_item = self.documents_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Erro", "Nenhum documento selecionado")
                return
            
            doc_data = current_item.data(Qt.UserRole)
            filename = doc_data['filename']
            
            # Confirmar remoção
            reply = QMessageBox.question(
                self, "Confirmar Remoção",
                f"Deseja remover o documento '{filename}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = self.rag_system.remove_document(filename)
                if success:
                    self.refresh_documents_list()
                    QMessageBox.information(self, "Sucesso", f"Documento removido: {filename}")
                else:
                    QMessageBox.warning(self, "Erro", f"Erro ao remover documento: {filename}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao remover documento: {e}")
    
    def clear_all_documents(self):
        """Limpa todos os documentos"""
        try:
            if not self.rag_system:
                QMessageBox.warning(self, "Aviso", "⚠️  Sistema RAG não disponível")
                return
                
            # Confirmar limpeza
            reply = QMessageBox.question(
                self, "Confirmar Limpeza",
                "Deseja remover TODOS os documentos? Esta ação não pode ser desfeita.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = self.rag_system.clear_all()
                if success:
                    self.refresh_documents_list()
                    QMessageBox.information(self, "Sucesso", "Todos os documentos foram removidos")
                else:
                    QMessageBox.warning(self, "Erro", "Erro ao limpar documentos")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao limpar documentos: {e}")
    
    def perform_search(self):
        """Executa busca semântica"""
        try:
            if not self.rag_system:
                QMessageBox.warning(self, "Aviso", "⚠️  Sistema RAG não disponível")
                return
                
            query = self.search_input.text().strip()
            if not query:
                QMessageBox.warning(self, "Erro", "Digite uma query para buscar")
                return
            
            top_k = self.top_k_spin.value()
            
            # Executar busca em thread separada
            def search_thread():
                try:
                    results = self.rag_system.search(query, top_k=top_k)
                    
                    # Atualizar interface na thread principal
                    if results:
                        result_text = f"Query: {query}\n\n"
                        for i, result in enumerate(results, 1):
                            result_text += f"Resultado {i}:\n"
                            result_text += f"Conteúdo: {result['content']}\n"
                            result_text += f"Score: {result['score']:.4f}\n"
                            result_text += f"Fonte: {result['source']}\n"
                            result_text += "-" * 50 + "\n"
                        
                        self.search_results.setText(result_text)
                    else:
                        self.search_results.setText("Nenhum resultado encontrado")
                        
                except Exception as e:
                    self.search_results.setText(f"Erro na busca: {e}")
            
            thread = threading.Thread(target=search_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao executar busca: {e}")
    
    def refresh_agent_status(self):
        """Atualiza status do agente"""
        try:
            if not self.agent:
                self.agent_status_text.setText("Agente não carregado")
                return
            
            status = self.agent.get_agent_status()
            status_text = json.dumps(status, indent=2, ensure_ascii=False)
            self.agent_status_text.setText(status_text)
            
        except Exception as e:
            self.agent_status_text.setText(f"Erro ao obter status: {e}")
    
    def send_message(self):
        """Envia mensagem para o agente"""
        try:
            if not self.agent:
                QMessageBox.warning(self, "Aviso", "⚠️  Agente não disponível")
                return
                
            message = self.message_input.text().strip()
            if not message:
                QMessageBox.warning(self, "Erro", "Digite uma mensagem")
                return
            
            # Adicionar mensagem do usuário ao chat
            self.chat_area.append(f"👤 Você: {message}")
            self.message_input.clear()
            
            # Processar mensagem em thread separada
            def process_message():
                try:
                    response = self.agent.process_message(message)
                    
                    # Atualizar interface na thread principal
                    if response.success:
                        self.chat_area.append(f"🤖 Agente: {response.message}")
                        self.chat_area.append(f"📊 Modelo: {response.model_used}, Tokens: {response.tokens_used}")
                    else:
                        self.chat_area.append(f"❌ Erro: {response.error_message}")
                        
                except Exception as e:
                    self.chat_area.append(f"❌ Erro: {e}")
            
            thread = threading.Thread(target=process_message)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao enviar mensagem: {e}")
    
    def load_mcp_manager(self):
        """Carrega o gerenciador de MCPs"""
        try:
            from mcp_manager import MCPManager
            self.mcp_manager = MCPManager()
            self.statusBar().showMessage("Gerenciador de MCPs carregado")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao carregar gerenciador de MCPs: {e}")
    
    def refresh_mcps_list(self):
        """Atualiza lista de MCPs"""
        try:
            if not hasattr(self, 'mcp_manager'):
                return
            
            status = self.mcp_manager.get_mcp_status()
            self.mcps_table.setRowCount(len(status))
            
            for row, (name, info) in enumerate(status.items()):
                self.mcps_table.setItem(row, 0, QTableWidgetItem(info['name']))
                self.mcps_table.setItem(row, 1, QTableWidgetItem(info['status']))
                self.mcps_table.setItem(row, 2, QTableWidgetItem(str(info['port'])))
                self.mcps_table.setItem(row, 3, QTableWidgetItem(info['category']))
                
                # Método de instalação
                method = info.get('installation_method', 'npm')
                self.mcps_table.setItem(row, 4, QTableWidgetItem(method))
                
                self.mcps_table.setItem(row, 5, QTableWidgetItem(info['description']))
                
                # Colorir status
                if info['status'] == 'running':
                    self.mcps_table.item(row, 1).setBackground(QColor(144, 238, 144))  # Verde
                elif info['status'] == 'stopped':
                    self.mcps_table.item(row, 1).setBackground(QColor(255, 182, 193))  # Vermelho claro
            
            self.mcps_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao atualizar lista de MCPs: {e}")
    
    def install_selected_mcp(self):
        """Instala MCP selecionado"""
        try:
            current_row = self.mcps_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Erro", "Selecione um MCP para instalar")
                return
            
            mcp_name = list(self.mcp_manager.mcps.keys())[current_row]
            
            reply = QMessageBox.question(self, "Confirmar", 
                f"Deseja instalar o MCP '{self.mcp_manager.mcps[mcp_name].name}'?",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                success = self.mcp_manager.install_mcp(mcp_name)
                if success:
                    QMessageBox.information(self, "Sucesso", "MCP instalado com sucesso")
                else:
                    QMessageBox.warning(self, "Erro", "Erro ao instalar MCP")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao instalar MCP: {e}")
    
    def start_selected_mcp(self):
        """Inicia MCP selecionado"""
        try:
            current_row = self.mcps_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Erro", "Selecione um MCP para iniciar")
                return
            
            mcp_name = list(self.mcp_manager.mcps.keys())[current_row]
            
            success = self.mcp_manager.start_mcp(mcp_name)
            if success:
                self.refresh_mcps_list()
                QMessageBox.information(self, "Sucesso", "MCP iniciado com sucesso")
            else:
                QMessageBox.warning(self, "Erro", "Erro ao iniciar MCP")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao iniciar MCP: {e}")
    
    def stop_selected_mcp(self):
        """Para MCP selecionado"""
        try:
            current_row = self.mcps_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Erro", "Selecione um MCP para parar")
                return
            
            mcp_name = list(self.mcp_manager.mcps.keys())[current_row]
            
            success = self.mcp_manager.stop_mcp(mcp_name)
            if success:
                self.refresh_mcps_list()
                QMessageBox.information(self, "Sucesso", "MCP parado com sucesso")
            else:
                QMessageBox.warning(self, "Erro", "Erro ao parar MCP")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao parar MCP: {e}")
    
    def load_ollama_models(self):
        """Carrega modelos Ollama recomendados"""
        try:
            if not hasattr(self, 'mcp_manager'):
                return
            
            # Verificar status do Ollama
            ollama_status = self.mcp_manager.ollama_manager.check_ollama_status()
            if ollama_status:
                self.ollama_list.clear()
                for name, info in self.mcp_manager.ollama_manager.recommended_models.items():
                    item_text = f"{name}: {info['description']} ({info['size']})"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, name)
                    self.ollama_list.addItem(item)
            else:
                self.ollama_list.clear()
                QMessageBox.warning(self, "Erro", "Modelos Ollama não encontrados")
                
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao carregar modelos Ollama: {e}")
    
    def install_ollama_model(self):
        """Instala modelo Ollama selecionado"""
        try:
            current_item = self.ollama_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Erro", "Selecione um modelo para instalar")
                return
            
            model_name = current_item.data(Qt.UserRole)
            model_info = self.mcp_manager.ollama_manager.recommended_models[model_name]
            
            reply = QMessageBox.question(self, "Confirmar", 
                f"Deseja instalar o modelo '{model_name}'?\n\n"
                f"Descrição: {model_info['description']}\n"
                f"Tamanho: {model_info['size']}\n"
                f"Performance: {model_info['performance']}",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Executar em thread separada
                def install_thread():
                    try:
                        success = self.mcp_manager.ollama_manager.install_model(model_info['name'])
                        if success:
                            QMessageBox.information(self, "Sucesso", f"Modelo {model_name} instalado com sucesso")
                        else:
                            QMessageBox.warning(self, "Erro", f"Erro ao instalar modelo {model_name}")
                    except Exception as e:
                        QMessageBox.critical(self, "Erro", f"Erro na instalação: {e}")
                
                thread = threading.Thread(target=install_thread)
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao instalar modelo: {e}")
    
    def remove_ollama_model(self):
        """Remove modelo Ollama selecionado"""
        try:
            current_item = self.ollama_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Erro", "Selecione um modelo para remover")
                return
            
            model_name = current_item.data(Qt.UserRole)
            model_info = self.mcp_manager.ollama_manager.recommended_models[model_name]
            
            reply = QMessageBox.question(self, "Confirmar", 
                f"Deseja remover o modelo '{model_name}'?\n\n"
                f"Esta ação não pode ser desfeita.",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                success = self.mcp_manager.ollama_manager.remove_model(model_info['name'])
                if success:
                    QMessageBox.information(self, "Sucesso", f"Modelo {model_name} removido com sucesso")
                else:
                    QMessageBox.warning(self, "Erro", f"Erro ao remover modelo {model_name}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao remover modelo: {e}")
    
    def analyze_and_manage_mcps(self):
        """Analisa prompt e gerencia MCPs automaticamente"""
        try:
            if not hasattr(self, 'mcp_manager'):
                QMessageBox.warning(self, "Erro", "Gerenciador de MCPs não carregado")
                return
            
            prompt = self.prompt_content.toPlainText().strip()
            if not prompt:
                QMessageBox.warning(self, "Erro", "Digite um prompt para análise")
                return
            
            # Analisar prompt
            suggested_mcps = self.mcp_manager.analyze_prompt_for_mcps(prompt)
            
            # Mostrar MCPs sugeridos
            self.suggested_mcps_list.clear()
            for mcp_name in suggested_mcps:
                mcp = self.mcp_manager.mcps[mcp_name]
                item_text = f"{mcp.name} ({mcp.category}) - {mcp.description}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, mcp_name)
                self.suggested_mcps_list.addItem(item)
            
            # Gerenciar MCPs automaticamente
            results = self.mcp_manager.auto_manage_mcps(prompt)
            
            # Mostrar resultados
            result_text = f"Análise do prompt: '{prompt}'\n\n"
            result_text += f"MCPs sugeridos: {', '.join(results['suggested_mcps'])}\n"
            result_text += f"MCPs iniciados: {', '.join(results['started'])}\n"
            result_text += f"MCPs parados: {', '.join(results['stopped'])}\n"
            
            if results['errors']:
                result_text += f"Erros: {', '.join(results['errors'])}\n"
            
            QMessageBox.information(self, "Análise Concluída", result_text)
            
            # Atualizar lista de MCPs
            self.refresh_mcps_list()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na análise: {e}")
    
    def install_from_github(self):
        """Instala MCP diretamente do GitHub"""
        try:
            from PyQt5.QtWidgets import QInputDialog, QMessageBox
            
            # Solicitar URL do GitHub
            github_url, ok = QInputDialog.getText(
                self, 
                "Instalar do GitHub", 
                "Digite a URL do repositório GitHub:"
            )
            
            if not ok or not github_url.strip():
                return
            
            # Solicitar nome do MCP
            mcp_name, ok = QInputDialog.getText(
                self, 
                "Nome do MCP", 
                "Digite o nome para o MCP:"
            )
            
            if not ok or not mcp_name.strip():
                return
            
            # Instalar
            success = self.mcp_manager.install_custom_mcp(
                mcp_name=mcp_name,
                github_url=github_url
            )
            
            if success:
                QMessageBox.information(self, "Sucesso", f"MCP {mcp_name} instalado com sucesso do GitHub")
                self.refresh_mcps_list()
            else:
                QMessageBox.warning(self, "Erro", f"Erro ao instalar MCP {mcp_name} do GitHub")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na instalação: {e}")
    
    def search_mcp_alternatives(self):
        """Busca alternativas para um MCP no GitHub"""
        try:
            from PyQt5.QtWidgets import QInputDialog, QMessageBox, QDialog, QVBoxLayout, QListWidget, QPushButton
            
            # Solicitar nome do MCP
            mcp_name, ok = QInputDialog.getText(
                self, 
                "Buscar Alternativas", 
                "Digite o nome do MCP para buscar alternativas:"
            )
            
            if not ok or not mcp_name.strip():
                return
            
            # Buscar alternativas
            alternatives = self.mcp_manager.search_mcp_alternatives(mcp_name)
            
            if not alternatives:
                QMessageBox.information(self, "Resultado", "Nenhuma alternativa encontrada")
                return
            
            # Mostrar resultados em uma janela
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Alternativas para {mcp_name}")
            dialog.setGeometry(400, 300, 600, 400)
            
            layout = QVBoxLayout(dialog)
            
            # Lista de alternativas
            alternatives_list = QListWidget()
            for alt in alternatives:
                item_text = f"{alt['full_name']} - {alt['description']} (⭐{alt['stars']})"
                alternatives_list.addItem(item_text)
            
            layout.addWidget(alternatives_list)
            
            # Botão para instalar selecionado
            install_btn = QPushButton("Instalar Selecionado")
            install_btn.clicked.connect(lambda: self._install_selected_alternative(
                alternatives, alternatives_list.currentRow(), dialog
            ))
            layout.addWidget(install_btn)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na busca: {e}")
    
    def _install_selected_alternative(self, alternatives, selected_index, dialog):
        """Instala alternativa selecionada"""
        try:
            if selected_index < 0 or selected_index >= len(alternatives):
                QMessageBox.warning(self, "Erro", "Selecione uma alternativa")
                return
            
            selected = alternatives[selected_index]
            
            # Solicitar nome do MCP
            from PyQt5.QtWidgets import QInputDialog
            mcp_name, ok = QInputDialog.getText(
                self, 
                "Nome do MCP", 
                f"Digite o nome para instalar {selected['name']}:"
            )
            
            if not ok or not mcp_name.strip():
                return
            
            # Instalar
            success = self.mcp_manager.install_custom_mcp(
                mcp_name=mcp_name,
                github_url=selected['clone_url']
            )
            
            if success:
                QMessageBox.information(self, "Sucesso", f"MCP {mcp_name} instalado com sucesso")
                self.refresh_mcps_list()
                dialog.accept()
            else:
                QMessageBox.warning(self, "Erro", f"Erro ao instalar MCP {mcp_name}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na instalação: {e}")
    
    def install_custom_mcp(self):
        """Instala MCP customizado"""
        try:
            from PyQt5.QtWidgets import QInputDialog, QMessageBox
            
            # Solicitar nome do MCP
            mcp_name, ok = QInputDialog.getText(
                self, 
                "Instalar MCP Customizado", 
                "Digite o nome do MCP:"
            )
            
            if not ok or not mcp_name.strip():
                return
            
            # Escolher método de instalação
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, 
                "Método de Instalação",
                "Escolha o método de instalação:",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # GitHub
                github_url, ok = QInputDialog.getText(
                    self, 
                    "URL do GitHub", 
                    "Digite a URL do repositório GitHub:"
                )
                
                if ok and github_url.strip():
                    success = self.mcp_manager.install_custom_mcp(
                        mcp_name=mcp_name,
                        github_url=github_url
                    )
                else:
                    return
            else:
                # npm
                npm_package, ok = QInputDialog.getText(
                    self, 
                    "Pacote npm", 
                    "Digite o nome do pacote npm:"
                )
                
                if ok and npm_package.strip():
                    success = self.mcp_manager.install_custom_mcp(
                        mcp_name=mcp_name,
                        npm_package=npm_package
                    )
                else:
                    return
            
            if success:
                QMessageBox.information(self, "Sucesso", f"MCP {mcp_name} instalado com sucesso")
                self.refresh_mcps_list()
            else:
                QMessageBox.warning(self, "Erro", f"Erro ao instalar MCP {mcp_name}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na instalação: {e}")
    
    def open_editor_uiux(self):
        """Abre o Editor UI/UX"""
        try:
            import subprocess
            import os
            from PyQt5.QtWidgets import QMessageBox
            
            # Caminho para o Editor UI/UX
            editor_path = os.path.join(os.path.dirname(__file__), "EditorUiUX", "run_editor.py")
            
            if not os.path.exists(editor_path):
                QMessageBox.warning(
                    self, 
                    "Editor não encontrado", 
                    f"O Editor UI/UX não foi encontrado em:\n{editor_path}\n\nVerifique se o diretório EditorUiUX existe."
                )
                return
            
            # Executar o editor
            try:
                subprocess.Popen([sys.executable, editor_path], 
                               cwd=os.path.dirname(editor_path))
                
                QMessageBox.information(
                    self, 
                    "Editor UI/UX", 
                    "🎨 Editor UI/UX iniciado!\n\nO editor será aberto em uma nova janela com tema escuro."
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Erro ao abrir Editor", 
                    f"Erro ao executar o Editor UI/UX:\n{str(e)}\n\nTente instalar as dependências primeiro."
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir Editor UI/UX: {e}")

    def install_editor_dependencies(self):
        """Instala as dependências do Editor UI/UX"""
        try:
            import subprocess
            import os
            from PyQt5.QtWidgets import QMessageBox, QProgressDialog
            
            # Caminho para o requirements do Editor UI/UX
            requirements_path = os.path.join(os.path.dirname(__file__), "EditorUiUX", "requirements.txt")
            
            if not os.path.exists(requirements_path):
                QMessageBox.warning(
                    self, 
                    "Requirements não encontrado", 
                    f"Arquivo requirements.txt não encontrado em:\n{requirements_path}"
                )
                return
            
            # Mostrar progresso
            progress = QProgressDialog("Instalando dependências do Editor UI/UX...", "Cancelar", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            try:
                # Instalar dependências
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", requirements_path],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(requirements_path)
                )
                
                progress.close()
                
                if result.returncode == 0:
                    QMessageBox.information(
                        self, 
                        "Instalação Concluída", 
                        "✅ Dependências do Editor UI/UX instaladas com sucesso!\n\nAgora você pode abrir o editor."
                    )
                else:
                    QMessageBox.warning(
                        self, 
                        "Erro na Instalação", 
                        f"❌ Erro ao instalar dependências:\n\n{result.stderr}\n\nTente instalar manualmente:\npip install -r {requirements_path}"
                    )
                    
            except Exception as e:
                progress.close()
                QMessageBox.critical(
                    self, 
                    "Erro", 
                    f"Erro durante a instalação:\n{str(e)}"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao instalar dependências: {e}")

    def save_cursor_configuration(self):
        """Salva configuração do Cursor"""
        try:
            config_text = self.cursor_config_input.toPlainText().strip()
            if not config_text:
                QMessageBox.warning(self, "Erro", "Digite uma configuração para salvar")
                return
            
            # Salvar em arquivo
            config_file = "cursor_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_text)
            
            QMessageBox.information(self, "Sucesso", f"Configuração salva em {config_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar configuração: {e}")
    
    def load_cursor_config(self):
        """Carrega configuração do Cursor"""
        try:
            config_file = "cursor_config.json"
            if not os.path.exists(config_file):
                QMessageBox.warning(self, "Erro", f"Arquivo {config_file} não encontrado")
                return
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_text = f.read()
            
            self.cursor_config_input.setPlainText(config_text)
            QMessageBox.information(self, "Sucesso", f"Configuração carregada de {config_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar configuração: {e}")

    def load_prompt_categories(self):
        """Carrega categorias de prompts"""
        try:
            # Aqui você carregaria as categorias do prompt_manager.py
            # Por enquanto, vamos usar as categorias padrão
            self.prompt_categories = {
                "Lovable": {
                    "description": "Prompts para desenvolvimento com Lovable",
                    "icon": "❤️",
                    "docs_url": "https://docs.lovable.dev/introduction"
                },
                "Leonardo AI": {
                    "description": "Prompts para geração de imagens com Leonardo AI",
                    "icon": "🎨",
                    "docs_url": "https://docs.leonardo.ai/"
                },
                "V03 Google": {
                    "description": "Prompts para geração de vídeo com V03 da Google",
                    "icon": "🎬",
                    "docs_url": "https://ai.google.dev/gemini-api/docs/models/gemini"
                },
                "Cursor": {
                    "description": "Prompts para desenvolvimento com Cursor",
                    "icon": "⚡",
                    "docs_url": "https://cursor.sh/docs"
                },
                "VS Code": {
                    "description": "Prompts para VS Code e extensões",
                    "icon": "💻",
                    "docs_url": "https://code.visualstudio.com/docs"
                },
                "Wandsurf": {
                    "description": "Prompts para Wandsurf",
                    "icon": "🌊",
                    "docs_url": ""
                },
                "Trae": {
                    "description": "Prompts para Trae",
                    "icon": "🌿",
                    "docs_url": ""
                },
                "GitHub Copilot Pro": {
                    "description": "Prompts para GitHub Copilot Pro",
                    "icon": "🤖",
                    "docs_url": "https://docs.github.com/en/copilot"
                }
            }
            
            # Carregar prompts de exemplo
            self.load_sample_prompts()
            
        except Exception as e:
            QMessageBox.warning(self, "Aviso", f"Erro ao carregar categorias: {e}")
    
    def load_sample_prompts(self):
        """Carrega prompts de exemplo"""
        self.prompts_data = {
            "Lovable": [
                {
                    "title": "Lovable Dev",
                    "content": "You are an expert in Lovable development. Help me create a modern web application with best practices.",
                    "rating": 4.5,
                    "usage_count": 45
                },
                {
                    "title": "UI Design",
                    "content": "Create a beautiful and responsive UI design following modern design principles.",
                    "rating": 4.8,
                    "usage_count": 32
                }
            ],
            "Cursor": [
                {
                    "title": "Code Review",
                    "content": "Review this code and suggest improvements for better performance and maintainability.",
                    "rating": 4.2,
                    "usage_count": 28
                }
            ],
            "Leonardo AI": [
                {
                    "title": "Image Generation",
                    "content": "Generate a high-quality image with detailed specifications and artistic style.",
                    "rating": 4.6,
                    "usage_count": 15
                }
            ]
        }
    
    def on_category_changed(self, category_name):
        """Chamado quando a categoria é alterada"""
        try:
            self.current_category = category_name
            self.load_prompts_for_category(category_name)
            self.update_stats()
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao carregar categoria: {e}")
    
    def load_prompts_for_category(self, category_name):
        """Carrega prompts para a categoria selecionada"""
        try:
            self.prompts_list.clear()
            
            if category_name in self.prompts_data:
                for prompt in self.prompts_data[category_name]:
                    item_text = f"{prompt['title']} ⭐{prompt['rating']} ({prompt['usage_count']} usos)"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, prompt)
                    self.prompts_list.addItem(item)
            else:
                # Adicionar prompt de exemplo para categorias vazias
                sample_prompt = {
                    "title": "Novo Prompt",
                    "content": f"Digite aqui seu prompt para {category_name}...",
                    "rating": 0.0,
                    "usage_count": 0
                }
                item_text = f"{sample_prompt['title']} ⭐{sample_prompt['rating']} ({sample_prompt['usage_count']} usos)"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, sample_prompt)
                self.prompts_list.addItem(item)
                
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao carregar prompts: {e}")
    
    def on_prompt_selected(self, item):
        """Chamado quando um prompt é selecionado"""
        try:
            prompt_data = item.data(Qt.UserRole)
            self.current_prompt = prompt_data
            self.prompt_content.setPlainText(prompt_data['content'])
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao selecionar prompt: {e}")
    
    def add_new_category(self):
        """Adiciona nova categoria"""
        try:
            from PyQt5.QtWidgets import QInputDialog
            
            name, ok = QInputDialog.getText(self, "Nova Categoria", "Nome da categoria:")
            if ok and name.strip():
                # Adicionar à lista de categorias
                self.category_combo.addItem(name)
                self.prompt_categories[name] = {
                    "description": f"Prompts para {name}",
                    "icon": "📁",
                    "docs_url": ""
                }
                self.prompts_data[name] = []
                QMessageBox.information(self, "Sucesso", f"Categoria '{name}' adicionada!")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar categoria: {e}")
    
    def add_new_prompt(self):
        """Adiciona novo prompt"""
        try:
            from PyQt5.QtWidgets import QInputDialog
            
            title, ok = QInputDialog.getText(self, "Novo Prompt", "Título do prompt:")
            if ok and title.strip():
                content, ok = QInputDialog.getMultiLineText(self, "Novo Prompt", "Conteúdo do prompt:")
                if ok and content.strip():
                    # Adicionar prompt
                    new_prompt = {
                        "title": title,
                        "content": content,
                        "rating": 0.0,
                        "usage_count": 0
                    }
                    
                    category = self.category_combo.currentText()
                    if category not in self.prompts_data:
                        self.prompts_data[category] = []
                    
                    self.prompts_data[category].append(new_prompt)
                    self.load_prompts_for_category(category)
                    QMessageBox.information(self, "Sucesso", f"Prompt '{title}' adicionado!")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar prompt: {e}")
    
    def edit_selected_prompt(self):
        """Edita prompt selecionado"""
        try:
            current_item = self.prompts_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Erro", "Selecione um prompt para editar")
                return
            
            prompt_data = current_item.data(Qt.UserRole)
            
            from PyQt5.QtWidgets import QInputDialog
            
            title, ok = QInputDialog.getText(self, "Editar Prompt", "Título:", text=prompt_data['title'])
            if ok and title.strip():
                content, ok = QInputDialog.getMultiLineText(self, "Editar Prompt", "Conteúdo:", text=prompt_data['content'])
                if ok and content.strip():
                    # Atualizar prompt
                    prompt_data['title'] = title
                    prompt_data['content'] = content
                    
                    category = self.category_combo.currentText()
                    self.load_prompts_for_category(category)
                    self.prompt_content.setPlainText(content)
                    QMessageBox.information(self, "Sucesso", "Prompt atualizado!")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao editar prompt: {e}")
    
    def delete_selected_prompt(self):
        """Exclui prompt selecionado"""
        try:
            current_item = self.prompts_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Erro", "Selecione um prompt para excluir")
                return
            
            prompt_data = current_item.data(Qt.UserRole)
            
            reply = QMessageBox.question(
                self, "Confirmar Exclusão",
                f"Deseja excluir o prompt '{prompt_data['title']}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                category = self.category_combo.currentText()
                self.prompts_data[category] = [p for p in self.prompts_data[category] if p['title'] != prompt_data['title']]
                self.load_prompts_for_category(category)
                self.prompt_content.clear()
                QMessageBox.information(self, "Sucesso", "Prompt excluído!")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao excluir prompt: {e}")
    
    def copy_prompt_content(self):
        """Copia conteúdo do prompt para área de transferência"""
        try:
            content = self.prompt_content.toPlainText()
            if content.strip():
                clipboard = QApplication.clipboard()
                clipboard.setText(content)
                QMessageBox.information(self, "Sucesso", "Prompt copiado para área de transferência!")
            else:
                QMessageBox.warning(self, "Erro", "Nenhum prompt selecionado")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao copiar prompt: {e}")
    
    def export_prompt(self):
        """Exporta prompt para arquivo"""
        try:
            content = self.prompt_content.toPlainText()
            if not content.strip():
                QMessageBox.warning(self, "Erro", "Nenhum prompt selecionado")
                return
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Exportar Prompt", "", "Text Files (*.txt);;JSON Files (*.json)"
            )
            
            if file_path:
                if file_path.endswith('.json'):
                    # Exportar como JSON
                    data = {
                        "title": self.current_prompt['title'] if self.current_prompt else "Prompt",
                        "content": content,
                        "category": self.category_combo.currentText(),
                        "exported_at": datetime.now().isoformat()
                    }
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    # Exportar como texto
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                QMessageBox.information(self, "Sucesso", f"Prompt exportado para {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar prompt: {e}")
    
    def rate_selected_prompt(self):
        """Avalia prompt selecionado"""
        try:
            if not self.current_prompt:
                QMessageBox.warning(self, "Erro", "Selecione um prompt para avaliar")
                return
            
            from PyQt5.QtWidgets import QInputDialog
            
            rating, ok = QInputDialog.getDouble(
                self, "Avaliar Prompt", 
                f"Avalie o prompt '{self.current_prompt['title']}' (0.0 - 5.0):",
                value=self.current_prompt['rating'],
                min=0.0, max=5.0, decimals=1
            )
            
            if ok:
                self.current_prompt['rating'] = rating
                category = self.category_combo.currentText()
                self.load_prompts_for_category(category)
                self.update_stats()
                QMessageBox.information(self, "Sucesso", f"Prompt avaliado com {rating} estrelas!")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao avaliar prompt: {e}")
    
    def search_documentation(self):
        """Busca documentação relacionada"""
        try:
            query = self.docs_search_input.text().strip()
            if not query:
                QMessageBox.warning(self, "Erro", "Digite algo para buscar")
                return
            
            category = self.category_combo.currentText()
            
            # Simular busca de documentação
            self.docs_results.setText(f"🔍 Buscando documentação para '{query}' na categoria '{category}'...\n\n")
            
            # Simular resultados
            results = f"""
📚 Resultados da busca para "{query}":

1. **Documentação Oficial {category}**
   - URL: {self.prompt_categories.get(category, {}).get('docs_url', 'N/A')}
   - Relevância: Alta
   - Conteúdo: Documentação oficial com exemplos e melhores práticas

2. **Tutoriais e Guias**
   - URL: https://example.com/tutorials/{category.lower()}
   - Relevância: Média
   - Conteúdo: Tutoriais passo a passo e casos de uso

3. **Comunidade e Fóruns**
   - URL: https://community.example.com/{category.lower()}
   - Relevância: Média
   - Conteúdo: Discussões da comunidade e soluções para problemas comuns

💡 Dica: Use o botão "✨ Melhorar Prompt com Docs" para aplicar essas informações ao seu prompt.
"""
            
            self.docs_results.setText(results)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na busca: {e}")
    
    def improve_prompt_with_docs(self):
        """Melhora prompt usando documentação encontrada"""
        try:
            if not self.current_prompt:
                QMessageBox.warning(self, "Erro", "Selecione um prompt para melhorar")
                return
            
            docs_content = self.docs_results.toPlainText()
            if not docs_content.strip() or "Buscando documentação" in docs_content:
                QMessageBox.warning(self, "Erro", "Execute uma busca de documentação primeiro")
                return
            
            # Simular melhoria do prompt
            original_content = self.current_prompt['content']
            improved_content = f"""
{original_content}

📚 Melhorado com base na documentação:

{original_content}

💡 Dicas da documentação:
- Use exemplos específicos
- Inclua contexto relevante
- Especifique o formato de saída desejado
- Adicione restrições ou requisitos específicos

🎯 Resultado esperado: Prompt mais eficaz e preciso
"""
            
            # Mostrar diálogo de comparação
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Melhorias de Prompt")
            dialog.setModal(True)
            dialog.setFixedSize(800, 600)
            
            layout = QVBoxLayout()
            
            # Splitter para comparar
            splitter = QSplitter(Qt.Horizontal)
            
            # Prompt original
            original_group = QGroupBox("Prompt Original")
            original_layout = QVBoxLayout()
            original_text = QTextEdit()
            original_text.setPlainText(original_content)
            original_text.setReadOnly(True)
            original_layout.addWidget(original_text)
            original_group.setLayout(original_layout)
            
            # Prompt melhorado
            improved_group = QGroupBox("Prompt Melhorado")
            improved_layout = QVBoxLayout()
            improved_text = QTextEdit()
            improved_text.setPlainText(improved_content)
            improved_layout.addWidget(improved_text)
            improved_group.setLayout(improved_layout)
            
            splitter.addWidget(original_group)
            splitter.addWidget(improved_group)
            
            layout.addWidget(splitter)
            
            # Botões
            button_layout = QHBoxLayout()
            apply_button = QPushButton("Aplicar Melhorias")
            cancel_button = QPushButton("Cancelar")
            
            apply_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)
            
            button_layout.addWidget(apply_button)
            button_layout.addWidget(cancel_button)
            
            layout.addLayout(button_layout)
            dialog.setLayout(layout)
            
            if dialog.exec_() == QDialog.Accepted:
                # Aplicar melhorias
                self.current_prompt['content'] = improved_text.toPlainText()
                self.prompt_content.setPlainText(improved_text.toPlainText())
                
                # Atualizar na lista
                category = self.category_combo.currentText()
                self.load_prompts_for_category(category)
                
                QMessageBox.information(self, "Sucesso", "Prompt melhorado com sucesso!")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao melhorar prompt: {e}")
    
    def update_stats(self):
        """Atualiza estatísticas"""
        try:
            total_prompts = sum(len(prompts) for prompts in self.prompts_data.values())
            total_categories = len(self.prompt_categories)
            
            # Encontrar prompt mais usado
            most_used = None
            max_usage = 0
            for category_prompts in self.prompts_data.values():
                for prompt in category_prompts:
                    if prompt['usage_count'] > max_usage:
                        max_usage = prompt['usage_count']
                        most_used = prompt['title']
            
            # Encontrar melhor avaliado
            best_rated = None
            max_rating = 0
            for category_prompts in self.prompts_data.values():
                for prompt in category_prompts:
                    if prompt['rating'] > max_rating:
                        max_rating = prompt['rating']
                        best_rated = prompt['title']
            
            stats_text = f"""• Total de prompts: {total_prompts}
• Categorias: {total_categories}
• Prompt mais usado: {most_used or 'N/A'} ({max_usage} usos)
• Melhor avaliado: {best_rated or 'N/A'} ({max_rating:.1f}/5.0)"""
            
            self.stats_label.setText(stats_text)
            
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao atualizar estatísticas: {e}")

def main():
    """Função principal"""
    app = QApplication(sys.argv)
    
    # Aplicar tema escuro
    DarkTheme.apply_theme(app)
    
    # Configurar fonte
    font = QFont("Consolas", 9)
    app.setFont(font)
    
    # Criar e mostrar janela principal
    window = AiAgentGUI()
    window.show()
    
    # Executar aplicação
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 