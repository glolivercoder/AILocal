import os
import shutil
import pyzipper
import random
import string
from datetime import datetime
from pathlib import Path
import json

# Importar lógicas do Google Drive se disponíveis
try:
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False

class ConfigManager:
    """
    Gerencia o backup, restauração e sincronização de arquivos de configuração sensíveis.
    """
    def __init__(self, config_dirs=None, backup_dir="config_backups"):
        """
        Inicializa o gerenciador de configurações.

        Args:
            config_dirs (list, optional): Lista de diretórios para fazer backup. Defaults to ["config", "rag_data"].
            backup_dir (str, optional): Diretório para armazenar os backups locais. Defaults to "config_backups".
        """
        if config_dirs is None:
            config_dirs = ["config", "rag_data"]
        
        self.config_dirs = [Path(d) for d in config_dirs]
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        self.history_file = self.backup_dir / "config_backup_history.json"
        self.history = self._load_history()
        
        self.gdrive = None
        if GDRIVE_AVAILABLE:
            self._init_gdrive()

    def _load_history(self):
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def _save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def _init_gdrive(self):
        """Inicializa a conexão com o Google Drive."""
        try:
            gauth = GoogleAuth()
            # Tenta carregar credenciais salvas
            gauth.LoadCredentialsFile("gdrive_creds.txt")
            if gauth.credentials is None:
                # Autentica via navegador se não houver credenciais
                gauth.LocalWebserverAuth()
            elif gauth.access_token_expired:
                # Atualiza o token se estiver expirado
                gauth.Refresh()
            else:
                # Autoriza com as credenciais existentes
                gauth.Authorize()
            # Salva as credenciais para futuros usos
            gauth.SaveCredentialsFile("gdrive_creds.txt")
            self.gdrive = GoogleDrive(gauth)
        except Exception as e:
            print(f"Erro ao inicializar Google Drive: {e}")
            self.gdrive = None

    def _generate_password(self, length=16):
        """Gera uma senha segura para o arquivo de backup."""
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

    def backup_configs(self, password=None):
        """
        Cria um backup criptografado dos diretórios de configuração.

        Args:
            password (str, optional): A senha para criptografar o backup. Se não for fornecida, uma será gerada.

        Returns:
            tuple: Caminho do arquivo de backup e a senha usada.
        """
        zip_name = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = self.backup_dir / zip_name
        
        if not password:
            password = self._generate_password()
            print(f"Senha gerada para o backup: {password}")

        files_to_backup = []
        for config_dir in self.config_dirs:
            if config_dir.exists() and config_dir.is_dir():
                for root, _, files in os.walk(config_dir):
                    for file in files:
                        files_to_backup.append(Path(root) / file)
        
        if not files_to_backup:
            raise FileNotFoundError("Nenhum arquivo de configuração encontrado para backup.")

        with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
            zf.setpassword(password.encode('utf-8'))
            for file_path in files_to_backup:
                arcname = file_path.relative_to(Path.cwd())
                zf.write(file_path, arcname=str(arcname))
        
        print(f"Backup criado com sucesso em: {zip_path}")
        return zip_path, password

    def upload_to_gdrive(self, file_path):
        """
        Faz o upload de um arquivo para o Google Drive.

        Args:
            file_path (Path): O caminho do arquivo a ser enviado.

        Returns:
            dict: Dicionário com informações do arquivo no Google Drive.
        """
        if not self.gdrive:
            raise ConnectionError("Google Drive não está inicializado ou configurado.")
        
        file_drive = self.gdrive.CreateFile({
            'title': file_path.name,
            'parents': [{'id': 'root'}] # Pode ser alterado para uma pasta específica
        })
        file_drive.SetContentFile(str(file_path))
        file_drive.Upload()
        
        print(f"Arquivo '{file_path.name}' enviado para o Google Drive com ID: {file_drive['id']}")
        return {'id': file_drive['id'], 'name': file_drive['title'], 'url': file_drive['alternateLink']}

    def run_backup_flow(self, password=None, upload=True):
        """
        Executa o fluxo completo de backup: compacta, criptografa e faz o upload.

        Args:
            password (str, optional): Senha para o backup. Se None, uma será gerada.
            upload (bool, optional): Se True, faz o upload para o Google Drive. Defaults to True.

        Returns:
            dict: Um registro do evento de backup.
        """
        try:
            zip_path, used_password = self.backup_configs(password)
            
            upload_info = None
            if upload and self.gdrive:
                upload_info = self.upload_to_gdrive(zip_path)

            entry = {
                "date": datetime.now().isoformat(),
                "local_path": str(zip_path),
                "password": used_password,
                "gdrive_info": upload_info,
                "status": "Success"
            }
            
        except Exception as e:
            print(f"Ocorreu um erro durante o fluxo de backup: {e}")
            entry = {
                "date": datetime.now().isoformat(),
                "error": str(e),
                "status": "Failed"
            }

        self.history.append(entry)
        self._save_history()
        return entry

    def list_backups(self):
        """Retorna o histórico de backups."""
        return self.history

# Exemplo de uso
if __name__ == '__main__':
    print("Executando o Gerenciador de Configurações como um script.")
    
    # Criar diretórios e arquivos de exemplo para o teste
    Path("config").mkdir(exist_ok=True)
    with open("config/api_keys.json", "w") as f:
        f.write('{"openai_api_key": "sk-example-key"}')
    Path("rag_data").mkdir(exist_ok=True)
    with open("rag_data/vector_db.faiss", "w") as f:
        f.write('dummy faiss data')
        
    manager = ConfigManager()
    
    # Executa o fluxo de backup com uma senha fornecida e faz o upload
    # Na primeira vez, isso abrirá o navegador para autenticação do Google Drive.
    print("\n--- Iniciando fluxo de backup com upload ---")
    # IMPORTANTE: A senha será impressa no console. Em uma aplicação real,
    # ela deve ser manuseada de forma segura (ex: exibida na UI, copiada para a área de transferência).
    backup_result = manager.run_backup_flow()
    print(f"Resultado do fluxo de backup: {json.dumps(backup_result, indent=2)}")

    print("\n--- Histórico de Backups ---")
    print(json.dumps(manager.list_backups(), indent=2)) 