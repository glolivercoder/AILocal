#!/usr/bin/env python3
"""
Script para testar a conexão com o Google Drive usando Service Account
"""

import os
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('google_drive_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

FOLDER_NAME = 'AILocalBKPs'
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDS_FILE = 'service_account_credentials.json'
USER_EMAIL = 'glolivercoder@gmail.com'  # Email do usuário para compartilhar

def get_drive_service():
    """Inicializa e retorna o serviço do Google Drive"""
    try:
        logger.info(f"Tentando carregar credenciais do arquivo: {CREDS_FILE}")
        if not os.path.exists(CREDS_FILE):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {CREDS_FILE}")
        
        credentials = service_account.Credentials.from_service_account_file(
            CREDS_FILE,
            scopes=SCOPES
        )
        logger.info("Credenciais carregadas com sucesso")
        logger.debug(f"Service Account email: {credentials.service_account_email}")
        
        service = build('drive', 'v3', credentials=credentials)
        logger.info("Serviço do Drive construído com sucesso")
        return service
    except Exception as e:
        logger.error(f"Erro ao criar serviço do Drive: {e}", exc_info=True)
        raise

def share_folder(service, folder_id, user_email):
    """Compartilha a pasta com o usuário especificado"""
    try:
        logger.info(f"Compartilhando pasta com {user_email}")
        
        # Primeiro tornar a pasta pública com link
        public_permission = {
            'type': 'anyone',
            'role': 'writer',
            'allowFileDiscovery': True
        }
        
        logger.info("Tornando pasta pública com link de acesso")
        service.permissions().create(
            fileId=folder_id,
            body=public_permission,
            fields='id'
        ).execute()
        
        # Depois compartilhar diretamente com o usuário
        user_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': user_email
        }
        
        logger.info(f"Compartilhando diretamente com {user_email}")
        service.permissions().create(
            fileId=folder_id,
            body=user_permission,
            fields='id',
            sendNotificationEmail=True
        ).execute()
        
        # Verificar permissões finais
        try:
            permissions = service.permissions().list(
                fileId=folder_id,
                fields="permissions(id, emailAddress, role, type)"
            ).execute()
            
            logger.info("Permissões atuais da pasta:")
            for perm in permissions.get('permissions', []):
                logger.info(f"- Type: {perm.get('type')}, Role: {perm.get('role')}, Email: {perm.get('emailAddress')}")
        except Exception as e:
            logger.warning(f"Erro ao listar permissões finais: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao compartilhar pasta: {e}", exc_info=True)
        return False

def find_or_create_folder(service, folder_name):
    """Encontra ou cria uma pasta no Drive"""
    try:
        # Procurar pasta existente
        logger.info(f"Procurando pasta '{folder_name}'")
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = results.get('files', [])
        
        if files:
            folder_id = files[0]['id']
            logger.info(f"Pasta encontrada com ID: {folder_id}")
            return folder_id
            
        # Criar nova pasta no root do Drive
        logger.info(f"Pasta não encontrada. Criando nova pasta '{folder_name}' no root")
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': ['root']  # Isso força a criação na raiz do Drive
        }
        
        file = service.files().create(
            body=file_metadata,
            fields='id, webViewLink'
        ).execute()
        
        folder_id = file.get('id')
        web_link = file.get('webViewLink')
        logger.info(f"Nova pasta criada com ID: {folder_id}")
        logger.info(f"Link público da pasta: {web_link}")
        
        return folder_id
        
    except Exception as e:
        logger.error(f"Erro ao criar/encontrar pasta: {e}", exc_info=True)
        raise

def test_folder_access(service, folder_id):
    """Testa o acesso à pasta criando um arquivo de teste"""
    try:
        # Criar arquivo de teste
        logger.info("Criando arquivo de teste na pasta")
        file_metadata = {
            'name': 'teste_acesso.txt',
            'parents': [folder_id]
        }
        
        content = "Este é um arquivo de teste para verificar o acesso à pasta."
        with open('teste_acesso.txt', 'w', encoding='utf-8') as f:
            f.write(content)
            
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload('teste_acesso.txt', mimetype='text/plain', resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()
        
        logger.info(f"Arquivo de teste criado com sucesso: {file['name']} (ID: {file['id']})")
        
        try:
            os.remove('teste_acesso.txt')
        except:
            pass
        return True
        
    except Exception as e:
        logger.error(f"Erro ao testar acesso à pasta: {e}", exc_info=True)
        return False

def create_public_folder(service, folder_name):
    """Cria uma pasta pública no Drive"""
    try:
        # Criar pasta no root do Drive
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        print(f"\nCriando pasta pública '{folder_name}'...")
        file = service.files().create(
            body=file_metadata,
            fields='id, webViewLink'
        ).execute()
        
        folder_id = file.get('id')
        
        # Tornar a pasta pública
        permission = {
            'type': 'anyone',
            'role': 'writer',
            'allowFileDiscovery': True
        }
        
        print("Configurando permissões públicas...")
        service.permissions().create(
            fileId=folder_id,
            body=permission,
            fields='id'
        ).execute()
        
        # Obter link público
        file = service.files().get(
            fileId=folder_id,
            fields='webViewLink'
        ).execute()
        
        web_link = file.get('webViewLink')
        
        print("\nPasta criada com sucesso!")
        print(f"ID da pasta: {folder_id}")
        print(f"Link público: {web_link}")
        print("\nQualquer pessoa com o link pode acessar e editar a pasta.")
        
        return folder_id, web_link
        
    except Exception as e:
        print(f"\nERRO ao criar pasta: {str(e)}")
        raise

def main():
    """Função principal"""
    try:
        print("\nIniciando configuração da pasta no Google Drive...")
        
        # Inicializar serviço
        service = get_drive_service()
        
        # Criar pasta pública
        folder_id, web_link = create_public_folder(service, FOLDER_NAME)
        
        # Testar criando um arquivo
        print("\nTestando acesso criando arquivo de teste...")
        file_metadata = {
            'name': 'teste_acesso.txt',
            'parents': [folder_id]
        }
        
        content = "Este é um arquivo de teste para verificar o acesso à pasta."
        with open('teste_acesso.txt', 'w', encoding='utf-8') as f:
            f.write(content)
            
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload('teste_acesso.txt', mimetype='text/plain', resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()
        
        print(f"Arquivo de teste criado: {file['name']}")
        
        try:
            os.remove('teste_acesso.txt')
        except:
            pass
            
        print("\nTudo configurado com sucesso!")
        print("\nIMPORTANTE:")
        print(f"1. A pasta '{FOLDER_NAME}' foi criada no Google Drive")
        print("2. A pasta é pública - qualquer pessoa com o link pode acessar")
        print("3. Acesse a pasta pelo link:")
        print(f"   {web_link}")
        
    except Exception as e:
        print(f"\nERRO: {str(e)}")

if __name__ == "__main__":
    main() 