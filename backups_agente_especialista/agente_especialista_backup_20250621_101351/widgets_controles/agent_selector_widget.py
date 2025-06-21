#!/usr/bin/env python3
"""
Widget de Seleção de Agentes OpenRouter
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QDialog, QTextEdit,
                             QCheckBox, QGroupBox, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QFont
import json
import os
import requests
from datetime import datetime

class AgentSelectorDialog(QDialog):
    """Dialog para seleção de agente OpenRouter"""
    
    agent_selected = pyqtSignal(dict)  # Emite dados do agente selecionado
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🤖 Seletor de Agentes OpenRouter")
        self.setFixedSize(600, 500)
        self.setModal(True)
        
        # Dados dos agentes
        self.agents_data = []
        self.filtered_agents = []
        self.selected_agent = None
        
        self.init_ui()
        self.load_agents()
        
    def init_ui(self):
        """Inicializa interface"""
        layout = QVBoxLayout(self)
        
        # Cabeçalho com ícone
        header_layout = QHBoxLayout()
        
        # Ícone do robô
        robot_label = QLabel()
        if os.path.exists('static/icons/robot_smiling.png'):
            pixmap = QPixmap('static/icons/robot_smiling.png')
            robot_label.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            robot_label.setText("🤖")
            robot_label.setStyleSheet("font-size: 32px;")
        
        # Título
        title_label = QLabel("Selecione seu Agente de IA")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        header_layout.addWidget(robot_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Filtros
        filters_group = QGroupBox("Filtros")
        filters_layout = QVBoxLayout(filters_group)
        
        # Checkbox para modelos gratuitos
        self.free_only_checkbox = QCheckBox("Apenas modelos gratuitos")
        self.free_only_checkbox.stateChanged.connect(self.filter_agents)
        filters_layout.addWidget(self.free_only_checkbox)
        
        # Filtro por provedor
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("Provedor:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItem("Todos")
        self.provider_combo.currentTextChanged.connect(self.filter_agents)
        provider_layout.addWidget(self.provider_combo)
        provider_layout.addStretch()
        
        filters_layout.addLayout(provider_layout)
        layout.addWidget(filters_group)
        
        # Lista de agentes
        agents_group = QGroupBox("Agentes Disponíveis")
        agents_layout = QVBoxLayout(agents_group)
        
        # Área de scroll para agentes
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.agents_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(250)
        
        agents_layout.addWidget(scroll_area)
        layout.addWidget(agents_group)
        
        # Informações do agente selecionado
        info_group = QGroupBox("Informações do Agente")
        info_layout = QVBoxLayout(info_group)
        
        self.agent_info_text = QTextEdit()
        self.agent_info_text.setMaximumHeight(80)
        self.agent_info_text.setReadOnly(True)
        info_layout.addWidget(self.agent_info_text)
        
        layout.addWidget(info_group)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("🔄 Atualizar Lista")
        self.refresh_button.clicked.connect(self.load_agents)
        
        self.select_button = QPushButton("✅ Selecionar Agente")
        self.select_button.clicked.connect(self.select_agent)
        self.select_button.setEnabled(False)
        
        cancel_button = QPushButton("❌ Cancelar")
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(self.select_button)
        
        layout.addLayout(buttons_layout)
        
    def load_agents(self):
        """Carrega lista de agentes do OpenRouter"""
        try:
            # Dados simulados dos principais agentes OpenRouter
            self.agents_data = [
                {
                    "id": "openai/gpt-4-turbo",
                    "name": "GPT-4 Turbo",
                    "provider": "OpenAI",
                    "description": "Modelo mais avançado da OpenAI com 128k tokens de contexto",
                    "pricing": {"prompt": "0.01", "completion": "0.03"},
                    "context_length": 128000,
                    "free": False
                },
                {
                    "id": "openai/gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "provider": "OpenAI", 
                    "description": "Modelo rápido e eficiente da OpenAI",
                    "pricing": {"prompt": "0.0015", "completion": "0.002"},
                    "context_length": 16385,
                    "free": False
                },
                {
                    "id": "anthropic/claude-3-sonnet",
                    "name": "Claude 3 Sonnet",
                    "provider": "Anthropic",
                    "description": "Modelo equilibrado da Anthropic com excelente raciocínio",
                    "pricing": {"prompt": "0.003", "completion": "0.015"},
                    "context_length": 200000,
                    "free": False
                },
                {
                    "id": "google/gemini-pro",
                    "name": "Gemini Pro",
                    "provider": "Google",
                    "description": "Modelo multimodal avançado do Google",
                    "pricing": {"prompt": "0.00025", "completion": "0.0005"},
                    "context_length": 32768,
                    "free": True
                },
                {
                    "id": "meta-llama/llama-3-70b-instruct",
                    "name": "Llama 3 70B Instruct",
                    "provider": "Meta",
                    "description": "Modelo open source da Meta com 70 bilhões de parâmetros",
                    "pricing": {"prompt": "0.0009", "completion": "0.0009"},
                    "context_length": 8192,
                    "free": True
                },
                {
                    "id": "mistralai/mixtral-8x7b-instruct",
                    "name": "Mixtral 8x7B Instruct",
                    "provider": "Mistral AI",
                    "description": "Modelo mixture-of-experts eficiente",
                    "pricing": {"prompt": "0.0007", "completion": "0.0007"},
                    "context_length": 32768,
                    "free": True
                }
            ]
            
            # Atualizar lista de provedores
            providers = set(agent["provider"] for agent in self.agents_data)
            self.provider_combo.clear()
            self.provider_combo.addItem("Todos")
            for provider in sorted(providers):
                self.provider_combo.addItem(provider)
            
            self.filter_agents()
            
        except Exception as e:
            self.agent_info_text.setText(f"❌ Erro ao carregar agentes: {str(e)}")
    
    def filter_agents(self):
        """Filtra agentes baseado nos critérios selecionados"""
        self.filtered_agents = self.agents_data.copy()
        
        # Filtrar por gratuitos
        if self.free_only_checkbox.isChecked():
            self.filtered_agents = [a for a in self.filtered_agents if a.get("free", False)]
        
        # Filtrar por provedor
        provider = self.provider_combo.currentText()
        if provider != "Todos":
            self.filtered_agents = [a for a in self.filtered_agents if a["provider"] == provider]
        
        self.update_agents_list()
    
    def update_agents_list(self):
        """Atualiza a lista visual de agentes"""
        # Limpar layout atual
        for i in reversed(range(self.agents_layout.count())):
            child = self.agents_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Adicionar agentes filtrados
        for agent in self.filtered_agents:
            agent_widget = self.create_agent_widget(agent)
            self.agents_layout.addWidget(agent_widget)
        
        # Adicionar espaçador
        self.agents_layout.addStretch()
    
    def create_agent_widget(self, agent):
        """Cria widget para um agente"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
            QFrame:hover {
                background-color: #f0f0f0;
                border-color: #0078d4;
            }
        """)
        frame.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(frame)
        
        # Informações do agente
        info_layout = QVBoxLayout()
        
        # Nome e provedor
        name_label = QLabel(f"{agent['name']} ({agent['provider']})")
        name_font = QFont()
        name_font.setBold(True)
        name_label.setFont(name_font)
        
        # Descrição
        desc_label = QLabel(agent['description'])
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666666; font-size: 11px;")
        
        # Preço e contexto
        price_text = "GRATUITO" if agent.get("free") else f"${agent['pricing']['prompt']}/1K tokens"
        context_text = f"{agent['context_length']:,} tokens"
        details_label = QLabel(f"💰 {price_text} | 📄 {context_text}")
        details_label.setStyleSheet("color: #888888; font-size: 10px;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(desc_label)
        info_layout.addWidget(details_label)
        
        layout.addLayout(info_layout)
        
        # Badge gratuito
        if agent.get("free"):
            free_label = QLabel("FREE")
            free_label.setStyleSheet("""
                background-color: #28a745;
                color: white;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            """)
            free_label.setFixedSize(40, 20)
            layout.addWidget(free_label)
        
        # Conectar clique
        frame.mousePressEvent = lambda event, a=agent: self.on_agent_clicked(a)
        
        return frame
    
    def on_agent_clicked(self, agent):
        """Manipula clique em um agente"""
        self.selected_agent = agent
        self.select_button.setEnabled(True)
        
        # Atualizar informações
        info_text = f"""
