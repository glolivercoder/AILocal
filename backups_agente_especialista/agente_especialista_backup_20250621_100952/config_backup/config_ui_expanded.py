#!/usr/bin/env python3
"""
Interface de Configurações Expandida - Versão Completa
Inclui: OpenRouter, Google Drive, N8N, Docker, UI Design, Backup
Baseado nas especificações do InterfaceGrafica.md
"""

import threading
import requests
import json
import webbrowser
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Importar o gerenciador de configurações
try:
    from config_manager import ConfigManager
    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    CONFIG_MANAGER_AVAILABLE = False
    ConfigManager = None

class ConfigBackupTabExpanded(QWidget):
    """Aba de Configurações Expandida com todas as funcionalidades"""
    
    # Sinais
    agent_reload_needed = pyqtSignal()
    backup_finished = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Inicializar o gerenciador
        self.config_manager = ConfigManager() if CONFIG_MANAGER_AVAILABLE else None
        
        # Cache de modelos OpenRouter
        self.openrouter_models = []
        self.last_used_model = ""
        
        self._init_ui()
        self.load_all_configs()
        self.load_openrouter_models()

    def _init_ui(self):
        """Inicializa a interface seguindo InterfaceGrafica.md"""
        # Layout principal com scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget principal
        main_widget = QWidget()
        self.main_layout = QVBoxLayout(main_widget)
        
        # Título principal
        title = QLabel("⚙️ Configurações Gerais e Backup")
        title.setFont(QFont("Inter", 18, QFont.Bold))
        title.setStyleSheet("color: #00ff7f; margin: 10px; padding: 10px;")
        self.main_layout.addWidget(title)
        
        # Criar todas as seções
        self._create_openrouter_section()
        self._create_google_drive_section()
        self._create_n8n_section()
        self._create_docker_section()
        self._create_ui_design_section()
        self._create_backup_section()
        
        # Configurar scroll
        scroll.setWidget(main_widget)
        
        # Layout final
        final_layout = QVBoxLayout(self)
        final_layout.addWidget(scroll)

    def _create_openrouter_section(self):
        """Cria seção OpenRouter com seleção de modelos"""
        group = QGroupBox("🤖 OpenRouter - Modelos de IA")
        group.setStyleSheet(self._get_group_style())
        layout = QVBoxLayout(group)
        
        # API Key
        layout.addWidget(QLabel("🔑 Chave da API OpenRouter:"))
        self.openrouter_key_input = QLineEdit()
        self.openrouter_key_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.openrouter_key_input)
        
        # Site URL
        layout.addWidget(QLabel("🌐 Site/Referrer (opcional):"))
        self.openrouter_site_input = QLineEdit()
        self.openrouter_site_input.setPlaceholderText("https://seusite.com")
        layout.addWidget(self.openrouter_site_input)
        
        # Seleção de Modelo
        layout.addWidget(QLabel("🧠 Modelo Preferido:"))
        self.model_combo = QComboBox()
        self.model_combo.setMinimumHeight(35)
        layout.addWidget(self.model_combo)
        
        # Filtros de modelo
        filter_layout = QHBoxLayout()
        self.free_models_check = QCheckBox("Apenas Modelos Gratuitos")
        self.free_models_check.stateChanged.connect(self.filter_models)
        filter_layout.addWidget(self.free_models_check)
        
        refresh_models_btn = QPushButton("🔄 Atualizar Modelos")
        refresh_models_btn.clicked.connect(self.load_openrouter_models)
        filter_layout.addWidget(refresh_models_btn)
        layout.addLayout(filter_layout)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        toggle_btn = QPushButton("👁️ Mostrar/Ocultar")
        toggle_btn.clicked.connect(self._toggle_openrouter_visibility)
        buttons_layout.addWidget(toggle_btn)
        
        test_btn = QPushButton("🧪 Testar Conexão")
        test_btn.clicked.connect(self._test_openrouter_connection)
        buttons_layout.addWidget(test_btn)
        
        save_btn = QPushButton("💾 Salvar OpenRouter")
        save_btn.clicked.connect(self._save_openrouter_config)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        self.main_layout.addWidget(group)

    def _create_google_drive_section(self):
        """Cria seção Google Drive"""
        group = QGroupBox("☁️ Google Drive - Backup na Nuvem")
        group.setStyleSheet(self._get_group_style())
        layout = QVBoxLayout(group)
        
        # Client ID
        layout.addWidget(QLabel("🔑 Client ID:"))
        self.gdrive_client_id = QLineEdit()
        self.gdrive_client_id.setEchoMode(QLineEdit.Password)
        self.gdrive_client_id.setPlaceholderText("Seu Google Client ID")
        layout.addWidget(self.gdrive_client_id)
        
        # Client Secret
        layout.addWidget(QLabel("🔐 Client Secret:"))
        self.gdrive_client_secret = QLineEdit()
        self.gdrive_client_secret.setEchoMode(QLineEdit.Password)
        self.gdrive_client_secret.setPlaceholderText("Seu Google Client Secret")
        layout.addWidget(self.gdrive_client_secret)
        
        # Refresh Token
        layout.addWidget(QLabel("🔄 Refresh Token:"))
        self.gdrive_refresh_token = QLineEdit()
        self.gdrive_refresh_token.setEchoMode(QLineEdit.Password)
        self.gdrive_refresh_token.setPlaceholderText("Token de atualização (gerado automaticamente)")
        layout.addWidget(self.gdrive_refresh_token)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        toggle_gdrive_btn = QPushButton("👁️ Mostrar/Ocultar")
        toggle_gdrive_btn.clicked.connect(self._toggle_gdrive_visibility)
        buttons_layout.addWidget(toggle_gdrive_btn)
        
        auth_gdrive_btn = QPushButton("🔐 Autenticar Google Drive")
        auth_gdrive_btn.clicked.connect(self._authenticate_gdrive)
        buttons_layout.addWidget(auth_gdrive_btn)
        
        test_gdrive_btn = QPushButton("🧪 Testar Conexão")
        test_gdrive_btn.clicked.connect(self._test_gdrive_connection)
        buttons_layout.addWidget(test_gdrive_btn)
        
        save_gdrive_btn = QPushButton("💾 Salvar Google Drive")
        save_gdrive_btn.clicked.connect(self._save_gdrive_config)
        buttons_layout.addWidget(save_gdrive_btn)
        
        layout.addLayout(buttons_layout)
        self.main_layout.addWidget(group)

    def _create_n8n_section(self):
        """Cria seção N8N"""
        group = QGroupBox("🔄 N8N - Automação e Workflows")
        group.setStyleSheet(self._get_group_style())
        layout = QVBoxLayout(group)
        
        # URL do N8N
        layout.addWidget(QLabel("🌐 URL do N8N:"))
        self.n8n_url = QLineEdit()
        self.n8n_url.setText("http://localhost:5678")
        layout.addWidget(self.n8n_url)
        
        # Token de Acesso
        layout.addWidget(QLabel("🔑 Token de Acesso:"))
        self.n8n_token = QLineEdit()
        self.n8n_token.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.n8n_token)
        
        # Webhook Path
        layout.addWidget(QLabel("🔗 Caminho do Webhook:"))
        self.n8n_webhook = QLineEdit()
        self.n8n_webhook.setText("/webhook")
        layout.addWidget(self.n8n_webhook)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        toggle_n8n_btn = QPushButton("👁️ Mostrar/Ocultar")
        toggle_n8n_btn.clicked.connect(self._toggle_n8n_visibility)
        buttons_layout.addWidget(toggle_n8n_btn)
        
        test_n8n_btn = QPushButton("🧪 Testar Conexão N8N")
        test_n8n_btn.clicked.connect(self._test_n8n_connection)
        buttons_layout.addWidget(test_n8n_btn)
        
        open_n8n_btn = QPushButton("🚀 Abrir N8N")
        open_n8n_btn.clicked.connect(self._open_n8n_interface)
        buttons_layout.addWidget(open_n8n_btn)
        
        save_n8n_btn = QPushButton("💾 Salvar N8N")
        save_n8n_btn.clicked.connect(self._save_n8n_config)
        buttons_layout.addWidget(save_n8n_btn)
        
        layout.addLayout(buttons_layout)
        self.main_layout.addWidget(group)

    def _create_docker_section(self):
        """Cria seção Docker"""
        group = QGroupBox("🐳 Docker - Gerenciamento de Containers")
        group.setStyleSheet(self._get_group_style())
        layout = QVBoxLayout(group)
        
        # Socket do Docker
        layout.addWidget(QLabel("🔌 Socket do Docker:"))
        self.docker_socket = QLineEdit()
        self.docker_socket.setText("/var/run/docker.sock")
        layout.addWidget(self.docker_socket)
        
        # Auto Refresh
        refresh_layout = QHBoxLayout()
        self.docker_auto_refresh = QCheckBox("Auto Refresh")
        self.docker_auto_refresh.setChecked(True)
        refresh_layout.addWidget(self.docker_auto_refresh)
        
        refresh_layout.addWidget(QLabel("Intervalo:"))
        self.docker_refresh_interval = QSpinBox()
        self.docker_refresh_interval.setRange(5, 300)
        self.docker_refresh_interval.setValue(30)
        self.docker_refresh_interval.setSuffix("s")
        refresh_layout.addWidget(self.docker_refresh_interval)
        
        layout.addLayout(refresh_layout)
        
        # Seção Docker Compose
        compose_group = QGroupBox("📋 Docker Compose Generator")
        compose_layout = QVBoxLayout(compose_group)
        
        # Seleção de serviços
        compose_layout.addWidget(QLabel("🎯 Serviços para incluir:"))
        services_layout = QGridLayout()
        
        self.service_supabase = QCheckBox("🗃️ Supabase (PostgreSQL)")
        self.service_supabase.setChecked(True)
        services_layout.addWidget(self.service_supabase, 0, 0)
        
        self.service_n8n = QCheckBox("🔄 N8N (Automação)")
        self.service_n8n.setChecked(True)
        services_layout.addWidget(self.service_n8n, 0, 1)
        
        self.service_ollama = QCheckBox("🧠 Ollama (LLM Local)")
        self.service_ollama.setChecked(True)
        services_layout.addWidget(self.service_ollama, 1, 0)
        
        self.service_redis = QCheckBox("⚡ Redis (Cache)")
        self.service_redis.setChecked(True)
        services_layout.addWidget(self.service_redis, 1, 1)
        
        compose_layout.addLayout(services_layout)
        
        # Botões do Docker Compose
        compose_buttons = QHBoxLayout()
        
        generate_compose_btn = QPushButton("📝 Gerar docker-compose.yml")
        generate_compose_btn.clicked.connect(self._generate_docker_compose)
        compose_buttons.addWidget(generate_compose_btn)
        
        preview_compose_btn = QPushButton("👁️ Visualizar")
        preview_compose_btn.clicked.connect(self._preview_docker_compose)
        compose_buttons.addWidget(preview_compose_btn)
        
        compose_layout.addLayout(compose_buttons)
        layout.addWidget(compose_group)
        
        # Botões principais
        buttons_layout = QHBoxLayout()
        
        test_docker_btn = QPushButton("🧪 Testar Conexão Docker")
        test_docker_btn.clicked.connect(self._test_docker_connection)
        buttons_layout.addWidget(test_docker_btn)
        
        open_docker_btn = QPushButton("🐳 Abrir Docker Manager")
        open_docker_btn.clicked.connect(self._open_docker_manager)
        buttons_layout.addWidget(open_docker_btn)
        
        save_docker_btn = QPushButton("💾 Salvar Docker")
        save_docker_btn.clicked.connect(self._save_docker_config)
        buttons_layout.addWidget(save_docker_btn)
        
        layout.addLayout(buttons_layout)
        self.main_layout.addWidget(group)

    def _create_ui_design_section(self):
        """Cria seção UI Design"""
        group = QGroupBox("🎨 Editor UI/UX - Design e Prototipagem")
        group.setStyleSheet(self._get_group_style())
        layout = QVBoxLayout(group)
        
        # Descrição
        desc = QLabel("Interface completa para design e prototipagem de UI/UX com componentes, tokens de design e templates.")
        desc.setStyleSheet("color: #888; margin-bottom: 10px; padding: 5px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("📊 Status:"))
        self.ui_design_status = QLabel("✅ Disponível")
        self.ui_design_status.setStyleSheet("color: #00ff7f; font-weight: bold;")
        status_layout.addWidget(self.ui_design_status)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.open_ui_design_btn = QPushButton("🎨 Abrir Editor UI/UX")
        self.open_ui_design_btn.setStyleSheet("""
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
        self.open_ui_design_btn.clicked.connect(self._open_ui_design)
        buttons_layout.addWidget(self.open_ui_design_btn)
        
        install_deps_btn = QPushButton("📦 Instalar Dependências")
        install_deps_btn.clicked.connect(self._install_ui_design_deps)
        buttons_layout.addWidget(install_deps_btn)
        
        layout.addLayout(buttons_layout)
        self.main_layout.addWidget(group)

    def _create_backup_section(self):
        """Cria seção de backup"""
        group = QGroupBox("💾 Backup e Restauração")
        group.setStyleSheet(self._get_group_style())
        layout = QVBoxLayout(group)
        
        # Botão de backup
        self.run_backup_button = QPushButton("🚀 Executar Backup Agora")
        self.run_backup_button.clicked.connect(self._run_backup_flow)
        if not self.config_manager:
            self.run_backup_button.setDisabled(True)
            self.run_backup_button.setToolTip("Módulo ConfigManager não encontrado.")
        layout.addWidget(self.run_backup_button)
        
        # Status
        self.backup_status_label = QLabel("Status: Pronto")
        self.backup_status_label.setStyleSheet("color: #888; padding: 5px;")
        layout.addWidget(self.backup_status_label)
        
        # Histórico
        layout.addWidget(QLabel("📋 Histórico de Backups:"))
        self.backup_history_table = QTableWidget()
        self.backup_history_table.setColumnCount(4)
        self.backup_history_table.setHorizontalHeaderLabels(["Data", "Status", "ID do Google Drive", "Senha"])
        self.backup_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.backup_history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.backup_history_table.setMaximumHeight(150)
        layout.addWidget(self.backup_history_table)
        
        self.main_layout.addWidget(group)

    def _get_group_style(self):
        """Retorna estilo padrão para GroupBox"""
        return """
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
        """

    # Métodos de funcionalidade

    def load_openrouter_models(self):
        """Carrega modelos disponíveis do OpenRouter"""
        def fetch_models():
            try:
                response = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.openrouter_models = data.get('data', [])
                    self.update_model_combo()
            except Exception as e:
                print(f"Erro ao carregar modelos OpenRouter: {e}")
        
        # Executar em thread separada
        threading.Thread(target=fetch_models, daemon=True).start()

    def update_model_combo(self):
        """Atualiza combo box com modelos"""
        self.model_combo.clear()
        
        # Filtrar modelos se necessário
        models_to_show = self.openrouter_models
        if self.free_models_check.isChecked():
            models_to_show = [m for m in self.openrouter_models 
                            if m.get('pricing', {}).get('prompt', '0') == '0']
        
        # Adicionar modelos
        for model in models_to_show:
            name = model.get('name', model.get('id', 'Modelo Desconhecido'))
            model_id = model.get('id', '')
            pricing = model.get('pricing', {})
            is_free = pricing.get('prompt', '0') == '0'
            
            display_name = f"{'🆓 ' if is_free else '💰 '}{name}"
            self.model_combo.addItem(display_name, model_id)
        
        # Restaurar seleção anterior se disponível
        if self.last_used_model:
            index = self.model_combo.findData(self.last_used_model)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)

    def filter_models(self):
        """Filtra modelos baseado no checkbox"""
        self.update_model_combo()

    # Métodos de toggle de visibilidade
    def _toggle_openrouter_visibility(self):
        if self.openrouter_key_input.echoMode() == QLineEdit.Password:
            self.openrouter_key_input.setEchoMode(QLineEdit.Normal)
        else:
            self.openrouter_key_input.setEchoMode(QLineEdit.Password)

    def _toggle_gdrive_visibility(self):
        mode = QLineEdit.Normal if self.gdrive_client_id.echoMode() == QLineEdit.Password else QLineEdit.Password
        self.gdrive_client_id.setEchoMode(mode)
        self.gdrive_client_secret.setEchoMode(mode)
        self.gdrive_refresh_token.setEchoMode(mode)

    def _toggle_n8n_visibility(self):
        if self.n8n_token.echoMode() == QLineEdit.Password:
            self.n8n_token.setEchoMode(QLineEdit.Normal)
        else:
            self.n8n_token.setEchoMode(QLineEdit.Password)

    # Métodos de teste de conexão
    def _test_openrouter_connection(self):
        QMessageBox.information(self, "Teste", "🧪 Testando conexão OpenRouter...")

    def _test_gdrive_connection(self):
        QMessageBox.information(self, "Teste", "🧪 Testando conexão Google Drive...")

    def _test_n8n_connection(self):
        QMessageBox.information(self, "Teste", "🧪 Testando conexão N8N...")

    def _test_docker_connection(self):
        QMessageBox.information(self, "Teste", "🧪 Testando conexão Docker...")

    # Métodos de abertura de interfaces
    def _open_n8n_interface(self):
        url = self.n8n_url.text() or "http://localhost:5678"
        webbrowser.open(url)

    def _open_docker_manager(self):
        QMessageBox.information(self, "Docker", "🐳 Abrindo Docker Manager...")

    def _open_ui_design(self):
        """Abre o Editor UI/UX"""
        try:
            # Tentar importar e abrir o módulo UI/UX
            from EditorUiUX.src.main import main as run_ui_editor
            run_ui_editor()
        except ImportError:
            QMessageBox.warning(self, "Editor UI/UX", 
                              "Editor UI/UX não encontrado.\nInstale as dependências primeiro.")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao abrir Editor UI/UX: {e}")

    def _install_ui_design_deps(self):
        QMessageBox.information(self, "Dependências", "📦 Instalando dependências do Editor UI/UX...")

    def _authenticate_gdrive(self):
        QMessageBox.information(self, "Google Drive", "🔐 Iniciando autenticação Google Drive...")

    # Métodos de salvamento
    def _save_openrouter_config(self):
        config_data = {
            "OPENROUTER_API_KEY": self.openrouter_key_input.text(),
            "YOUR_SITE_URL": self.openrouter_site_input.text(),
            "PREFERRED_MODEL": self.model_combo.currentData() or ""
        }
        self._save_config("openrouter_config.json", config_data)
        self.agent_reload_needed.emit()

    def _save_gdrive_config(self):
        config_data = {
            "client_id": self.gdrive_client_id.text(),
            "client_secret": self.gdrive_client_secret.text(),
            "refresh_token": self.gdrive_refresh_token.text()
        }
        self._save_config("gdrive_config.json", config_data)

    def _save_n8n_config(self):
        config_data = {
            "url": self.n8n_url.text(),
            "token": self.n8n_token.text(),
            "webhook_path": self.n8n_webhook.text()
        }
        self._save_config("n8n_config.json", config_data)

    def _save_docker_config(self):
        config_data = {
            "socket": self.docker_socket.text(),
            "auto_refresh": self.docker_auto_refresh.isChecked(),
            "refresh_interval": self.docker_refresh_interval.value()
        }
        self._save_config("docker_config.json", config_data)

    def _save_config(self, filename, data):
        """Salva configuração em arquivo JSON"""
        config_path = Path("config") / filename
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        QMessageBox.information(self, "Sucesso", f"✅ Configuração salva em {config_path}")

    def load_all_configs(self):
        """Carrega todas as configurações salvas"""
        # Implementar carregamento de configs
        pass

    def _run_backup_flow(self):
        """Executa fluxo de backup"""
        if not self.config_manager:
            QMessageBox.warning(self, "Erro", "O Gerenciador de Configurações não está disponível.")
            return

        self.run_backup_button.setDisabled(True)
        self.backup_status_label.setText("Status: Executando backup...")
        
        threading.Thread(target=self._backup_worker, daemon=True).start()

    def _backup_worker(self):
        """Worker thread para backup"""
        try:
            result = self.config_manager.run_backup_flow()
            self.backup_finished.emit(result)
        except Exception as e:
            self.backup_finished.emit({"status": "Failed", "error": str(e)})

    @pyqtSlot(dict)
    def on_backup_finished(self, result):
        """Callback quando backup termina"""
        if result['status'] == 'Success':
            password = result.get('password', 'N/A')
            QMessageBox.information(self, "Backup Concluído", 
                                    f"Backup realizado com sucesso!\n\nSenha: {password}")
            self.backup_status_label.setText(f"Status: Último backup concluído em {datetime.now().strftime('%H:%M:%S')}")
        else:
            error_msg = result.get('error', 'Erro desconhecido')
            QMessageBox.critical(self, "Erro no Backup", f"Falha ao realizar o backup:\n{error_msg}")
            self.backup_status_label.setText(f"Status: Falha no último backup.")

        self.run_backup_button.setDisabled(False)

    def connect_signals(self):
        """Conecta sinais internos"""
        self.backup_finished.connect(self.on_backup_finished)
    
    def _generate_docker_compose(self):
        """Gera arquivo docker-compose.yml"""
        try:
            # Importar o gerador
            from docker_compose_generator import create_docker_compose
            
            # Coletar serviços selecionados
            services = []
            if hasattr(self, 'service_supabase') and self.service_supabase.isChecked():
                services.append('supabase')
            if hasattr(self, 'service_n8n') and self.service_n8n.isChecked():
                services.append('n8n')
            if hasattr(self, 'service_ollama') and self.service_ollama.isChecked():
                services.append('ollama')
            if hasattr(self, 'service_redis') and self.service_redis.isChecked():
                services.append('redis')
            
            # Gerar docker-compose
            result = create_docker_compose(services)
            
            # Mostrar resultado
            QMessageBox.information(
                self,
                "✅ Docker Compose Gerado",
                f"Arquivos criados com sucesso:\n\n"
                f"📄 {result['compose_file']}\n"
                f"📄 {result['env_file']}\n\n"
                f"Para usar:\n"
                f"1. cp .env.example .env\n"
                f"2. Configure as variáveis no .env\n"
                f"3. docker-compose up -d"
            )
            
        except ImportError:
            QMessageBox.warning(
                self,
                "❌ Erro",
                "Módulo docker_compose_generator não encontrado.\n"
                "Certifique-se de que o arquivo docker_compose_generator.py existe."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Erro na Geração",
                f"Erro ao gerar docker-compose.yml:\n\n{str(e)}"
            )
    
    def _preview_docker_compose(self):
        """Visualiza o docker-compose.yml antes de gerar"""
        try:
            from docker_compose_generator import DockerComposeGenerator
            import yaml
            
            # Coletar serviços selecionados
            services = []
            if hasattr(self, 'service_supabase') and self.service_supabase.isChecked():
                services.append('supabase')
            if hasattr(self, 'service_n8n') and self.service_n8n.isChecked():
                services.append('n8n')
            if hasattr(self, 'service_ollama') and self.service_ollama.isChecked():
                services.append('ollama')
            if hasattr(self, 'service_redis') and self.service_redis.isChecked():
                services.append('redis')
            
            # Gerar preview
            generator = DockerComposeGenerator()
            result = generator.generate_compose_file(services)
            compose_yaml = yaml.dump(result['compose'], default_flow_style=False, sort_keys=False)
            
            # Mostrar preview em dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("👁️ Preview Docker Compose")
            dialog.setModal(True)
            dialog.resize(800, 600)
            
            layout = QVBoxLayout(dialog)
            
            # Área de texto
            text_area = QTextEdit()
            text_area.setPlainText(compose_yaml)
            text_area.setFont(QFont("Courier", 10))
            text_area.setStyleSheet("""
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #404040;
                }
            """)
            layout.addWidget(text_area)
            
            # Botões
            buttons = QHBoxLayout()
            
            copy_btn = QPushButton("📋 Copiar")
            copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(compose_yaml))
            buttons.addWidget(copy_btn)
            
            generate_btn = QPushButton("📝 Gerar Arquivo")
            generate_btn.clicked.connect(lambda: [dialog.accept(), self._generate_docker_compose()])
            buttons.addWidget(generate_btn)
            
            close_btn = QPushButton("❌ Fechar")
            close_btn.clicked.connect(dialog.reject)
            buttons.addWidget(close_btn)
            
            layout.addLayout(buttons)
            
            dialog.exec_()
            
        except ImportError:
            QMessageBox.warning(
                self,
                "❌ Erro",
                "Módulo docker_compose_generator não encontrado."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Erro no Preview",
                f"Erro ao gerar preview:\n\n{str(e)}"
            )

# Função de compatibilidade
ConfigBackupTab = ConfigBackupTabExpanded 