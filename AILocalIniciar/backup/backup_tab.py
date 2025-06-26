#!/usr/bin/env python3
"""
Interface gráfica para a aba de backup
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QFileDialog, QMessageBox,
                           QGroupBox, QLineEdit, QProgressBar, QTableWidget,
                           QTableWidgetItem, QHeaderView, QCheckBox, QInputDialog)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QIcon
from datetime import datetime
import json
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices

from backup_manager import BackupManager

class BackupTab(QWidget):
    """Aba de backup com integração Google Drive e relatórios por email"""
    
    backup_finished = pyqtSignal(dict)  # Sinal emitido quando um backup é concluído
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backup_manager = None
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        """Inicializa a interface da aba"""
        layout = QVBoxLayout(self)
        
        # Grupo de Configurações
        config_group = QGroupBox("📝 Configurações")
        config_layout = QVBoxLayout()
        
        # Layout para diretório padrão
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Diretório Padrão:"))
        self.dir_input = QLineEdit()
        self.dir_input.setReadOnly(True)
        dir_layout.addWidget(self.dir_input)
        
        # Botão de selecionar diretório com ícone
        self.select_dir_btn = QPushButton()
        self.select_dir_btn.setIcon(QIcon.fromTheme("folder", QIcon("icons/folder.png")))
        self.select_dir_btn.setToolTip("Selecionar diretório padrão")
        self.select_dir_btn.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.select_dir_btn)
        config_layout.addLayout(dir_layout)
        
        # Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("seu.email@provedor.com")
        email_layout.addWidget(self.email_input)
        config_layout.addLayout(email_layout)
        
        # Senha
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Senha:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Senha do email (ou senha de app para Gmail)")
        password_layout.addWidget(self.password_input)
        config_layout.addLayout(password_layout)

        # Configurações SMTP Avançadas
        smtp_group = QGroupBox("Configurações SMTP Avançadas")
        smtp_layout = QVBoxLayout()

        # Servidor SMTP
        smtp_server_layout = QHBoxLayout()
        smtp_server_layout.addWidget(QLabel("Servidor SMTP:"))
        self.smtp_server_input = QLineEdit()
        self.smtp_server_input.setText("smtp.gmail.com")  # Pré-configurado para Gmail
        self.smtp_server_input.setPlaceholderText("Ex: smtp.gmail.com")
        smtp_server_layout.addWidget(self.smtp_server_input)
        smtp_layout.addLayout(smtp_server_layout)

        # Porta SMTP
        smtp_port_layout = QHBoxLayout()
        smtp_port_layout.addWidget(QLabel("Porta SMTP:"))
        self.smtp_port_input = QLineEdit()
        self.smtp_port_input.setText("587")  # Pré-configurado para Gmail
        self.smtp_port_input.setPlaceholderText("Ex: 587")
        smtp_port_layout.addWidget(self.smtp_port_input)
        smtp_layout.addLayout(smtp_port_layout)

        # Opções de Segurança
        security_layout = QHBoxLayout()
        self.use_tls_checkbox = QCheckBox("Usar TLS")
        self.use_tls_checkbox.setChecked(True)  # Gmail requer TLS
        self.use_ssl_checkbox = QCheckBox("Usar SSL")
        self.use_ssl_checkbox.setChecked(False)  # Gmail não usa SSL na porta 587
        security_layout.addWidget(self.use_tls_checkbox)
        security_layout.addWidget(self.use_ssl_checkbox)
        smtp_layout.addLayout(security_layout)

        # Dica específica para Gmail
        gmail_tip = QLabel(
            "<small>💡 Para Gmail:<br>"
            "1. Use uma senha de app (recomendado)<br>"
            "2. Ative 'Acesso a app menos seguro' na sua conta Google<br>"
            "3. Se usar autenticação de 2 fatores, senha de app é obrigatória</small>"
        )
        gmail_tip.setTextFormat(Qt.RichText)
        smtp_layout.addWidget(gmail_tip)

        smtp_group.setLayout(smtp_layout)
        config_layout.addWidget(smtp_group)
        
        # Dica sobre senhas
        tip_label = QLabel(
            "<small>💡 Para Gmail: Use senha de app ou email alternativo<br>"
            "Para outros provedores: Use sua senha normal</small>"
        )
        tip_label.setTextFormat(Qt.RichText)
        config_layout.addWidget(tip_label)
        
        # Botões de configuração
        btn_layout = QHBoxLayout()
        self.save_config_btn = QPushButton("💾 Salvar Configurações")
        self.save_config_btn.clicked.connect(self.save_config)
        self.test_config_btn = QPushButton("🧪 Testar Configurações")
        self.test_config_btn.clicked.connect(self.test_config)
        btn_layout.addWidget(self.save_config_btn)
        btn_layout.addWidget(self.test_config_btn)
        config_layout.addLayout(btn_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Grupo de Backup
        backup_group = QGroupBox("📦 Backup de Projetos")
        backup_layout = QVBoxLayout()
        
        # Seleção de projeto
        project_layout = QHBoxLayout()
        project_layout.addWidget(QLabel("Projeto:"))
        self.project_path = QLineEdit()
        self.project_path.setReadOnly(True)
        project_layout.addWidget(self.project_path)
        self.browse_btn = QPushButton("📁 Selecionar")
        self.browse_btn.clicked.connect(self.browse_project)
        project_layout.addWidget(self.browse_btn)
        backup_layout.addLayout(project_layout)
        
        # Descrição
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Descrição:"))
        self.description = QLineEdit()
        desc_layout.addWidget(self.description)
        backup_layout.addLayout(desc_layout)
        
        # Botão de backup
        self.backup_btn = QPushButton("🔄 Criar Backup")
        self.backup_btn.clicked.connect(self.create_backup)
        backup_layout.addWidget(self.backup_btn)
        
        # Barra de progresso
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        backup_layout.addWidget(self.progress)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Grupo de Histórico
        history_group = QGroupBox("📋 Histórico de Backups")
        history_layout = QVBoxLayout()
        
        # Barra de pesquisa
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Pesquisar backups...")
        self.search_input.textChanged.connect(self.filter_history)
        search_layout.addWidget(self.search_input)
        history_layout.addLayout(search_layout)
        
        # Tabela de histórico
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)  # Adicionada uma coluna para o botão de relatório
        self.history_table.setHorizontalHeaderLabels([
            "Data", "Arquivo", "Tamanho", "Status", 
            "Link Drive", "Senha", "Ações", "Relatório"  # Nova coluna
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        history_layout.addWidget(self.history_table)
        
        # Botões de histórico
        history_btn_layout = QHBoxLayout()
        
        # Botão de atualizar
        self.refresh_btn = QPushButton("🔄 Atualizar")
        self.refresh_btn.clicked.connect(self.refresh_history)
        history_btn_layout.addWidget(self.refresh_btn)
        
        # Botão de limpar
        self.clear_btn = QPushButton("🗑️ Limpar")
        self.clear_btn.clicked.connect(self.clear_history)
        history_btn_layout.addWidget(self.clear_btn)
        
        # Botão de enviar relatório geral
        self.send_report_btn = QPushButton("📧 Enviar Relatório Geral")
        self.send_report_btn.clicked.connect(self.send_general_report)
        history_btn_layout.addWidget(self.send_report_btn)
        
        history_layout.addLayout(history_btn_layout)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
    def load_config(self):
        """Carrega as configurações salvas"""
        try:
            if os.path.exists('backup_config.json'):
                with open('backup_config.json', 'r') as f:
                    config = json.load(f)
                    self.email_input.setText(config.get('email', ''))
                    self.password_input.setText(config.get('password', ''))
                    self.smtp_server_input.setText(config.get('smtp_server', ''))
                    self.smtp_port_input.setText(str(config.get('port', '')))
                    self.use_tls_checkbox.setChecked(config.get('use_tls', True))
                    self.use_ssl_checkbox.setChecked(config.get('use_ssl', False))
                    
                    # Inicializar backup manager
                    self.init_backup_manager()
        except Exception as e:
            QMessageBox.warning(self, "Aviso", f"Erro ao carregar configurações: {e}")
    
    def save_config(self):
        """Salva as configurações"""
        try:
            config = {
                'email': self.email_input.text(),
                'password': self.password_input.text(),
                'smtp_server': self.smtp_server_input.text(),
                'port': int(self.smtp_port_input.text()) if self.smtp_port_input.text() else None,
                'use_tls': self.use_tls_checkbox.isChecked(),
                'use_ssl': self.use_ssl_checkbox.isChecked()
            }
            
            with open('backup_config.json', 'w') as f:
                json.dump(config, f)
            
            self.init_backup_manager()
            QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar configurações: {e}")
    
    def init_backup_manager(self):
        """Inicializa o gerenciador de backup"""
        email_config = {
            'email': self.email_input.text(),
            'password': self.password_input.text(),
            'smtp_server': self.smtp_server_input.text(),
            'port': int(self.smtp_port_input.text()) if self.smtp_port_input.text() else None,
            'use_tls': self.use_tls_checkbox.isChecked(),
            'use_ssl': self.use_ssl_checkbox.isChecked()
        }
        
        self.backup_manager = BackupManager(
            email_config=email_config,
            google_creds_file='service_account_credentials.json'
        )
        
        self.refresh_history()
    
    def test_config(self):
        """Testa as configurações de email e Google Drive"""
        if not self.backup_manager:
            QMessageBox.warning(self, "Aviso", "Salve as configurações primeiro!")
            return
            
        try:
            # Tentar enviar email de teste
            success = self.backup_manager._send_email_report(
                self.email_input.text(),
                "Teste de Configuração",
                "<h1>Teste de configuração realizado com sucesso!</h1>"
            )
            
            if success:
                QMessageBox.information(self, "Sucesso", "Configurações testadas com sucesso!")
            else:
                QMessageBox.warning(self, "Aviso", "Erro ao enviar email de teste")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao testar configurações: {e}")
    
    def browse_project(self):
        """Abre diálogo para selecionar projeto"""
        path = QFileDialog.getExistingDirectory(self, "Selecionar Projeto")
        if path:
            self.project_path.setText(path)
    
    def select_directory(self):
        """Seleciona diretório padrão"""
        path = QFileDialog.getExistingDirectory(self, "Selecionar Diretório Padrão")
        if path:
            self.dir_input.setText(path)
            if self.backup_manager:
                self.backup_manager.default_dir = path
    
    def create_backup(self):
        """Cria um novo backup"""
        if not self.backup_manager:
            QMessageBox.warning(self, "Aviso", "Configure o gerenciador primeiro!")
            return
            
        if not self.project_path.text():
            QMessageBox.warning(self, "Aviso", "Selecione um projeto para backup!")
            return
            
        try:
            self.progress.setVisible(True)
            self.progress.setValue(0)
            
            # Criar backup
            backup_info = self.backup_manager.create_backup(
                self.project_path.text(),
                description=self.description.text()
            )
            
            self.progress.setValue(50)
            
            # Enviar email se configurado
            if self.email_input.text():
                self.backup_manager.send_backup_report(
                    self.email_input.text(),
                    backup_info
                )
            
            self.progress.setValue(100)
            
            # Atualizar histórico
            self.refresh_history()
            
            # Emitir sinal de conclusão
            self.backup_finished.emit(backup_info)
            
            QMessageBox.information(self, "Sucesso", "Backup criado com sucesso!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao criar backup: {e}")
        finally:
            self.progress.setVisible(False)
    
    def send_general_report(self):
        """Envia relatório geral por email"""
        if not self.backup_manager:
            QMessageBox.warning(self, "Aviso", "Configure o gerenciador primeiro!")
            return
            
        if not self.email_input.text():
            QMessageBox.warning(self, "Aviso", "Configure um email para envio!")
            return
            
        try:
            # Gerar HTML do relatório
            backups = self.backup_manager.get_backup_history()
            
            html = """
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    tr:nth-child(even) { background-color: #f9f9f9; }
                    .success { color: green; }
                    .error { color: red; }
                </style>
            </head>
            <body>
                <h2>Relatório Geral de Backups</h2>
                <table>
                    <tr>
                        <th>Data</th>
                        <th>Arquivo</th>
                        <th>Tamanho</th>
                        <th>Status</th>
                        <th>Link Drive</th>
                        <th>Senha</th>
                    </tr>
            """
            
            for backup in backups:
                timestamp = datetime.fromisoformat(backup['timestamp']).strftime('%d/%m/%Y %H:%M:%S')
                size_mb = f"{backup['size'] / 1024 / 1024:.2f} MB"
                status_class = 'success' if backup['status'] == 'success' else 'error'
                status_text = '✅ Sucesso' if backup['status'] == 'success' else '❌ Erro'
                
                html += f"""
                    <tr>
                        <td>{timestamp}</td>
                        <td>{backup['filename']}</td>
                        <td>{size_mb}</td>
                        <td class="{status_class}">{status_text}</td>
                        <td>{'<a href="' + backup['google_drive_link'] + '">Link</a>' if backup['google_drive_link'] else 'N/A'}</td>
                        <td>{backup['password']}</td>
                    </tr>
                """
            
            html += """
                </table>
            </body>
            </html>
            """
            
            # Enviar email
            success = self.backup_manager._send_email_report(
                self.email_input.text(),
                "Relatório Geral de Backups",
                html
            )
            
            if success:
                QMessageBox.information(self, "Sucesso", "Relatório enviado com sucesso!")
            else:
                QMessageBox.warning(self, "Aviso", "Erro ao enviar relatório")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao enviar relatório: {e}")
    
    def send_backup_report(self, backup_info):
        """Envia relatório de um backup específico por email"""
        if not self.backup_manager:
            QMessageBox.warning(self, "Aviso", "Configure o gerenciador primeiro!")
            return
            
        # Pedir email do destinatário
        email, ok = QInputDialog.getText(
            self, 
            "Enviar Relatório",
            "Email do destinatário:",
            QLineEdit.Normal,
            self.email_input.text()
        )
        
        if ok and email:
            try:
                success = self.backup_manager.send_backup_report(email, backup_info)
                
                if success:
                    QMessageBox.information(self, "Sucesso", "Relatório enviado com sucesso!")
                else:
                    QMessageBox.warning(self, "Aviso", "Erro ao enviar relatório")
                    
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao enviar relatório: {e}")
    
    def refresh_history(self):
        """Atualiza a tabela de histórico"""
        if not self.backup_manager:
            return
            
        try:
            # Limpar tabela
            self.history_table.setRowCount(0)
            
            # Buscar histórico do banco de dados
            backups = self.backup_manager.get_backup_history()
            
            for backup in backups:
                row = self.history_table.rowCount()
                self.history_table.insertRow(row)
                
                # Data
                timestamp = datetime.fromisoformat(backup['timestamp']).strftime('%d/%m/%Y %H:%M:%S')
                self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
                
                # Arquivo
                self.history_table.setItem(row, 1, QTableWidgetItem(backup['filename']))
                
                # Tamanho
                size_mb = f"{backup['size'] / 1024 / 1024:.2f} MB"
                self.history_table.setItem(row, 2, QTableWidgetItem(size_mb))
                
                # Status
                status_item = QTableWidgetItem("✅" if backup['status'] == 'success' else "❌")
                self.history_table.setItem(row, 3, status_item)
                
                # Link Drive
                if backup['google_drive_link']:
                    link_btn = QPushButton("🔗 Abrir")
                    link_btn.clicked.connect(
                        lambda checked, link=backup['google_drive_link']: 
                        QDesktopServices.openUrl(QUrl(link))
                    )
                    self.history_table.setCellWidget(row, 4, link_btn)
                else:
                    self.history_table.setItem(row, 4, QTableWidgetItem("N/A"))
                
                # Senha
                password_btn = QPushButton("📋 Copiar")
                password_btn.clicked.connect(
                    lambda checked, pwd=backup['password']: 
                    QApplication.clipboard().setText(pwd)
                )
                self.history_table.setCellWidget(row, 5, password_btn)
                
                # Ações
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                
                # Botão para abrir diretório
                open_dir_btn = QPushButton("📂")
                open_dir_btn.setToolTip("Abrir diretório")
                open_dir_btn.clicked.connect(
                    lambda checked, path=backup['path']: 
                    QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(path)))
                )
                actions_layout.addWidget(open_dir_btn)
                
                self.history_table.setCellWidget(row, 6, actions_widget)
                
                # Botão de relatório
                report_btn = QPushButton("📧")
                report_btn.setToolTip("Enviar relatório por email")
                report_btn.clicked.connect(
                    lambda checked, info=backup: 
                    self.send_backup_report(info)
                )
                self.history_table.setCellWidget(row, 7, report_btn)
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar histórico: {e}")
    
    def filter_history(self):
        """Filtra a tabela de histórico"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.history_table.rowCount()):
            show_row = False
            for col in range(self.history_table.columnCount()):
                item = self.history_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            
            self.history_table.setRowHidden(row, not show_row)
    
    def clear_history(self):
        """Limpa o histórico de backups"""
        reply = QMessageBox.question(
            self, 
            "Limpar Histórico",
            "Tem certeza que deseja limpar o histórico? Esta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Limpar tabela
                self.history_table.setRowCount(0)
                
                # Limpar banco de dados
                if self.backup_manager:
                    self.backup_manager.db.clear_history()
                
                QMessageBox.information(self, "Sucesso", "Histórico limpo com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao limpar histórico: {e}") 