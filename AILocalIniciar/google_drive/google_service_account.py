"""
Google Service Account Wrapper
Substitui OAuth por Service Account para estabilidade
"""

import os
import json
from pathlib import Path

class GoogleServiceAccount:
    """Gerenciador de Service Account do Google"""
    
    def __init__(self, credentials_path="service_account_credentials.json"):
        self.credentials_path = Path(credentials_path)
        self.credentials = None
        self.service_enabled = False
        
        # Tentar carregar credenciais
        self.load_credentials()
    
    def load_credentials(self):
        """Carrega credenciais do Service Account"""
        try:
            if self.credentials_path.exists():
                with open(self.credentials_path, 'r', encoding='utf-8') as f:
                    self.credentials = json.load(f)
                
                # Verificar se é template ou credenciais reais
                if self.credentials.get("project_id") != "seu-projeto-id":
                    self.service_enabled = True
                    print("✅ Credenciais de Service Account carregadas")
                else:
                    print("⚠️ Usando template - configure credenciais reais")
            else:
                print("⚠️ Arquivo de credenciais não encontrado")
                self.create_placeholder()
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar credenciais: {e}")
            self.service_enabled = False
    
    def create_placeholder(self):
        """Cria placeholder para credenciais"""
        placeholder = {
            "type": "service_account",
            "project_id": "seu-projeto-id",
            "private_key_id": "configure-suas-credenciais",
            "private_key": "-----BEGIN PRIVATE KEY-----\nCONFIGURE_SUA_CHAVE\n-----END PRIVATE KEY-----\n",
            "client_email": "configure@seu-projeto.iam.gserviceaccount.com",
            "client_id": "configure-client-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
        }
        
        with open(self.credentials_path, 'w', encoding='utf-8') as f:
            json.dump(placeholder, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Placeholder criado: {self.credentials_path}")
    
    def is_configured(self):
        """Verifica se Service Account está configurado"""
        return self.service_enabled and self.credentials is not None
    
    def get_drive_service(self):
        """Retorna serviço do Google Drive"""
        if not self.is_configured():
            print("⚠️ Service Account não configurado")
            return None
        
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            # Criar credenciais
            credentials = service_account.Credentials.from_service_account_info(
                self.credentials,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            # Criar serviço
            service = build('drive', 'v3', credentials=credentials)
            print("✅ Serviço Google Drive criado")
            return service
            
        except ImportError:
            print("⚠️ Bibliotecas Google não instaladas")
            print("Execute: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            return None
        except Exception as e:
            print(f"⚠️ Erro ao criar serviço Drive: {e}")
            return None
    
    def get_gmail_service(self):
        """Retorna serviço do Gmail"""
        if not self.is_configured():
            print("⚠️ Service Account não configurado")
            return None
        
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            # Criar credenciais
            credentials = service_account.Credentials.from_service_account_info(
                self.credentials,
                scopes=['https://www.googleapis.com/auth/gmail.readonly']
            )
            
            # Criar serviço
            service = build('gmail', 'v1', credentials=credentials)
            print("✅ Serviço Gmail criado")
            return service
            
        except ImportError:
            print("⚠️ Bibliotecas Google não instaladas")
            return None
        except Exception as e:
            print(f"⚠️ Erro ao criar serviço Gmail: {e}")
            return None
    
    def test_connection(self):
        """Testa conexão com Google Drive"""
        if not self.is_configured():
            return False, "Service Account não configurado"
        
        try:
            drive_service = self.get_drive_service()
            if drive_service:
                # Testar listagem de arquivos
                results = drive_service.files().list(pageSize=1).execute()
                return True, "Conexão com Google Drive bem-sucedida"
            else:
                return False, "Erro ao criar serviço Drive"
                
        except Exception as e:
            return False, f"Erro na conexão: {e}"
    
    def transfer_ownership(self, file_id, new_owner_email):
        """Transfere propriedade de um arquivo/pasta para outro usuário"""
        if not self.is_configured():
            return False, "Service Account não configurado"
            
        try:
            drive_service = self.get_drive_service()
            if not drive_service:
                return False, "Erro ao criar serviço Drive"
                
            # Criar permissão de proprietário
            permission = {
                'type': 'user',
                'role': 'owner',
                'emailAddress': new_owner_email
            }
            
            drive_service.permissions().create(
                fileId=file_id,
                body=permission,
                transferOwnership=True
            ).execute()
            
            print(f"✅ Permissões atualizadas para {new_owner_email}")
            return True, f"Propriedade transferida para {new_owner_email}"
            
        except Exception as e:
            return False, f"Erro ao transferir propriedade: {e}"
            
    def move_to_root(self, file_id):
        """Move um arquivo/pasta para a raiz do Drive"""
        if not self.is_configured():
            return False, "Service Account não configurado"
            
        try:
            drive_service = self.get_drive_service()
            if not drive_service:
                return False, "Erro ao criar serviço Drive"
                
            # Atualizar o arquivo removendo todos os parents
            file = drive_service.files().get(
                fileId=file_id, 
                fields='parents'
            ).execute()
            
            previous_parents = ",".join(file.get('parents', []))
            
            # Mover para a raiz removendo parents anteriores
            drive_service.files().update(
                fileId=file_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            
            return True, "Arquivo/pasta movido para raiz do Drive"
            
        except Exception as e:
            return False, f"Erro ao mover para raiz: {e}"
    
    def share_with_user(self, file_id, user_email):
        """Compartilha um arquivo/pasta com um usuário como editor"""
        if not self.is_configured():
            return False, "Service Account não configurado"
            
        try:
            drive_service = self.get_drive_service()
            if not drive_service:
                return False, "Erro ao criar serviço Drive"
                
            # Criar permissão de editor
            permission = {
                'type': 'user',
                'role': 'writer',
                'emailAddress': user_email
            }
            
            drive_service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            print(f"✅ Permissões de editor concedidas para {user_email}")
            return True, f"Pasta compartilhada com {user_email}"
            
        except Exception as e:
            return False, f"Erro ao compartilhar: {e}"

# Instância global
google_service = GoogleServiceAccount()
