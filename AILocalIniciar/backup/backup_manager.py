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

try:
    import pyzipper
except ImportError:
    raise ImportError("Por favor instale o pacote pyzipper: pip install pyzipper")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DRIVE_FOLDER_NAME = 'AILocalBKPs'

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

    def create_backup(self, source_path, description=None):
        """
        Cria um backup do diretório especificado.
        
        Args:
            source_path (str): Caminho do diretório para fazer backup
            description (str, optional): Descrição do backup
            
        Returns:
            dict: Informações do backup criado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_name = Path(source_path).name
        zip_name = f"{source_name}_{timestamp}.zip"
        zip_path = Path(self.default_dir) / "backups" / zip_name
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        
        password = self._generate_password()
        
        try:
            # Criar backup criptografado
            with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
                zf.setpassword(password.encode('utf-8'))
                
                # Adicionar arquivos ao zip
                for root, _, files in os.walk(source_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(source_path)
                        zf.write(file_path, arcname=str(arcname))
            
            # Preparar informações do backup
            backup_info = {
                'timestamp': datetime.now().isoformat(),
                'filename': zip_name,
                'path': str(zip_path),
                'password': password,
                'description': description or f'Backup de {source_name}',
                'size': zip_path.stat().st_size,
                'google_drive_id': None,
                'google_drive_link': None,
                'status': 'success'
            }
            
            # Salvar no banco de dados
            self.db.add_backup(backup_info)
            
            # Tentar fazer upload para o Google Drive
            if self.google_drive_service and self.drive_folder_id:
                try:
                    file_metadata = {
                        'name': zip_name,
                        'parents': [self.drive_folder_id]
                    }
                    media = MediaFileUpload(zip_path, resumable=True)
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
                    
                    backup_info['google_drive_id'] = file.get('id')
                    backup_info['google_drive_link'] = file.get('webViewLink')
                    
                except Exception as e:
                    logger.error(f"Erro ao fazer upload para o Google Drive: {e}")
            
            return backup_info
            
        except Exception as e:
            error_msg = f"Erro ao criar backup: {e}"
            logger.error(error_msg)
            
            # Registrar falha no banco
            backup_info = {
                'timestamp': datetime.now().isoformat(),
                'filename': zip_name,
                'path': str(zip_path),
                'password': password,
                'description': description,
                'size': 0,
                'google_drive_id': None,
                'google_drive_link': None,
                'status': 'error'
            }
            self.db.add_backup(backup_info)
            
            raise Exception(error_msg)

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