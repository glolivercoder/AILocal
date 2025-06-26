from pathlib import Path
from typing import Optional, Dict, List, Any, Set, Union, Callable
import os
import time
import logging
from datetime import datetime
import sqlite3
import shutil
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyzipper  # Para zip com senha

from .database import BackupDatabase

class BackupManager:
    """
    Gerenciador de backups usando Google Drive.
    
    Esta classe é responsável por criar, gerenciar e excluir backups,
    além de fazer upload para o Google Drive usando uma conta de serviço.
    Os backups são armazenados localmente e suas informações são 
    registradas em um banco SQLite.
    
    Attributes:
        backup_dir (Path): Diretório onde os backups são armazenados
        db (BackupDatabase): Interface com o banco de dados
        logger (logging.Logger): Logger para registro de operações
        drive_service: Serviço do Google Drive
        folder_id: ID da pasta BackupSmart no Google Drive
    """
    
    def __init__(self, backup_dir: str = "backups"):
        """Inicializa o gerenciador de backups"""
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configura logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler("backup.log")
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Carrega configurações
        config_path = Path(__file__).parent / "backup_config.json"
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {str(e)}")
            self.config = {}
        
        # Conecta ao banco
        self.db = BackupDatabase()
        
        # Configura Google Drive
        try:
            credentials = service_account.Credentials.from_service_account_file(
                Path(__file__).parent / 'service_account_credentials.json',
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            self.drive_service = build('drive', 'v3', credentials=credentials)
            self.folder_id = self._get_or_create_folder()
            self.logger.info("Google Drive configurado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao configurar Google Drive: {str(e)}")
            self.drive_service = None
            self.folder_id = None
        
    def _get_or_create_folder(self) -> Optional[str]:
        """Obtém ou cria pasta 'BackupSmart' no Drive"""
        if not self.drive_service:
            return None
            
        # Procura pasta existente
        results = self.drive_service.files().list(
            q="name='BackupSmart' and mimeType='application/vnd.google-apps.folder'",
            fields="files(id, name)"
        ).execute()
        
        items = results.get('files', [])
        
        if items:
            return items[0]['id']
            
        # Cria nova pasta
        file_metadata = {
            'name': 'BackupSmart',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        file = self.drive_service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        return file.get('id')

    def create_backup(
        self,
        source_dir: str,
        name: str,
        password: Optional[str] = None,
        send_email: bool = True
    ) -> Dict[str, Any]:
        """Cria um novo backup"""
        try:
            # Valida entrada
            source_path = Path(source_dir)
            if not source_path.exists():
                raise ValueError(f"Diretório não encontrado: {source_dir}")
                
            # Gera nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_name = f"{name}_{timestamp}.zip"
            zip_path = self.backup_dir / zip_name
            
            # Cria backup
            if password:
                # Usa pyzipper para criptografia
                with pyzipper.AESZipFile(
                    zip_path,
                    'w',
                    compression=pyzipper.ZIP_LZMA,
                    encryption=pyzipper.WZ_AES
                ) as zf:
                    zf.setpassword(password.encode())
                    
                    for file in source_path.rglob('*'):
                        if file.is_file():
                            arcname = file.relative_to(source_path)
                            zf.write(file, arcname)
            else:
                # Backup sem senha
                shutil.make_archive(
                    str(zip_path.with_suffix('')),
                    'zip',
                    source_dir
                )
                
            # Upload para Drive
            drive_link = None
            if self.drive_service and self.folder_id:
                try:
                    file_metadata = {
                        'name': zip_name,
                        'parents': [self.folder_id]
                    }
                    
                    media = MediaFileUpload(
                        zip_path,
                        mimetype='application/zip',
                        resumable=True
                    )
                    
                    file = self.drive_service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id, webViewLink'
                    ).execute()
                    
                    drive_link = file.get('webViewLink')
                    
                except Exception as e:
                    self.logger.error(f"Erro no upload para Drive: {str(e)}")
                    
            # Salva no banco
            backup_info = {
                'name': name,
                'filename': zip_name,
                'created_at': timestamp,
                'size': os.path.getsize(zip_path),
                'drive_link': drive_link,
                'password': password is not None
            }
            
            self.db.add_backup(backup_info)
            
            # Envia email
            if send_email:
                self._send_backup_report(backup_info)
                
            return backup_info
            
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {str(e)}")
            raise

    def _send_backup_report(self, backup_info: Dict[str, Any]):
        """Envia relatório por email"""
        try:
            # Obtém configurações
            email_config = self.config.get('email', {})
            if not email_config:
                return
                
            # Configura servidor
            server = smtplib.SMTP(
                email_config['smtp_server'],
                email_config['smtp_port']
            )
            
            if email_config.get('use_tls'):
                server.starttls()
                
            server.login(
                email_config['username'],
                email_config['password']
            )
            
            # Prepara mensagem
            msg = MIMEMultipart()
            msg['From'] = email_config['username']
            msg['To'] = email_config['username']  # Envia para si mesmo
            msg['Subject'] = f"Relatório de Backup - {backup_info['name']}"
            
            body = f"""
            Backup realizado com sucesso!
            
            Nome: {backup_info['name']}
            Arquivo: {backup_info['filename']}
            Data: {backup_info['created_at']}
            Tamanho: {backup_info['size']} bytes
            
            Link do Drive: {backup_info.get('drive_link', 'N/A')}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Envia
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar email: {str(e)}")

    def list_backups(self) -> List[Dict[str, Any]]:
        """Lista todos os backups"""
        return self.db.list_backups()
        
    def delete_backups(self, names: List[str]):
        """Remove backups por nome"""
        for name in names:
            try:
                # Obtém info do backup
                backup = self.db.get_backup(name)
                if not backup:
                    continue
                    
                # Remove arquivo local
                zip_path = self.backup_dir / backup['filename']
                if zip_path.exists():
                    zip_path.unlink()
                    
                # Remove do Drive
                if backup.get('drive_link'):
                    try:
                        file_id = backup['drive_link'].split('/')[-1]
                        self.drive_service.files().delete(fileId=file_id).execute()
                    except Exception as e:
                        self.logger.error(f"Erro ao remover do Drive: {str(e)}")
                        
                # Remove do banco
                self.db.delete_backup(name)
                
            except Exception as e:
                self.logger.error(f"Erro ao remover backup {name}: {str(e)}")

    def delete_all_backups(self):
        """Remove todos os backups"""
        try:
            # Remove arquivos locais
            for file in self.backup_dir.glob("*.zip"):
                file.unlink()
                
            # Remove do Drive
            if self.drive_service and self.folder_id:
                try:
                    # Lista todos os arquivos na pasta
                    results = self.drive_service.files().list(
                        q=f"'{self.folder_id}' in parents",
                        fields="files(id)"
                    ).execute()
                    
                    # Remove cada arquivo
                    for file in results.get('files', []):
                        self.drive_service.files().delete(
                            fileId=file['id']
                        ).execute()
                        
                except Exception as e:
                    self.logger.error(f"Erro ao limpar Drive: {str(e)}")
                    
            # Limpa banco
            self.db.clear()
            
        except Exception as e:
            self.logger.error(f"Erro ao remover todos os backups: {str(e)}")
            raise
            
    def send_general_report(self):
        """Envia relatório geral por email"""
        try:
            # Obtém lista de backups
            backups = self.list_backups()
            
            # Prepara corpo do email
            body = """
            Relatório Geral de Backups
            
            Total de backups: {}
            Último backup: {}
            Espaço total: {:.2f} MB
            
            Lista de backups:
            """.format(
                len(backups),
                backups[0]['created_at'] if backups else "N/A",
                sum(b['size'] for b in backups) / 1024 / 1024
            )
            
            # Adiciona lista detalhada
            for backup in backups:
                body += f"""
                Nome: {backup['name']}
                Data: {backup['created_at']}
                Tamanho: {backup['size'] / 1024 / 1024:.2f} MB
                Drive: {backup.get('drive_link', 'N/A')}
                Senha: {'Sim' if backup.get('password') else 'Não'}
                ---
                """
                
            # Envia email
            email_config = self.config.get('email', {})
            if not email_config:
                raise ValueError("Configurações de email não encontradas")
                
            msg = MIMEMultipart()
            msg['From'] = email_config['username']
            msg['To'] = email_config['username']
            msg['Subject'] = "Relatório Geral de Backups"
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                if email_config.get('use_tls'):
                    server.starttls()
                server.login(email_config['username'], email_config['password'])
                server.send_message(msg)
                
        except Exception as e:
            self.logger.error(f"Erro ao enviar relatório geral: {str(e)}")
            raise