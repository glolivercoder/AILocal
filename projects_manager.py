#!/usr/bin/env python3
"""
Projects Manager: Exportação, Backup e Upload para Google Drive e Terabox
"""

import os
import shutil
import pyzipper
import random
import string
import yagmail
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Google Drive
try:
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False

# Terabox
try:
    from terabox import Terabox
    TERABOX_AVAILABLE = True
except ImportError:
    TERABOX_AVAILABLE = False

class ProjectsManager:
    def __init__(self, backup_dir="backups", email_config=None):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.email_config = email_config or {}
        self.history_file = self.backup_dir / "backup_history.json"
        self.history = self._load_history()
        self.gdrive = None
        self.terabox = None
        self.google_drive_available = False
        self.terabox_available = False
        if GDRIVE_AVAILABLE:
            self._init_gdrive()
            self.google_drive_available = True
        if TERABOX_AVAILABLE:
            self._init_terabox()
            self.terabox_available = True

    def _load_history(self):
        import json
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_history(self):
        import json
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def _init_gdrive(self):
        gauth = GoogleAuth()
        # Tenta autenticação automática (service_account.json na pasta)
        gauth.LoadCredentialsFile("gdrive_creds.txt")
        if gauth.credentials is None:
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()
        gauth.SaveCredentialsFile("gdrive_creds.txt")
        self.gdrive = GoogleDrive(gauth)

    def _init_terabox(self):
        # Espera-se que o usuário já tenha token salvo
        self.terabox = Terabox(token=os.getenv("TERABOX_TOKEN", ""))

    def _generate_password(self, length=12):
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

    def zip_project(self, project_path, password=None):
        project_path = Path(project_path)
        if not project_path.exists():
            raise FileNotFoundError(f"Projeto não encontrado: {project_path}")
        zip_name = f"{project_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = self.backup_dir / zip_name
        password = password or self._generate_password()
        with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_LZMA) as zf:
            zf.setpassword(password.encode())
            for root, _, files in os.walk(project_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(project_path.parent)
                    zf.write(file_path, arcname)
        return zip_path, password

    def upload_gdrive(self, zip_path):
        if not self.gdrive:
            raise RuntimeError("Google Drive não configurado")
        file1 = self.gdrive.CreateFile({'title': Path(zip_path).name})
        file1.SetContentFile(str(zip_path))
        file1.Upload()
        return file1['id']

    def upload_terabox(self, zip_path):
        if not self.terabox:
            raise RuntimeError("Terabox não configurado")
        result = self.terabox.upload(str(zip_path))
        return result.get('url', '')

    def send_password_email(self, to_emails, project_name, password, report):
        yag = yagmail.SMTP(self.email_config['user'], self.email_config['password'])
        subject = f"Senha do backup do projeto {project_name}"
        contents = [
            f"Projeto: {project_name}",
            f"Senha do arquivo zip: {password}",
            f"Relatório: {report}"
        ]
        yag.send(to=to_emails, subject=subject, contents=contents)

    def export_project(self, project_path, to_emails, upload_to=("gdrive", "terabox")):
        zip_path, password = self.zip_project(project_path)
        report = {}
        if "gdrive" in upload_to and self.google_drive_available:
            gdrive_id = self.upload_gdrive(zip_path)
            report['gdrive_id'] = gdrive_id
        if "terabox" in upload_to and self.terabox_available:
            terabox_url = self.upload_terabox(zip_path)
            report['terabox_url'] = terabox_url
        self.send_password_email(to_emails, Path(project_path).name, password, report)
        # Salvar histórico
        entry = {
            "project": str(project_path),
            "zip": str(zip_path),
            "date": datetime.now().isoformat(),
            "report": report,
            "emails": to_emails
        }
        self.history.append(entry)
        self._save_history()
        return entry

    def list_backups(self):
        return self.history

    def search_projects(self, query):
        return [h for h in self.history if query.lower() in h['project'].lower()]

    def list_unsaved_projects(self, projects_dir):
        projects = [p for p in Path(projects_dir).iterdir() if p.is_dir()]
        saved = set(Path(h['project']).name for h in self.history)
        return [p for p in projects if p.name not in saved]

    def upload_to_cloud(self, file_path: str, project_name: str) -> Dict[str, Any]:
        """Upload para nuvem com fallback automático"""
        result = {
            "success": False,
            "service": None,
            "url": None,
            "error": None
        }
        
        # Tentar Google Drive primeiro (mais confiável)
        if self.google_drive_available:
            try:
                result = self.upload_to_google_drive(file_path, project_name)
                if result["success"]:
                    self.log(f"Upload para Google Drive bem-sucedido: {project_name}")
                    return result
            except Exception as e:
                self.log(f"Erro no Google Drive: {str(e)}")
                result["error"] = f"Google Drive: {str(e)}"
        
        # Tentar Terabox se disponível
        if self.terabox_available:
            try:
                result = self.upload_to_terabox(file_path, project_name)
                if result["success"]:
                    self.log(f"Upload para Terabox bem-sucedido: {project_name}")
                    return result
            except Exception as e:
                self.log(f"Erro no Terabox: {str(e)}")
                result["error"] = f"Terabox: {str(e)}"
        
        # Se nenhum serviço funcionou
        if not result["success"]:
            result["error"] = "Nenhum serviço de nuvem disponível. Configure Google Drive ou Terabox."
            self.log("Falha no upload - nenhum serviço disponível")
        
        return result

    def upload_to_google_drive(self, file_path: str, project_name: str) -> Dict[str, Any]:
        """Upload para Google Drive"""
        try:
            # Configurar autenticação
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()
            drive = GoogleDrive(gauth)
            
            # Criar arquivo no Google Drive
            file_drive = drive.CreateFile({
                'title': f"{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                'parents': [{'id': 'root'}]  # Pasta raiz
            })
            
            # Fazer upload
            file_drive.SetContentFile(file_path)
            file_drive.Upload()
            
            return {
                "success": True,
                "service": "Google Drive",
                "url": f"https://drive.google.com/file/d/{file_drive['id']}/view",
                "file_id": file_drive['id']
            }
            
        except Exception as e:
            return {
                "success": False,
                "service": "Google Drive",
                "error": str(e)
            }

    def upload_to_terabox(self, file_path: str, project_name: str) -> Dict[str, Any]:
        """Upload para Terabox (com fallback para Google Drive)"""
        try:
            # Tentar importar terabox
            import terabox
            
            # Configuração do Terabox (exemplo)
            # Nota: Implementação real depende da API do Terabox
            self.log("Terabox não implementado - usando Google Drive como fallback")
            
            # Fallback para Google Drive
            if self.google_drive_available:
                return self.upload_to_google_drive(file_path, project_name)
            else:
                return {
                    "success": False,
                    "service": "Terabox",
                    "error": "Terabox não implementado e Google Drive não disponível"
                }
                
        except ImportError:
            # Se terabox não estiver disponível, usar Google Drive
            if self.google_drive_available:
                self.log("Terabox não disponível - usando Google Drive")
                return self.upload_to_google_drive(file_path, project_name)
            else:
                return {
                    "success": False,
                    "service": "Terabox",
                    "error": "Terabox não disponível e Google Drive não configurado"
                }
        except Exception as e:
            return {
                "success": False,
                "service": "Terabox",
                "error": str(e)
            }

    def get_available_services(self) -> Dict[str, bool]:
        """Retorna serviços disponíveis"""
        return {
            "google_drive": self.google_drive_available,
            "terabox": self.terabox_available,
            "any_service": self.google_drive_available or self.terabox_available
        } 