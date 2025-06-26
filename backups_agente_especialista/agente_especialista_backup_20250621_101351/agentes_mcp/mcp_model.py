import os
import json
import platform
import subprocess
from datetime import datetime

class MCP:
    """Classe que representa um Model Control Protocol (MCP)"""
    
    def __init__(self, id, name, source, type, status=False, endpoint=None, process=None):
        self.id = id
        self.name = name
        self.source = source
        self.type = type
        self.status = status
        self.endpoint = endpoint
        self.process = process
        self.last_activity = datetime.now().isoformat()
    
    def to_dict(self):
        """Converte o MCP para um dicionário"""
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "type": self.type,
            "status": self.status,
            "endpoint": self.endpoint,
            "last_activity": self.last_activity
        }
    
    @classmethod
    def from_dict(cls, data):
        """Cria um MCP a partir de um dicionário"""
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            source=data.get("source"),
            type=data.get("type"),
            status=data.get("status", False),
            endpoint=data.get("endpoint")
        )
    
    def start(self):
        """Inicia o MCP (implementação específica dependeria do tipo de MCP)"""
        # Implementação genérica - seria sobrescrita por subclasses específicas
        self.status = True
        self.last_activity = datetime.now().isoformat()
        return f"MCP {self.name} iniciado."
    
    def stop(self):
        """Para o MCP (implementação específica dependeria do tipo de MCP)"""
        # Implementação genérica - seria sobrescrita por subclasses específicas
        if self.process:
            try:
                self.process.terminate()
                self.process = None
            except Exception as e:
                return f"Erro ao parar MCP {self.name}: {str(e)}"
        
        self.status = False
        self.last_activity = datetime.now().isoformat()
        return f"MCP {self.name} parado."


class BrowserAgentMCP(MCP):
    """Classe específica para o MCP Browser Agent"""
    
    def __init__(self, id="browser-agent", name="Browser Agent", source="AgentDesk AI", 
                 type="Browser", status=False, port=3333):
        super().__init__(id, name, source, type, status)
        self.port = port
        self.logs = []
        self.status_callback = None
    
    def start(self):
        """Inicia o MCP Browser Agent via NPX"""
        if self.status:
            return "Browser Agent MCP já está em execução"
        
        try:
            # Construir o comando para iniciar o browser-tools-server
            command = f"npx @agentdeskai/browser-tools-server@latest --port {self.port}"
            
            # Iniciar o processo em modo não-bloqueante
            self.process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Iniciar thread para capturar a saída do processo
            def monitor_process():
                import threading
                
                while self.process and self.process.poll() is None:
                    # Ler saída
                    stdout_line = self.process.stdout.readline()
                    if stdout_line:
                        self.logs.append({"type": "stdout", "message": stdout_line.strip()})
                        print(f"Browser MCP: {stdout_line.strip()}")
                        
                        # Verificar se a mensagem indica que o servidor está pronto
                        if "Server started" in stdout_line:
                            self.status = True
                            self.last_activity = datetime.now().isoformat()
                            if self.status_callback:
                                self.status_callback(True)
                    
                    # Ler erros
                    stderr_line = self.process.stderr.readline()
                    if stderr_line:
                        self.logs.append({"type": "stderr", "message": stderr_line.strip()})
                        print(f"Browser MCP Error: {stderr_line.strip()}")
                
                # O processo terminou
                self.status = False
                if self.status_callback:
                    self.status_callback(False)
            
            # Iniciar thread para monitorar o processo
            import threading
            threading.Thread(target=monitor_process, daemon=True).start()
            
            return "Iniciando Browser Agent MCP..."
        
        except Exception as e:
            return f"Erro ao iniciar Browser Agent MCP: {str(e)}"
    
    def stop(self):
        """Para o MCP Browser Agent"""
        if not self.status or not self.process:
            return "Browser Agent MCP não está em execução"
        
        try:
            # Encerrar o processo
            self.process.terminate()
            
            # Aguardar o processo encerrar (com timeout)
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Forçar encerramento se não terminar normalmente
                self.process.kill()
            
            self.status = False
            self.process = None
            self.last_activity = datetime.now().isoformat()
            
            if self.status_callback:
                self.status_callback(False)
            
            return "Browser Agent MCP encerrado com sucesso"
        
        except Exception as e:
            return f"Erro ao encerrar Browser Agent MCP: {str(e)}"
    
    def take_screenshot(self, url=None):
        """Captura screenshot da página atual (ou da URL especificada)"""
        if not self.status:
            return "Browser Agent MCP não está em execução. Inicie-o primeiro."
        
        try:
            # Em uma implementação real, você enviaria um comando para o MCP Browser
            # através da sua API para capturar a screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshot_{timestamp}.png"
            
            # Para uma implementação real, você usaria uma biblioteca como requests
            # para chamar a API do browser-tools-server
            # Exemplo:
            # import requests
            # response = requests.post(f"http://localhost:{self.port}/screenshot", 
            #                         json={"url": url} if url else {})
            
            return f"Screenshot capturada: {screenshot_path}"
        
        except Exception as e:
            return f"Erro ao capturar screenshot: {str(e)}"
    
    def execute_console_command(self, command, url=None):
        """Executa um comando no console do navegador"""
        if not self.status:
            return "Browser Agent MCP não está em execução. Inicie-o primeiro."
        
        try:
            # Em uma implementação real, você enviaria um comando para o MCP Browser
            # através da sua API para executar no console
            
            # Para uma implementação real, você usaria uma biblioteca como requests
            # para chamar a API do browser-tools-server
            # Exemplo:
            # import requests
            # response = requests.post(f"http://localhost:{self.port}/console", 
            #                         json={"command": command, "url": url} if url else {"command": command})
            
            return f"Comando executado no console do navegador: {command}"
        
        except Exception as e:
            return f"Erro ao executar comando no console: {str(e)}"
    
    def navigate_to(self, url):
        """Navega para uma URL específica"""
        if not self.status:
            return "Browser Agent MCP não está em execução. Inicie-o primeiro."
        
        try:
            # Em uma implementação real, você enviaria um comando para o MCP Browser
            # através da sua API para navegar para a URL
            
            # Para uma implementação real, você usaria uma biblioteca como requests
            # para chamar a API do browser-tools-server
            # Exemplo:
            # import requests
            # response = requests.post(f"http://localhost:{self.port}/navigate", 
            #                         json={"url": url})
            
            return f"Navegando para: {url}"
        
        except Exception as e:
            return f"Erro ao navegar para URL: {str(e)}"
    
    def register_status_callback(self, callback):
        """Registra um callback para receber atualizações de status"""
        self.status_callback = callback
    
    def to_dict(self):
        """Sobrescreve o método to_dict para incluir propriedades específicas"""
        data = super().to_dict()
        data.update({
            "port": self.port
        })
        return data


