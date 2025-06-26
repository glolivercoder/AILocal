#!/usr/bin/env python3
"""
Interface gráfica para a aba de backup
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QFileDialog, QMessageBox,
                           QGroupBox, QLineEdit, QProgressBar, QTableWidget,
                           QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QIcon
from datetime import datetime
import json
import os
from pathlib import Path

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
        
        # Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("seu.email@gmail.com")
        email_layout.addWidget(self.email_input)
        config_layout.addLayout(email_layout)
        
        # Senha do App
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Senha do App:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Senha de app do Gmail")
        password_layout.addWidget(self.password_input)
        config_layout.addLayout(password_layout)
        
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
        
        # Tabela de histórico
        history_group = QGroupBox("📋 Histórico de Backups")
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Data", "Arquivo", "Tamanho", "Senha", "Google Drive", "Status"
        ])
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        history_layout.addWidget(self.history_table)
        
        # Botões de histórico
        history_btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 Atualizar")
        self.refresh_btn.clicked.connect(self.refresh_history)
        self.report_btn = QPushButton("📧 Enviar Relatório")
        self.report_btn.clicked.connect(self.send_report)
        history_btn_layout.addWidget(self.refresh_btn)
        history_btn_layout.addWidget(self.report_btn)
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
                    
                    # Inicializar backup manager
                    self.init_backup_manager()
        except Exception as e:
            QMessageBox.warning(self, "Aviso", f"Erro ao carregar configurações: {e}")
    
    def save_config(self):
        """Salva as configurações"""
        try:
            config = {
                'email': self.email_input.text(),
                'password': self.password_input.text()
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
            'smtp_server': 'smtp.gmail.com',
            'port': 587,
            'email': self.email_input.text(),
            'password': self.password_input.text()
        }
        
        self.backup_manager = BackupManager(
            email_config=email_config,
            google_creds_file='credentials.json'
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
    
    def create_backup(self):
        """Cria um backup do projeto selecionado"""
        if not self.backup_manager:
            QMessageBox.warning(self, "Aviso", "Configure o backup primeiro!")
            return
            
        if not self.project_path.text():
            QMessageBox.warning(self, "Aviso", "Selecione um projeto primeiro!")
            return
            
        try:
            self.progress.setVisible(True)
            self.progress.setValue(0)
            
            # Criar backup
            backup_info = self.backup_manager.create_backup(
                self.project_path.text(),
                self.description.text()
            )
            
            self.progress.setValue(50)
            
            # Enviar email
            if backup_info['status'] == 'success':
                self.backup_manager.send_backup_report(
                    self.email_input.text(),
                    backup_info
                )
            
            self.progress.setValue(100)
            self.backup_finished.emit(backup_info)
            
            QMessageBox.information(self, "Sucesso", "Backup criado e enviado com sucesso!")
            self.refresh_history()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao criar backup: {e}")
        finally:
            self.progress.setVisible(False)
    
    def refresh_history(self):
        """Atualiza a tabela de histórico"""
        if not self.backup_manager:
            return
            
        try:
            history = self.backup_manager.history
            self.history_table.setRowCount(len(history))
            
            for row, backup in enumerate(sorted(history, key=lambda x: x['timestamp'], reverse=True)):
                timestamp = datetime.fromisoformat(backup['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                size_mb = round(backup['size'] / (1024 * 1024), 2)
                
                self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
                self.history_table.setItem(row, 1, QTableWidgetItem(backup['filename']))
                self.history_table.setItem(row, 2, QTableWidgetItem(f"{size_mb} MB"))
                self.history_table.setItem(row, 3, QTableWidgetItem(backup['password']))
                
                drive_item = QTableWidgetItem()
                if backup['google_drive_link']:
                    drive_item.setText("Link")
                    drive_item.setData(Qt.UserRole, backup['google_drive_link'])
                else:
                    drive_item.setText("N/A")
                self.history_table.setItem(row, 4, drive_item)
                
                status_item = QTableWidgetItem(backup['status'])
                status_item.setForeground(Qt.green if backup['status'] == 'success' else Qt.red)
                self.history_table.setItem(row, 5, status_item)
                
        except Exception as e:
            QMessageBox.warning(self, "Aviso", f"Erro ao atualizar histórico: {e}")
    
    def send_report(self):
        """Envia relatório completo por email"""
        if not self.backup_manager:
            QMessageBox.warning(self, "Aviso", "Configure o backup primeiro!")
            return
            
        try:
            report = self.backup_manager.generate_report()
            success = self.backup_manager._send_email_report(
                self.email_input.text(),
                "Relatório de Backups",
                report
            )
            
            if success:
                QMessageBox.information(self, "Sucesso", "Relatório enviado com sucesso!")
            else:
                QMessageBox.warning(self, "Aviso", "Erro ao enviar relatório")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao enviar relatório: {e}") 