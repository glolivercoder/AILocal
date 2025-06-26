#!/usr/bin/env python3
"""
Script para ajustar as pastas no Google Drive
"""

import os
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDS_FILE = 'service_account_credentials.json'

def get_drive_service():
    """Inicializa e retorna o serviço do Google Drive"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDS_FILE,
            scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=credentials)
        return service
    except Exception as e:
        logger.error(f"Erro ao criar serviço do Drive: {e}")
        raise

def find_folder(service, folder_name):
    """Encontra uma pasta no Drive pelo nome"""
    try:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        files = results.get('files', [])
        return files[0]['id'] if files else None
    except Exception as e:
        logger.error(f"Erro ao procurar pasta: {e}")
        return None

def move_files(service, old_folder_id, new_folder_id):
    """Move todos os arquivos de uma pasta para outra"""
    try:
        # Listar arquivos na pasta antiga
        query = f"'{old_folder_id}' in parents and trashed=false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        files = results.get('files', [])
        
        logger.info(f"Encontrados {len(files)} arquivos para mover")
        
        # Mover cada arquivo
        for file in files:
            try:
                # Atualizar pasta do arquivo
                service.files().update(
                    fileId=file['id'],
                    addParents=new_folder_id,
                    removeParents=old_folder_id,
                    fields='id, parents'
                ).execute()
                
                # Configurar permissões públicas
                service.permissions().create(
                    fileId=file['id'],
                    body={
                        'type': 'anyone',
                        'role': 'writer'
                    },
                    fields='id'
                ).execute()
                
                logger.info(f"Arquivo movido com sucesso: {file['name']}")
            except Exception as e:
                logger.error(f"Erro ao mover arquivo {file['name']}: {e}")
                
    except Exception as e:
        logger.error(f"Erro ao listar arquivos: {e}")

def create_shared_folder(service, folder_name):
    """Cria uma pasta compartilhada no Drive"""
    try:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        folder_id = folder.get('id')
        
        # Configurar permissões públicas
        service.permissions().create(
            fileId=folder_id,
            body={
                'type': 'anyone',
                'role': 'writer'
            },
            fields='id'
        ).execute()
        
        logger.info(f"Pasta '{folder_name}' criada com sucesso (ID: {folder_id})")
        return folder_id
        
    except Exception as e:
        logger.error(f"Erro ao criar pasta compartilhada: {e}")
        return None

def main():
    """Função principal"""
    try:
        service = get_drive_service()
        
        # Encontrar pasta antiga
        old_folder_id = find_folder(service, 'AILocalBKPs')
        if not old_folder_id:
            logger.warning("Pasta antiga 'AILocalBKPs' não encontrada")
            return
            
        # Encontrar ou criar pasta compartilhada
        shared_folder_name = 'Arquivos compartilhados'
        new_folder_id = find_folder(service, shared_folder_name)
        if not new_folder_id:
            logger.info(f"Pasta '{shared_folder_name}' não encontrada. Criando...")
            new_folder_id = create_shared_folder(service, shared_folder_name)
            if not new_folder_id:
                logger.error("Não foi possível criar a pasta compartilhada")
                return
            
        # Mover arquivos
        move_files(service, old_folder_id, new_folder_id)
        
        # Tentar deletar pasta antiga
        try:
            service.files().delete(fileId=old_folder_id).execute()
            logger.info("Pasta antiga removida com sucesso")
        except:
            logger.warning("Não foi possível remover a pasta antiga")
            
        logger.info("Processo concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante o processo: {e}")

if __name__ == '__main__':
    main() 