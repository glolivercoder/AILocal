#!/usr/bin/env python3
"""
Gerenciador de Backup com integração Google Drive e relatórios por email
"""

import os
import json
import pyzipper
import random
import string
from datetime import datetime
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupManager:
    """Gerenciador de backup com integração Google Drive e relatórios por email"""
    
    def __init__(self, email_config=None, google_creds_file=None):
        """
        Inicializa o gerenciador de backup.
        
        Args:
            email_config (dict): Configurações de email (smtp_server, port, email, password)
            google_creds_file (str): Caminho para o arquivo de credenciais do Google
        """
        self.email_config = email_config or {}
        self.google_creds_file = google_creds_file
        self.history_file = Path("backup_history.json")
        self.history = self._load_history()
        self.google_drive_service = None
        
        # Inicializar Google Drive se as credenciais estiverem disponíveis
        if google_creds_file:
            self._init_google_drive()

    def _load_history(self):
        """Carrega o histórico de backups"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def _save_history(self):
        """Salva o histórico de backups"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def _init_google_drive(self):
        """Inicializa a conexão com o Google Drive"""
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        creds = None

        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.google_creds_file, SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.google_drive_service = build('drive', 'v3', credentials=creds)

    def _generate_password(self, length=16):
        """Gera uma senha segura para o arquivo zip"""
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

    def _send_email_report(self, to_email, subject, content):
        """Envia relatório por email"""
        if not self.email_config:
            raise ValueError("Configurações de email não definidas")

        msg = MIMEMultipart()
        msg['From'] = self.email_config['email']
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(content, 'html'))

        try:
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['port']) as server:
                server.starttls()
                server.login(self.email_config['email'], self.email_config['password'])
                server.send_message(msg)
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False

    def create_backup(self, project_path, description=""):
        """
        Cria um backup do projeto.
        
        Args:
            project_path (str): Caminho do projeto para backup
            description (str): Descrição opcional do backup
            
        Returns:
            dict: Informações do backup criado
        """
        timestamp = datetime.now()
        backup_name = f"backup_{timestamp.strftime('%Y%m%d_%H%M%S')}.zip"
        backup_path = Path("backups") / backup_name
        backup_path.parent.mkdir(exist_ok=True)
        
        password = self._generate_password()
        
        # Criar zip criptografado
        with pyzipper.AESZipFile(backup_path, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
            zf.setpassword(password.encode('utf-8'))
            
            for root, _, files in os.walk(project_path):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix in ['.git', '.env', '.pyc', '.pyo']:
                        continue
                    arcname = file_path.relative_to(Path(project_path))
                    zf.write(file_path, arcname=str(arcname))

        # Upload para Google Drive
        file_id = None
        if self.google_drive_service:
            try:
                file_metadata = {'name': backup_name}
                media = MediaFileUpload(backup_path, resumable=True)
                file = self.google_drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id, webViewLink'
                ).execute()
                file_id = file.get('id')
                drive_link = file.get('webViewLink')
            except Exception as e:
                logger.error(f"Erro no upload para Google Drive: {e}")
                drive_link = None
        else:
            drive_link = None

        # Registrar no histórico
        backup_info = {
            'timestamp': timestamp.isoformat(),
            'filename': backup_name,
            'path': str(backup_path),
            'password': password,
            'description': description,
            'size': os.path.getsize(backup_path),
            'google_drive_id': file_id,
            'google_drive_link': drive_link,
            'status': 'success'
        }
        
        self.history.append(backup_info)
        self._save_history()
        
        return backup_info

    def generate_report(self, days=None):
        """
        Gera um relatório HTML dos backups.
        
        Args:
            days (int): Número de dias para incluir no relatório. Se None, inclui todos.
            
        Returns:
            str: Relatório em formato HTML
        """
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            backups = [b for b in self.history if datetime.fromisoformat(b['timestamp']) > cutoff]
        else:
            backups = self.history

        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .success { color: green; }
                .failed { color: red; }
            </style>
        </head>
        <body>
            <h2>Relatório de Backups</h2>
            <table>
                <tr>
                    <th>Data</th>
                    <th>Arquivo</th>
                    <th>Tamanho</th>
                    <th>Senha</th>
                    <th>Google Drive</th>
                    <th>Status</th>
                </tr>
        """
        
        for backup in sorted(backups, key=lambda x: x['timestamp'], reverse=True):
            timestamp = datetime.fromisoformat(backup['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            size_mb = round(backup['size'] / (1024 * 1024), 2)
            status_class = 'success' if backup['status'] == 'success' else 'failed'
            
            html += f"""
                <tr>
                    <td>{timestamp}</td>
                    <td>{backup['filename']}</td>
                    <td>{size_mb} MB</td>
                    <td>{backup['password']}</td>
                    <td>{'<a href="' + backup['google_drive_link'] + '">Link</a>' if backup['google_drive_link'] else 'N/A'}</td>
                    <td class="{status_class}">{backup['status']}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        return html

    def send_backup_report(self, to_email, backup_info):
        """
        Envia relatório de backup por email.
        
        Args:
            to_email (str): Email do destinatário
            backup_info (dict): Informações do backup
            
        Returns:
            bool: True se o email foi enviado com sucesso
        """
        timestamp = datetime.fromisoformat(backup_info['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        size_mb = round(backup_info['size'] / (1024 * 1024), 2)
        
        subject = f"Backup Realizado - {timestamp}"
        
        content = f"""
        <html>
        <body>
            <h2>Backup Realizado com Sucesso</h2>
            <p><strong>Data:</strong> {timestamp}</p>
            <p><strong>Arquivo:</strong> {backup_info['filename']}</p>
            <p><strong>Tamanho:</strong> {size_mb} MB</p>
            <p><strong>Senha do ZIP:</strong> {backup_info['password']}</p>
            {'<p><strong>Link Google Drive:</strong> <a href="' + backup_info['google_drive_link'] + '">Acessar Backup</a></p>' if backup_info['google_drive_link'] else ''}
            <p><strong>Status:</strong> {backup_info['status']}</p>
            <hr>
            <p>Este é um email automático. Por favor, não responda.</p>
        </body>
        </html>
        """
        
        return self._send_email_report(to_email, subject, content)

if __name__ == '__main__':
    # Exemplo de uso
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'port': 587,
        'email': 'seu_email@gmail.com',
        'password': 'sua_senha_de_app'
    }
    
    manager = BackupManager(email_config=email_config, google_creds_file='credentials.json')
    
    # Criar backup
    backup_info = manager.create_backup('caminho/do/projeto', description='Backup de teste')
    
    # Enviar relatório
    manager.send_backup_report('destinatario@email.com', backup_info) 