🤖 {agent['name']} ({agent['provider']})

📝 {agent['description']}

💰 Preço: {"GRATUITO" if agent.get('free') else f"${agent['pricing']['prompt']}/1K prompt + ${agent['pricing']['completion']}/1K completion"}
📄 Contexto: {agent['context_length']:,} tokens
🆔 ID: {agent['id']}
        """.strip()
        
        self.agent_info_text.setText(info_text)
    
    def select_agent(self):
        """Seleciona o agente atual"""
        if self.selected_agent:
            # Salvar último agente usado
            self.save_last_agent(self.selected_agent)
            
            # Emitir sinal
            self.agent_selected.emit(self.selected_agent)
            self.accept()
    
    def save_last_agent(self, agent):
        """Salva último agente usado"""
        try:
            config_path = "config/last_agent.json"
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "agent": agent,
                    "selected_at": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar último agente: {e}")

class AgentSelectorWidget(QWidget):
    """Widget compacto para seleção de agentes"""
    
    agent_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_agent = None
        self.init_ui()
        self.load_last_agent()
    
    def init_ui(self):
        """Inicializa interface compacta"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Botão com ícone do robô
        self.robot_button = QPushButton()
        self.robot_button.setFixedSize(32, 32)
        self.robot_button.setToolTip("Clique para selecionar agente de IA")
        
        # Definir ícone
        if os.path.exists('static/icons/robot_smiling.png'):
            icon = QIcon('static/icons/robot_smiling.png')
            self.robot_button.setIcon(icon)
            self.robot_button.setIconSize(self.robot_button.size())
        else:
            self.robot_button.setText("🤖")
            self.robot_button.setStyleSheet("font-size: 16px;")
        
        self.robot_button.clicked.connect(self.show_agent_selector)
        
        # Label com agente atual
        self.agent_label = QLabel("Nenhum agente selecionado")
        self.agent_label.setStyleSheet("color: #666666; font-size: 11px;")
        
        layout.addWidget(self.robot_button)
        layout.addWidget(self.agent_label)
        layout.addStretch()
    
    def show_agent_selector(self):
        """Mostra dialog de seleção de agente"""
        dialog = AgentSelectorDialog(self)
        dialog.agent_selected.connect(self.on_agent_selected)
        dialog.exec_()
    
    def on_agent_selected(self, agent):
        """Manipula seleção de agente"""
        self.current_agent = agent
        self.agent_label.setText(f"{agent['name']} ({agent['provider']})")
        self.agent_changed.emit(agent)
    
    def load_last_agent(self):
        """Carrega último agente usado"""
        try:
            config_path = "config/last_agent.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.on_agent_selected(data['agent'])
        except Exception as e:
            print(f"Erro ao carregar último agente: {e}")
    
    def get_current_agent(self):
        """Retorna agente atual"""
        return self.current_agent 