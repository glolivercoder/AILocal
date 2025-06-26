#!/usr/bin/env python3
"""
Gerenciador de Backup com integração Google Drive e relatórios por email
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging
import random
import string
from database import BackupDatabase
import py7zr
import shutil
import time
from typing import Callable, Optional, Dict
import threading

try:
    import py7zr
except ImportError:
    raise ImportError("Por favor instale o pacote py7zr: pip install py7zr")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DRIVE_FOLDER_NAME = 'AILocalBKPs'

class BackupProgress:
    """Classe para armazenar informações de progresso do backup"""
    def __init__(self):
        self.total_size: int = 0
        self.processed_size: int = 0
        self.current_file: str = ""
        self.start_time: float = time.time()
        self.speed: float = 0.0  # bytes/segundo
        self.eta: float = 0.0    # segundos
        self.percent: float = 0.0

def calculate_directory_size(path: str) -> int:
    """Calcula o tamanho total de um diretório"""
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

class BackupManager:
    """Gerenciador de backup com integração Google Drive e relatórios por email"""
    
    def __init__(self, email_config=None, google_creds_file='service_account_credentials.json', default_dir=None):
        """
        Inicializa o gerenciador de backup.
        
        Args:
            email_config (dict): Configurações de email (smtp_server, port, email, password)
            google_creds_file (str): Caminho para o arquivo de credenciais do Google Service Account
            default_dir (str): Diretório padrão para salvar backups
        """
        # Configurações padrão para Gmail
        default_config = {
            'smtp_server': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'use_ssl': False
        }
        
        # Mesclar configurações fornecidas com as padrão
        self.email_config = {**default_config, **(email_config or {})}
        self.default_dir = default_dir or os.getcwd()
        
        # Usar caminho absoluto para as credenciais
        self.google_creds_file = str(Path(__file__).parent / google_creds_file)
        
        # Inicializar banco de dados
        self.db = BackupDatabase()
        
        # Migrar dados do JSON se existir
        json_history = Path("backup_history.json")
        if json_history.exists():
            self.db.migrate_from_json(json_history)
            # Fazer backup do JSON e removê-lo
            json_history.rename(json_history.with_suffix('.json.bak'))
        
        self.google_drive_service = None
        self.drive_folder_id = None
        
        # Inicializar Google Drive se as credenciais estiverem disponíveis
        if os.path.exists(self.google_creds_file):
            self._init_google_drive()
        else:
            logger.error(f"Arquivo de credenciais não encontrado: {self.google_creds_file}")
            self.google_drive_service = None
        
        self.progress = BackupProgress()
        self.progress_callback = None

    def set_progress_callback(self, callback: Callable[[Dict], None]):
        """Define o callback para atualizações de progresso"""
        self.progress_callback = callback

    def _update_progress(self, file_path: str, size: int):
        """Atualiza o progresso do backup e notifica via callback"""
        self.progress.processed_size += size
        self.progress.current_file = os.path.basename(file_path)
        
        # Calcular velocidade (bytes/segundo)
        elapsed_time = time.time() - self.progress.start_time
        if elapsed_time > 0:
            self.progress.speed = self.progress.processed_size / elapsed_time
        
        # Calcular tempo estimado restante
        if self.progress.speed > 0:
            remaining_bytes = self.progress.total_size - self.progress.processed_size
            self.progress.eta = remaining_bytes / self.progress.speed
        
        # Calcular porcentagem
        self.progress.percent = (self.progress.processed_size / self.progress.total_size) * 100
        
        # Notificar via callback
        if self.progress_callback:
            self.progress_callback({
                'current_file': self.progress.current_file,
                'processed_size': self.progress.processed_size,
                'total_size': self.progress.total_size,
                'speed': self.progress.speed,
                'eta': self.progress.eta,
                'percent': self.progress.percent
            })

    def _init_google_drive(self):
        """Inicializa a conexão com o Google Drive usando Service Account"""
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.google_creds_file, 
                scopes=SCOPES
            )
            self.google_drive_service = build('drive', 'v3', credentials=credentials)
            logger.info("Google Drive service inicializado com sucesso usando Service Account")
            
            # Configurar pasta compartilhada
            self.drive_folder_id = self._setup_shared_folder()
            
        except Exception as e:
            logger.error(f"Erro ao inicializar Google Drive service: {e}")
            self.google_drive_service = None

    def _setup_shared_folder(self):
        """Configura a pasta compartilhada no Drive"""
        try:
            # Procurar pasta existente
            query = "name='Compartilhados comigo' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.google_drive_service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            files = results.get('files', [])
            
            if files:
                folder_id = files[0]['id']
                logger.info(f"Usando pasta compartilhada existente: {folder_id}")
            else:
                # Criar pasta compartilhada
                file_metadata = {
                    'name': 'Compartilhados comigo',
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.google_drive_service.files().create(
                    body=file_metadata,
                    fields='id'
                ).execute()
                folder_id = folder.get('id')
                logger.info(f"Nova pasta compartilhada criada: {folder_id}")
            
            # Configurar permissões públicas
            self.google_drive_service.permissions().create(
                fileId=folder_id,
                body={
                    'type': 'anyone',
                    'role': 'writer'
                },
                fields='id'
            ).execute()
            
            logger.info("Permissões da pasta configuradas para acesso público")
            return folder_id
            
        except Exception as e:
            logger.error(f"Erro ao configurar pasta compartilhada: {e}")
            raise

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

        # Determinar configurações do servidor com base no email
        email_domain = self.email_config['email'].split('@')[1].lower()
        
        # Configurações padrão para diferentes provedores
        smtp_configs = {
            'gmail.com': {
                'server': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True,
                'use_ssl': False
            },
            'outlook.com': {
                'server': 'smtp-mail.outlook.com',
                'port': 587,
                'use_tls': True,
                'use_ssl': False
            },
            'hotmail.com': {
                'server': 'smtp-mail.outlook.com',
                'port': 587,
                'use_tls': True,
                'use_ssl': False
            },
            'yahoo.com': {
                'server': 'smtp.mail.yahoo.com',
                'port': 587,
                'use_tls': True,
                'use_ssl': False
            },
            'live.com': {
                'server': 'smtp-mail.outlook.com',
                'port': 587,
                'use_tls': True,
                'use_ssl': False
            }
        }
        
        # Usar configurações personalizadas se fornecidas, senão usar padrão
        config = smtp_configs.get(email_domain, {
            'server': self.email_config.get('smtp_server', 'smtp.gmail.com'),
            'port': self.email_config.get('port', 587),
            'use_tls': True,
            'use_ssl': False
        })

        try:
            # Tentar primeiro com TLS
            if config['use_tls']:
                try:
                    with smtplib.SMTP(config['server'], config['port']) as server:
                server.starttls()
                server.login(self.email_config['email'], self.email_config['password'])
                server.send_message(msg)
            return True
                except Exception as e:
                    logger.warning(f"Falha ao enviar com TLS: {e}")

            # Se falhar com TLS, tentar com SSL
            if config['use_ssl']:
                try:
                    with smtplib.SMTP_SSL(config['server'], config['port']) as server:
                        server.login(self.email_config['email'], self.email_config['password'])
                        server.send_message(msg)
                    return True
                except Exception as e:
                    logger.warning(f"Falha ao enviar com SSL: {e}")

            # Se ambos falharem, tentar sem criptografia
            try:
                with smtplib.SMTP(config['server'], config['port']) as server:
                    server.login(self.email_config['email'], self.email_config['password'])
                    server.send_message(msg)
                return True
            except Exception as e:
                logger.error(f"Todas as tentativas de envio falharam. Último erro: {e}")
                return False

        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False

    def create_backup(self, source_path: str, description: Optional[str] = None) -> Dict:
        """
        Cria um backup do diretório especificado.
        
        Args:
            source_path (str): Caminho do diretório para fazer backup
            description (str, optional): Descrição do backup
            
        Returns:
            dict: Informações do backup criado
        """
        # Resetar progresso
        self.progress = BackupProgress()
        self.progress.total_size = calculate_directory_size(source_path)
        self.progress.start_time = time.time()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_name = Path(source_path).name
        archive_name = f"{source_name}_{timestamp}.7z"
        archive_path = Path(self.default_dir) / "backups" / archive_name
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        
        password = self._generate_password()
        
        try:
            # Criar backup criptografado com 7zip
            filters = [{"id": py7zr.FILTER_LZMA2, "preset": 9}]  # Máxima compressão
            
            def progress_callback(file_path: str, size: int):
                self._update_progress(file_path, size)
            
            with py7zr.SevenZipFile(archive_path, 'w', password=password, filters=filters) as archive:
                # Configurar callback de progresso
                archive.set_encoded_header_mode(True)
                archive.set_encoded_header_key(password.encode())
                archive.set_progress_callback(progress_callback)
                
                # Adicionar arquivos ao 7z com compressão máxima
                archive.writeall(source_path, 'root')

            # Preparar informações do backup
            backup_info = {
                'timestamp': datetime.now().isoformat(),
                'filename': archive_name,
                'path': str(archive_path),
                'password': password,
                'description': description or f'Backup de {source_name}',
                'size': archive_path.stat().st_size,
                'google_drive_id': None,
                'google_drive_link': None,
                'status': 'success'
            }
            
            # Salvar no banco de dados
            self.db.add_backup(backup_info)
            
            # Upload para Google Drive em thread separada
            if self.google_drive_service and self.drive_folder_id:
                thread = threading.Thread(
                    target=self._upload_to_drive,
                    args=(backup_info, archive_path)
                )
                thread.start()
            
            return backup_info

        except Exception as e:
            error_msg = f"Erro ao criar backup: {e}"
            logger.error(error_msg)
            
            backup_info = {
                'timestamp': datetime.now().isoformat(),
                'filename': archive_name,
                'path': str(archive_path),
                'password': password,
                'description': description,
                'size': 0,
                'google_drive_id': None,
                'google_drive_link': None,
                'status': 'error'
            }
            self.db.add_backup(backup_info)
            
            raise Exception(error_msg)

    def _upload_to_drive(self, backup_info: Dict, archive_path: Path):
        """Upload do arquivo para o Google Drive em thread separada"""
        try:
            file_metadata = {
                'name': backup_info['filename'],
                'parents': [self.drive_folder_id]
            }
            media = MediaFileUpload(archive_path, resumable=True)
            file = self.google_drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            # Atualizar informações do Drive no banco
            self.db.update_drive_info(
                backup_info['id'],
                file.get('id'),
                file.get('webViewLink')
            )
            
        except Exception as e:
            logger.error(f"Erro ao fazer upload para o Google Drive: {e}")

    def get_backup_history(self):
        """Retorna o histórico de backups"""
        return self.db.get_all_backups()

    def get_backup_info(self, backup_id):
        """Retorna informações de um backup específico"""
        return self.db.get_backup_by_id(backup_id)

    def send_backup_report(self, to_email, backup_info):
        """
        Envia relatório do backup por email
        
        Args:
            to_email (str): Email do destinatário
            backup_info (dict): Informações do backup
        """
        subject = f"Relatório de Backup - {backup_info['filename']}"
        
        # Criar conteúdo HTML
        content = f"""
        <h2>Relatório de Backup</h2>
        <p><strong>Data:</strong> {datetime.fromisoformat(backup_info['timestamp']).strftime('%d/%m/%Y %H:%M:%S')}</p>
            <p><strong>Arquivo:</strong> {backup_info['filename']}</p>
        <p><strong>Tamanho:</strong> {backup_info['size'] / 1024 / 1024:.2f} MB</p>
        <p><strong>Status:</strong> {'✅ Sucesso' if backup_info['status'] == 'success' else '❌ Erro'}</p>
        <p><strong>Senha:</strong> {backup_info['password']}</p>
        """
        
        if backup_info['google_drive_link']:
            content += f"""
            <p><strong>Link do Google Drive:</strong> 
               <a href="{backup_info['google_drive_link']}">{backup_info['google_drive_link']}</a>
            </p>
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
    
    manager = BackupManager(email_config=email_config, google_creds_file='service_account_credentials.json')
    
    # Criar backup
    backup_info = manager.create_backup('caminho/do/projeto', description='Backup de teste')
    
    # Enviar relatório
    manager.send_backup_report('destinatario@email.com', backup_info) 