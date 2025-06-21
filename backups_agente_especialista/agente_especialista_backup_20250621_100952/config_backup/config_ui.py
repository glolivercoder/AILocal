import threading
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QGroupBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox)
from PyQt5.QtCore import pyqtSignal, pyqtSlot

# Importar o gerenciador de configurações
try:
    from config_manager import ConfigManager
    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    CONFIG_MANAGER_AVAILABLE = False
    ConfigManager = None

class ConfigBackupTab(QWidget):
    """
    Um QWidget que encapsula toda a funcionalidade da aba de Configurações e Backup.
    """
    # Sinal para indicar que o agente precisa ser recarregado após salvar a config
    agent_reload_needed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Inicializar o gerenciador
        self.config_manager = ConfigManager() if CONFIG_MANAGER_AVAILABLE else None

        self._init_ui()
        self.load_api_config_into_tab()
        self.refresh_backup_history()

    def _init_ui(self):
        """Inicializa a interface do usuário da aba."""
        main_layout = QVBoxLayout(self)
        
        # --- Grupo de Configurações de API ---
        api_group_box = self._create_api_group()
        main_layout.addWidget(api_group_box)

        # --- Grupo de Backup e Restauração ---
        backup_group_box = self._create_backup_group()
        main_layout.addWidget(backup_group_box)
        
        self.setLayout(main_layout)

    def _create_api_group(self):
        """Cria o QGroupBox para configuração de API."""
        group_box = QGroupBox("Configuração de Chaves de API")
        layout = QVBoxLayout()
        
        self.api_widgets = {}

        layout.addWidget(QLabel("Chave da API OpenRouter:"))
        self.api_widgets['key_input'] = QLineEdit()
        self.api_widgets['key_input'].setEchoMode(QLineEdit.Password)
        layout.addWidget(self.api_widgets['key_input'])

        layout.addWidget(QLabel("Seu Site/Referrer (opcional):"))
        self.api_widgets['referrer_input'] = QLineEdit()
        layout.addWidget(self.api_widgets['referrer_input'])
        
        buttons_layout = QHBoxLayout()
        toggle_button = QPushButton("Mostrar/Ocultar Chave")
        toggle_button.clicked.connect(self._toggle_api_visibility)
        buttons_layout.addWidget(toggle_button)

        save_button = QPushButton("Salvar Configuração da API")
        save_button.clicked.connect(self._save_api_config)
        buttons_layout.addWidget(save_button)

        layout.addLayout(buttons_layout)
        group_box.setLayout(layout)
        return group_box

    def _create_backup_group(self):
        """Cria o QGroupBox para a funcionalidade de backup."""
        group_box = QGroupBox("Backup de Configurações no Google Drive")
        layout = QVBoxLayout()

        self.run_backup_button = QPushButton("Executar Backup Agora")
        self.run_backup_button.clicked.connect(self._run_backup_flow)
        if not self.config_manager:
            self.run_backup_button.setDisabled(True)
            self.run_backup_button.setToolTip("Módulo ConfigManager não encontrado.")
        
        self.backup_status_label = QLabel("Status: Pronto")
        
        layout.addWidget(self.run_backup_button)
        layout.addWidget(self.backup_status_label)

        layout.addWidget(QLabel("Histórico de Backups:"))
        self.backup_history_table = QTableWidget()
        self.backup_history_table.setColumnCount(4)
        self.backup_history_table.setHorizontalHeaderLabels(["Data", "Status", "ID do Google Drive", "Senha"])
        self.backup_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.backup_history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.backup_history_table)
        group_box.setLayout(layout)
        return group_box
        
    def _toggle_api_visibility(self):
        if self.api_widgets['key_input'].echoMode() == QLineEdit.Password:
            self.api_widgets['key_input'].setEchoMode(QLineEdit.Normal)
        else:
            self.api_widgets['key_input'].setEchoMode(QLineEdit.Password)

    def _save_api_config(self):
        """Salva a configuração da API em config/agent_config.json."""
        api_key = self.api_widgets['key_input'].text()
        site_url = self.api_widgets['referrer_input'].text()

        if not api_key:
            QMessageBox.warning(self, "Chave da API Faltando", "Por favor, insira sua chave da API OpenRouter.")
            return

        config_data = {"OPENROUTER_API_KEY": api_key, "YOUR_SITE_URL": site_url}
        config_path = Path("config/agent_config.json")
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            import json
            json.dump(config_data, f, indent=2)
            
        QMessageBox.information(self, "Configuração Salva", f"Configuração da API salva em {config_path}")
        self.agent_reload_needed.emit() # Emite sinal para a janela principal

    def load_api_config_into_tab(self):
        """Lê o arquivo de configuração e preenche os campos."""
        config_path = Path("config/agent_config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                import json
                config = json.load(f)
            self.api_widgets['key_input'].setText(config.get("OPENROUTER_API_KEY", ""))
            self.api_widgets['referrer_input'].setText(config.get("YOUR_SITE_URL", ""))

    def _run_backup_flow(self):
        if not self.config_manager:
            QMessageBox.warning(self, "Erro", "O Gerenciador de Configurações não está disponível.")
            return

        self.run_backup_button.setDisabled(True)
        self.backup_status_label.setText("Status: Executando backup... Isso pode levar um momento e pode pedir autenticação no navegador.")
        
        threading.Thread(target=self._backup_worker).start()

    def _backup_worker(self):
        try:
            result = self.config_manager.run_backup_flow()
            # O resultado será tratado no slot conectado a este sinal
            self.backup_finished.emit(result) 
        except Exception as e:
            self.backup_finished.emit({"status": "Failed", "error": str(e)})

    @pyqtSlot(dict)
    def on_backup_finished(self, result):
        if result['status'] == 'Success':
            password = result.get('password', 'N/A')
            QMessageBox.information(self, "Backup Concluído", 
                                    f"Backup realizado com sucesso!\n\nA senha do arquivo é: {password}\n\n"
                                    "Esta senha foi salva no histórico. É recomendado guardá-la em um local seguro.")
            self.backup_status_label.setText(f"Status: Último backup concluído em {datetime.now().strftime('%H:%M:%S')}")
        else:
            error_msg = result.get('error', 'Erro desconhecido')
            QMessageBox.critical(self, "Erro no Backup", f"Falha ao realizar o backup:\n{error_msg}")
            self.backup_status_label.setText(f"Status: Falha no último backup.")

        self.run_backup_button.setDisabled(False)
        self.refresh_backup_history()

    def refresh_backup_history(self):
        if not self.config_manager:
            return
        
        history = self.config_manager.list_backups()
        self.backup_history_table.setRowCount(0)
        
        for item in reversed(history):
            row_position = self.backup_history_table.rowCount()
            self.backup_history_table.insertRow(row_position)
            
            date = datetime.fromisoformat(item.get('date')).strftime('%Y-%m-%d %H:%M:%S')
            status = item.get('status', 'N/A')
            gdrive_info = item.get('gdrive_info')
            gdrive_id = gdrive_info.get('id', 'N/A') if gdrive_info else "Upload desabilitado"
            password = item.get('password', 'N/A')

            self.backup_history_table.setItem(row_position, 0, QTableWidgetItem(date))
            self.backup_history_table.setItem(row_position, 1, QTableWidgetItem(status))
            self.backup_history_table.setItem(row_position, 2, QTableWidgetItem(gdrive_id))
            self.backup_history_table.setItem(row_position, 3, QTableWidgetItem(password))

    # Sinal para o processo de backup
    backup_finished = pyqtSignal(dict)
    
    def connect_signals(self):
        """Conecta os sinais da thread aos slots da UI."""
        self.backup_finished.connect(self.on_backup_finished) 