class MCPManager:
    """Classe para gerenciar um conjunto de MCPs"""
    
    def __init__(self):
        self.mcps = {}
        self.cursor_path = self._find_cursor_path()
        self.mcp_json_path = self._find_mcp_json()
    
    def _find_cursor_path(self):
        """Tenta encontrar o caminho de instalação do Cursor"""
        if platform.system() == "Windows":
            # Verificar AppData
            appdata_path = os.path.expanduser("~/AppData/Roaming/Cursor")
            if os.path.exists(appdata_path):
                return appdata_path
                
            # Verificar Program Files
            program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            cursor_path = os.path.join(program_files, "Cursor")
            if os.path.exists(cursor_path):
                return cursor_path
        
        elif platform.system() == "Darwin":  # macOS
            cursor_path = os.path.expanduser("~/Library/Application Support/Cursor")
            if os.path.exists(cursor_path):
                return cursor_path
        
        elif platform.system() == "Linux":
            cursor_path = os.path.expanduser("~/.config/Cursor")
            if os.path.exists(cursor_path):
                return cursor_path
        
        return None
    
    def _find_mcp_json(self):
        """Tenta encontrar o arquivo mcp.json do Cursor"""
        cursor_path = self.cursor_path
        
        if cursor_path:
            mcp_json = os.path.join(cursor_path, "mcp.json")
            if os.path.exists(mcp_json):
                return mcp_json
        
        return None
    
    def add_mcp(self, mcp):
        """Adiciona um MCP ao gerenciador"""
        self.mcps[mcp.id] = mcp
    
    def remove_mcp(self, mcp_id):
        """Remove um MCP do gerenciador"""
        if mcp_id in self.mcps:
            mcp = self.mcps[mcp_id]
            
            # Se o MCP estiver ativo, para-lo primeiro
            if mcp.status:
                mcp.stop()
            
            del self.mcps[mcp_id]
            return True
        
        return False
    
    def get_mcp(self, mcp_id):
        """Obtém um MCP pelo ID"""
        return self.mcps.get(mcp_id)
    
    def get_mcps(self, filter_func=None):
        """Obtém todos os MCPs, opcionalmente filtrados"""
        if filter_func:
            return {k: v for k, v in self.mcps.items() if filter_func(v)}
        return self.mcps
    
    def get_active_mcps(self):
        """Obtém todos os MCPs ativos"""
        return self.get_mcps(lambda mcp: mcp.status)
    
    def load_from_cursor(self):
        """Carrega MCPs a partir do arquivo mcp.json do Cursor"""
        if not self.mcp_json_path:
            return False
        
        try:
            with open(self.mcp_json_path, 'r') as f:
                data = json.load(f)
            
            if "mcps" in data:
                for mcp_data in data["mcps"]:
                    # Determinar o tipo de MCP para criar a instância correta
                    if mcp_data.get("type") == "browser" or mcp_data.get("id") == "browser-agent":
                        mcp = BrowserAgentMCP(
                            id=mcp_data.get("id"),
                            name=mcp_data.get("name"),
                            source=mcp_data.get("origin", "Cursor Directory"),
                            status=mcp_data.get("enabled", False)
                        )
                    else:
                        mcp = MCP.from_dict({
                            "id": mcp_data.get("id"),
                            "name": mcp_data.get("name"),
                            "source": mcp_data.get("origin", "Cursor Directory"),
                            "type": mcp_data.get("type", "Unknown"),
                            "status": mcp_data.get("enabled", False),
                            "endpoint": mcp_data.get("endpoint")
                        })
                    
                    self.add_mcp(mcp)
            
            return True
        
        except Exception as e:
            print(f"Erro ao carregar MCPs do Cursor: {str(e)}")
            return False
    
    def save_to_cursor(self):
        """Salva MCPs para o arquivo mcp.json do Cursor"""
        if not self.mcp_json_path:
            return False
        
        try:
            # Ler o arquivo existente primeiro para preservar outras configurações
            with open(self.mcp_json_path, 'r') as f:
                data = json.load(f)
            
            # Atualizar a lista de MCPs
            mcp_list = []
            for mcp in self.mcps.values():
                # Converter para o formato esperado pelo Cursor
                mcp_data = {
                    "id": mcp.id,
                    "name": mcp.name,
                    "origin": mcp.source,
                    "type": mcp.type,
                    "enabled": mcp.status
                }
                
                if mcp.endpoint:
                    mcp_data["endpoint"] = mcp.endpoint
                
                # Adicionar atributos específicos dependendo do tipo
                if isinstance(mcp, BrowserAgentMCP):
                    mcp_data["port"] = mcp.port
                
                mcp_list.append(mcp_data)
            
            data["mcps"] = mcp_list
            
            # Salvar de volta ao arquivo
            with open(self.mcp_json_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Erro ao salvar MCPs para o Cursor: {str(e)}")
            return False
    
    def export_to_file(self, filepath):
        """Exporta MCPs para um arquivo JSON"""
        try:
            data = {
                "mcps": [mcp.to_dict() for mcp in self.mcps.values()],
                "exported_at": datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Erro ao exportar MCPs: {str(e)}")
            return False
    
    def import_from_file(self, filepath):
        """Importa MCPs de um arquivo JSON"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if "mcps" in data:
                for mcp_data in data["mcps"]:
                    # Determinar o tipo de MCP para criar a instância correta
                    if mcp_data.get("type") == "Browser" or mcp_data.get("id") == "browser-agent":
                        mcp = BrowserAgentMCP(
                            id=mcp_data.get("id"),
                            name=mcp_data.get("name"),
                            source=mcp_data.get("source"),
                            status=mcp_data.get("status", False)
                        )
                        if "port" in mcp_data:
                            mcp.port = mcp_data["port"]
                    else:
                        mcp = MCP.from_dict(mcp_data)
                    
                    self.add_mcp(mcp)
            
            return True
        
        except Exception as e:
            print(f"Erro ao importar MCPs: {str(e)}")
            return False


# Criar alguns MCPs para teste
def create_sample_mcps():
    """Cria MCPs de exemplo para teste"""
    manager = MCPManager()
    
    # Adicionar MCPs de exemplo
    manager.add_mcp(MCP(
        id="1",
        name="Claude 3 Opus",
        source="HiMCP.ai",
        type="LLM",
        status=True
    ))
    
    manager.add_mcp(MCP(
        id="2",
        name="Code Interpreter",
        source="Cursor Directory",
        type="Code",
        status=False
    ))
    
    manager.add_mcp(MCP(
        id="3",
        name="Image Analyzer",
        source="MCP.so",
        type="Vision",
        status=True
    ))
    
    manager.add_mcp(MCP(
        id="4",
        name="Data Visualizer",
        source="Smithery",
        type="Data",
        status=False
    ))
    
    manager.add_mcp(MCP(
        id="5",
        name="Web Scraper",
        source="PulseMCP",
        type="Tool",
        status=True
    ))
    
    manager.add_mcp(BrowserAgentMCP())
    
    return manager


if __name__ == "__main__":
    # Testar funcionalidades
    manager = create_sample_mcps()
    
    print("MCPs criados:")
    for mcp_id, mcp in manager.get_mcps().items():
        print(f"- {mcp.name} ({mcp.id}): {'Ativo' if mcp.status else 'Inativo'}")
    
    # Exportar para arquivo
    manager.export_to_file("mcps_test.json")
    print("\nMCPs exportados para mcps_test.json")
    
    # Testes de importação/exportação para Cursor
    if manager.mcp_json_path:
        print(f"\nArquivo mcp.json do Cursor encontrado em: {manager.mcp_json_path}")
        
        # Carregar do Cursor
        if manager.load_from_cursor():
            print("MCPs carregados do Cursor com sucesso.")
            
            # Exibir MCPs carregados
            print("\nMCPs do Cursor:")
            for mcp_id, mcp in manager.get_mcps().items():
                print(f"- {mcp.name} ({mcp.id}): {'Ativo' if mcp.status else 'Inativo'}")
    else:
        print("\nArquivo mcp.json do Cursor não encontrado.") 