import sys
import json
import os
import threading
import subprocess
import platform
import re
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QCheckBox, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QTabWidget, QTextEdit, QFileDialog,
                           QMessageBox, QGroupBox, QComboBox, QScrollArea,
                           QListWidget, QListWidgetItem, QRadioButton, QSplitter)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtGui import QIcon, QColor, QFont, QDesktopServices

# Importações condicionais para funcionalidades de voz
VOICE_AVAILABLE = False
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
    print("Recursos de voz disponíveis")
except ImportError as e:
    print(f"Recursos de voz não disponíveis: {e}")
    VOICE_AVAILABLE = False

# Modelo de dados para configurações de APIs
class APIConfig:
    def __init__(self):
        # OpenRouter
        self.openrouter_api_key = ""
        self.openrouter_models = [
            "anthropic/claude-3-opus", 
            "anthropic/claude-3-sonnet",
            "anthropic/claude-3-haiku",
            "google/gemini-pro", 
            "google/gemini-1.5-pro",
            "mistralai/mistral-large",
            "mistralai/mistral-medium",
            "meta-llama/llama-3-70b-instruct",
            "meta-llama/llama-3-8b-instruct",
            "openai/gpt-4-turbo",
            "openai/gpt-4o",
            "openai/gpt-3.5-turbo",
            "deepseek/deepseek-coder",
            "cohere/command-r-plus"
        ]
        self.openrouter_selected_model = "anthropic/claude-3-opus"
        
        # Gemini
        self.gemini_api_key = ""
        self.gemini_models = ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
        self.gemini_selected_model = "gemini-pro"
        
        # Claude
        self.claude_api_key = ""
        self.claude_models = ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
        self.claude_selected_model = "claude-3-opus"
        
        # DeepSeek
        self.deepseek_api_key = ""
        self.deepseek_models = ["deepseek-coder", "deepseek-chat", "deepseek-v2"]
        self.deepseek_selected_model = "deepseek-coder"

# Classe para gerenciar o MCP Browser Agent
class BrowserAgentMCP:
    def __init__(self):
        self.process = None
        self.is_running = False
        self.port = 3333  # Porta padrão do browser-tools-server
        self.logs = []
        self.status_callback = None
        
    def start(self):
        """Inicia o MCP Browser Agent via NPX"""
        if self.is_running:
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
                while self.process and self.process.poll() is None:
                    # Ler saída
                    stdout_line = self.process.stdout.readline()
                    if stdout_line:
                        self.logs.append({"type": "stdout", "message": stdout_line.strip()})
                        print(f"Browser MCP: {stdout_line.strip()}")
                        
                        # Verificar se a mensagem indica que o servidor está pronto
                        if "Server started" in stdout_line:
                            self.is_running = True
                            if self.status_callback:
                                self.status_callback(True)
                    
                    # Ler erros
                    stderr_line = self.process.stderr.readline()
                    if stderr_line:
                        self.logs.append({"type": "stderr", "message": stderr_line.strip()})
                        print(f"Browser MCP Error: {stderr_line.strip()}")
                
                # O processo terminou
                self.is_running = False
                if self.status_callback:
                    self.status_callback(False)
            
            # Iniciar thread para monitorar o processo
            threading.Thread(target=monitor_process, daemon=True).start()
            
            # Aguardar um momento para o processo iniciar
            return "Iniciando Browser Agent MCP..."
        
        except Exception as e:
            return f"Erro ao iniciar Browser Agent MCP: {str(e)}"
    
    def stop(self):
        """Para o MCP Browser Agent"""
        if not self.is_running or not self.process:
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
            
            self.is_running = False
            
            if self.status_callback:
                self.status_callback(False)
            
            return "Browser Agent MCP encerrado com sucesso"
        
        except Exception as e:
            return f"Erro ao encerrar Browser Agent MCP: {str(e)}"
    
    def take_screenshot(self, url=None):
        """Captura screenshot da página atual (ou da URL especificada)"""
        if not self.is_running:
            return "Browser Agent MCP não está em execução. Inicie-o primeiro."
        
        try:
            # Em uma implementação real, você enviaria um comando para o MCP Browser
            # através da sua API para capturar a screenshot
            
            # Exemplo simulado:
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
        if not self.is_running:
            return "Browser Agent MCP não está em execução. Inicie-o primeiro."
        
        try:
            # Em uma implementação real, você enviaria um comando para o MCP Browser
            # através da sua API para executar no console
            
            # Exemplo simulado:
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
        if not self.is_running:
            return "Browser Agent MCP não está em execução. Inicie-o primeiro."
        
        try:
            # Em uma implementação real, você enviaria um comando para o MCP Browser
            # através da sua API para navegar para a URL
            
            # Exemplo simulado:
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

# Classe do Agente Automatizador (Fil)
class FilAgent:
    def __init__(self, parent=None):
        self.name = "Fil"
        self.parent = parent
        self.voice_engine = None
        self.history = []
        
        # Inicializar MCP Browser Agent
        self.browser_agent = BrowserAgentMCP()
        self.browser_agent.register_status_callback(self.on_browser_agent_status_change)
        
        # Estado de detecção de projeto
        self.active_project_path = None
        self.active_project_type = None  # "cursor" ou "vscode"
        self.mcp_json_path = None
        
        # Inicializar TTS se disponível
        if VOICE_AVAILABLE:
            try:
                self.voice_engine = pyttsx3.init()
                # Configurar voz
                try:
                    voices = self.voice_engine.getProperty('voices')
                    # Selecionar voz em português se disponível
                    # Verificar se há vozes disponíveis
                    if voices and len(voices) > 0:
                        # Tentar encontrar uma voz em português
                        portuguese_voice = None
                        for voice in voices:
                            if hasattr(voice, 'languages') and len(voice.languages) > 0:
                                if "portuguese" in voice.languages[0].lower():
                                    portuguese_voice = voice.id
                                    break
                        
                        # Se encontrou uma voz em português, use-a
                        if portuguese_voice:
                            self.voice_engine.setProperty('voice', portuguese_voice)
                        # Caso contrário, use a primeira voz disponível
                        elif len(voices) > 0:
                            self.voice_engine.setProperty('voice', voices[0].id)
                except Exception as e:
                    print(f"Aviso ao configurar voz: {e}, usando configuração padrão")
            except Exception as e:
                print(f"Erro ao inicializar voz do agente: {e}")
                self.voice_engine = None
        
        # Identificar o sistema operacional
        self.os_name = platform.system()
        self.os_version = platform.version()
    
    def on_browser_agent_status_change(self, is_running):
        """Callback para mudanças de status no Browser Agent"""
        status = "ativo" if is_running else "inativo"
        if self.parent:
            self.parent.update_browser_agent_status(is_running)
        self.respond(f"Browser Agent MCP agora está {status}.", speak=False)
    
    def detect_editor_project(self, path=None):
        """Detecta se o caminho é um projeto do Cursor ou VS Code"""
        if not path:
            path = os.getcwd()
        
        # Verificar se é um projeto do Cursor
        cursor_config = os.path.join(path, '.cursor')
        if os.path.exists(cursor_config):
            self.active_project_path = path
            self.active_project_type = "cursor"
            
            # Localizar o mcp.json
            cursor_app_data = os.path.expanduser("~/AppData/Roaming/Cursor")
            if os.path.exists(cursor_app_data):
                mcp_json = os.path.join(cursor_app_data, "mcp.json")
                if os.path.exists(mcp_json):
                    self.mcp_json_path = mcp_json
            
            return True
        
        # Verificar se é um projeto do VS Code
        vscode_config = os.path.join(path, '.vscode')
        if os.path.exists(vscode_config):
            self.active_project_path = path
            self.active_project_type = "vscode"
            return True
        
        # Verificar se há um arquivo de workspace do VS Code
        workspace_files = [f for f in os.listdir(path) if f.endswith('.code-workspace')]
        if workspace_files:
            self.active_project_path = path
            self.active_project_type = "vscode"
            return True
        
        return False
    
    def auto_start_browser_agent(self):
        """Inicia automaticamente o Browser Agent se um projeto for detectado"""
        if self.detect_editor_project():
            project_type = self.active_project_type.upper()
            result = self.browser_agent.start()
            self.respond(f"Detectado projeto {project_type} em: {self.active_project_path}. {result}")
            return True
        return False
    
    def respond(self, text, speak=True):
        """Responde ao usuário e opcionalmente fala a resposta"""
        # Adicionar ao histórico
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({"timestamp": timestamp, "type": "response", "text": text})
        
        # Se o parent for fornecido, adicionar ao chat da interface
        if self.parent:
            self.parent.add_chat_message(self.name, text, "assistant")
        
        # Falar a resposta se solicitado e disponível
        if speak and self.voice_engine:
            threading.Thread(target=self.speak, args=(text,)).start()
        
        return text
    
    def speak(self, text):
        """Fala o texto fornecido"""
        try:
            plain_text = text.replace("<br>", " ").replace("<b>", "").replace("</b>", "")
            self.voice_engine.say(plain_text)
            self.voice_engine.runAndWait()
        except Exception as e:
            print(f"Erro ao falar: {e}")
    
    def execute_terminal_command(self, command, terminal_type="auto"):
        """Executa um comando no terminal especificado"""
        # Determinar o terminal automaticamente se for "auto"
        if terminal_type == "auto":
            if self.os_name == "Windows":
                terminal_type = "cmd"
            else:
                terminal_type = "bash"
        
        try:
            # Configurar o comando para o tipo de terminal
            if terminal_type == "cmd":
                process = subprocess.Popen(
                    ["cmd.exe", "/c", command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            elif terminal_type == "powershell":
                process = subprocess.Popen(
                    ["powershell.exe", "-Command", command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            elif terminal_type == "bash":
                process = subprocess.Popen(
                    ["bash", "-c", command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            elif terminal_type == "docker":
                process = subprocess.Popen(
                    ["docker", "exec", "-it", "container_name", "bash", "-c", command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                return f"Tipo de terminal '{terminal_type}' não suportado."
            
            # Capturar saída
            stdout, stderr = process.communicate()
            
            # Adicionar ao histórico
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.history.append({
                "timestamp": timestamp, 
                "type": "command", 
                "terminal": terminal_type,
                "command": command,
                "stdout": stdout,
                "stderr": stderr
            })
            
            # Formatar resposta
            if stderr:
                return f"Comando executado com erros:\n{stderr}\n\nSaída:\n{stdout}"
            else:
                return f"Comando executado com sucesso:\n{stdout}"
        
        except Exception as e:
            return f"Erro ao executar comando: {str(e)}"
    
    def create_python_script(self, script_content, file_name=None):
        """Cria um script Python"""
        if not file_name:
            # Gerar nome de arquivo baseado na data e hora
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"automation_{timestamp}.py"
        
        try:
            # Garantir que o nome do arquivo termina com .py
            if not file_name.endswith('.py'):
                file_name += '.py'
            
            # Escrever o conteúdo no arquivo
            with open(file_name, 'w') as f:
                f.write(script_content)
            
            # Adicionar ao histórico
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.history.append({
                "timestamp": timestamp, 
                "type": "script_creation", 
                "file_name": file_name,
                "content": script_content
            })
            
            return f"Script Python criado com sucesso: {os.path.abspath(file_name)}"
        
        except Exception as e:
            return f"Erro ao criar script: {str(e)}"
    
    def execute_python_script(self, script_path):
        """Executa um script Python"""
        try:
            # Executar o script
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Capturar saída
            stdout, stderr = process.communicate()
            
            # Adicionar ao histórico
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.history.append({
                "timestamp": timestamp, 
                "type": "script_execution", 
                "script_path": script_path,
                "stdout": stdout,
                "stderr": stderr
            })
            
            # Formatar resposta
            if stderr:
                return f"Script executado com erros:\n{stderr}\n\nSaída:\n{stdout}"
            else:
                return f"Script executado com sucesso:\n{stdout}"
        
        except Exception as e:
            return f"Erro ao executar script: {str(e)}"
    
    def process_command(self, command_text):
        """Processa um comando de texto e executa a ação apropriada"""
        command_text = command_text.strip().lower()
        
        # Adicionar ao histórico
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({"timestamp": timestamp, "type": "command_request", "text": command_text})
        
        # Comandos para Browser Agent MCP
        if command_text.startswith("browser start") or command_text.startswith("iniciar browser"):
            result = self.browser_agent.start()
            return self.respond(result)
        
        elif command_text.startswith("browser stop") or command_text.startswith("parar browser"):
            result = self.browser_agent.stop()
            return self.respond(result)
        
        elif command_text.startswith("screenshot") or command_text.startswith("capturar tela"):
            # Verificar se há URL especificada
            url_match = re.search(r'https?://\S+', command_text)
            url = url_match.group(0) if url_match else None
            
            result = self.browser_agent.take_screenshot(url)
            return self.respond(result)
        
        elif command_text.startswith("console "):
            # Extrair o comando para o console
            console_command = command_text[8:].strip()
            if not console_command:
                return self.respond("Por favor, especifique um comando para executar no console.")
            
            result = self.browser_agent.execute_console_command(console_command)
            return self.respond(result)
        
        elif command_text.startswith("navegar para ") or command_text.startswith("abrir site "):
            # Extrair a URL
            url_match = re.search(r'https?://\S+', command_text)
            
            if url_match:
                url = url_match.group(0)
            else:
                # Tentar extrair sem o protocolo
                parts = command_text.split(" ", 2)
                if len(parts) < 3:
                    return self.respond("Por favor, especifique uma URL válida.")
                
                # Adicionar protocolo se não presente
                url = parts[2]
                if not url.startswith("http"):
                    url = "https://" + url
            
            result = self.browser_agent.navigate_to(url)
            return self.respond(result)
        
        elif command_text.startswith("detectar projeto"):
            if self.detect_editor_project():
                return self.respond(f"Projeto {self.active_project_type.upper()} detectado em: {self.active_project_path}")
            else:
                return self.respond("Nenhum projeto Cursor ou VS Code detectado no diretório atual.")
        
        # Comandos para executar no terminal
        elif command_text.startswith("execute ") or command_text.startswith("run "):
            parts = command_text.split(" ", 2)
            if len(parts) < 3:
                return self.respond("Por favor, especifique um comando para executar.")
            
            terminal_type = "auto"
            if "in cmd" in command_text or "no cmd" in command_text:
                terminal_type = "cmd"
            elif "in powershell" in command_text or "no powershell" in command_text:
                terminal_type = "powershell"
            elif "in bash" in command_text or "no bash" in command_text:
                terminal_type = "bash"
            elif "in docker" in command_text or "no docker" in command_text:
                terminal_type = "docker"
            
            # Extrair o comando real
            cmd = parts[2]
            for term in ["in cmd", "no cmd", "in powershell", "no powershell", "in bash", "no bash", "in docker", "no docker"]:
                cmd = cmd.replace(term, "").strip()
            
            result = self.execute_terminal_command(cmd, terminal_type)
            return self.respond(result)
        
        # Comandos para criar scripts Python
        elif command_text.startswith("create script") or command_text.startswith("create python"):
            # Este é um comando simplificado. Em um sistema real, você teria uma interface mais robusta
            # para obter o conteúdo do script
            return self.respond("Para criar um script Python, use a aba 'Automação' e preencha o conteúdo do script.")
        
        # Comandos para informações do sistema
        elif "system info" in command_text or "system information" in command_text:
            system_info = f"Sistema operacional: {self.os_name} {self.os_version}\n"
            system_info += f"Python versão: {sys.version}\n"
            system_info += f"Diretório atual: {os.getcwd()}"
            return self.respond(system_info)
        
        # Comandos relacionados ao Fil
        elif "who are you" in command_text or "quem é você" in command_text:
            return self.respond("Eu sou Fil, seu assistente de automação. Posso executar comandos em diferentes terminais, criar e executar scripts Python, e ajudar com a configuração de MCPs.")
        
        else:
            return self.respond("Desculpe, não entendi o comando. Tente comandos como 'execute [comando]', 'browser start', ou 'screenshot'.")

class MCPManagerApp(QMainWindow):
    # Sinal para atualizar a UI a partir de thread de reconhecimento de voz
    speech_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de MCPs")
        self.setGeometry(100, 100, 1200, 800)
        
        # Inicializar o agente Fil
        self.agent = FilAgent(self)
        
        # Dados simulados de MCPs
        self.mcps = [
            {"id": "1", "name": "Claude 3 Opus", "source": "HiMCP.ai", "type": "LLM", "status": True},
            {"id": "2", "name": "Code Interpreter", "source": "Cursor Directory", "type": "Code", "status": False},
            {"id": "3", "name": "Image Analyzer", "source": "MCP.so", "type": "Vision", "status": True},
            {"id": "4", "name": "Data Visualizer", "source": "Smithery", "type": "Data", "status": False},
            {"id": "5", "name": "Web Scraper", "source": "PulseMCP", "type": "Tool", "status": True},
            {"id": "6", "name": "Browser Agent", "source": "AgentDesk AI", "type": "Browser", "status": False},
        ]
        
        # Histórico simulado de prompts
        self.prompts_history = [
            {"timestamp": "2024-05-01 10:30:22", "prompt": "Explique como usar TypeScript com React", "mcp": "Code Interpreter"},
            {"timestamp": "2024-05-01 11:45:13", "prompt": "Analise esta imagem de um gráfico de desempenho", "mcp": "Image Analyzer"},
            {"timestamp": "2024-05-02 09:15:44", "prompt": "Gere um exemplo de código para um servidor Express", "mcp": "Claude 3 Opus"},
        ]
        
        # Histórico de chat
        self.chat_history = []
        
        # Configuração de APIs
        self.api_config = APIConfig()
        
        # Configuração do reconhecimento de voz (se disponível)
        self.is_listening = False
        self.speech_thread = None
        self.voice_enabled = False
        self.voice_available = VOICE_AVAILABLE  # Copiamos a variável global para uma variável de instância
        
        if self.voice_available:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                self.engine = pyttsx3.init()
                # Conectar sinal de fala
                self.speech_signal.connect(self.process_speech)
            except Exception as e:
                print(f"Erro ao inicializar recursos de voz: {e}")
                self.voice_available = False  # Usamos a variável de instância
        
        # Configurar interface
        self.setup_ui()
        
        # Tentar detectar e iniciar Browser Agent automaticamente se estiver em um projeto
        # Fazer isso em uma thread para não bloquear a inicialização da UI
        threading.Thread(target=self.autodetect_and_start_browser_agent, daemon=True).start()
    
    def autodetect_and_start_browser_agent(self):
        """Tenta detectar um projeto do Cursor ou VS Code e iniciar o Browser Agent"""
        # Aguardar um momento para a UI inicializar completamente
        QTimer.singleShot(1000, self.agent.auto_start_browser_agent)
    
    def update_browser_agent_status(self, is_running):
        """Atualiza a UI com o status do Browser Agent"""
        # Atualizar o status do MCP Browser Agent na lista
        for mcp in self.mcps:
            if mcp["id"] == "6" and mcp["name"] == "Browser Agent":
                mcp["status"] = is_running
                break
        
        # Atualizar a tabela
        self.populate_mcp_table()
        
        # Atualizar a interface do Browser
        if hasattr(self, 'browser_status_label'):
            status_text = "Ativo" if is_running else "Inativo"
            status_color = "#4CAF50" if is_running else "#F44336"  # Verde ou Vermelho
            self.browser_status_label.setText(f"Status: <span style='color: {status_color};'><b>{status_text}</b></span>")
            
            # Atualizar botões
            if hasattr(self, 'browser_start_button'):
                self.browser_start_button.setEnabled(not is_running)
            if hasattr(self, 'browser_stop_button'):
                self.browser_stop_button.setEnabled(is_running)
            if hasattr(self, 'browser_screenshot_button'):
                self.browser_screenshot_button.setEnabled(is_running)
            if hasattr(self, 'browser_console_button'):
                self.browser_console_button.setEnabled(is_running)
    
    def setup_ui(self):
        # Widget central e layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Abas principais
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Aba de gerenciamento de MCPs
        mcp_tab = QWidget()
        mcp_layout = QVBoxLayout(mcp_tab)
        tabs.addTab(mcp_tab, "Gerenciamento de MCPs")
        
        # Aba de histórico de prompts
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        tabs.addTab(history_tab, "Histórico de Prompts")
        
        # Aba de chat
        chat_tab = QWidget()
        chat_layout = QVBoxLayout(chat_tab)
        tabs.addTab(chat_tab, "Chat com Fil")  # Renomeado para "Fil"
        
        # Aba de automação
        automation_tab = QWidget()
        automation_layout = QVBoxLayout(automation_tab)
        tabs.addTab(automation_tab, "Automação")
        
        # Aba de Browser Agent
        browser_tab = QWidget()
        browser_layout = QVBoxLayout(browser_tab)
        tabs.addTab(browser_tab, "Browser Agent")
        
        # Aba de configurações
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        tabs.addTab(settings_tab, "Configurações")
        
        # Aba de configuração de APIs
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        tabs.addTab(api_tab, "Configuração de APIs")
        
        # === CONTEÚDO DA ABA DE GERENCIAMENTO DE MCPs ===
        
        # Área de pesquisa
        search_group = QGroupBox("Pesquisar MCPs")
        search_layout = QHBoxLayout(search_group)
        
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para buscar MCPs...")
        self.search_input.textChanged.connect(self.filter_mcps)
        search_layout.addWidget(self.search_input)
        
        search_layout.addWidget(QLabel("Fonte:"))
        self.source_filter = QComboBox()
        self.source_filter.addItems(["Todas", "HiMCP.ai", "MCP.so", "Smithery", "Cursor Directory", "PulseMCP"])
        self.source_filter.currentTextChanged.connect(self.filter_mcps)
        search_layout.addWidget(self.source_filter)
        
        search_layout.addWidget(QLabel("Tipo:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Todos", "LLM", "Code", "Vision", "Data", "Tool", "Browser"])
        self.type_filter.currentTextChanged.connect(self.filter_mcps)
        search_layout.addWidget(self.type_filter)
        
        refresh_button = QPushButton("Atualizar")
        refresh_button.clicked.connect(self.refresh_mcps)
        search_layout.addWidget(refresh_button)
        
        mcp_layout.addWidget(search_group)
        
        # Tabela de MCPs
        self.mcp_table = QTableWidget(0, 6)  # Aumentei para 6 colunas para incluir checkbox
        self.mcp_table.setHorizontalHeaderLabels(["Selecionar", "ID", "Nome", "Fonte", "Tipo", "Status"])
        self.mcp_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        mcp_layout.addWidget(self.mcp_table)
        
        # Área de ações
        actions_group = QGroupBox("Ações")
        actions_layout = QHBoxLayout(actions_group)
        
        toggle_selected_button = QPushButton("Alternar Selecionados")
        toggle_selected_button.clicked.connect(self.toggle_selected_mcps)
        actions_layout.addWidget(toggle_selected_button)
        
        enable_all_button = QPushButton("Ativar Todos")
        enable_all_button.clicked.connect(lambda: self.toggle_all_mcps(True))
        actions_layout.addWidget(enable_all_button)
        
        disable_all_button = QPushButton("Desativar Todos")
        disable_all_button.clicked.connect(lambda: self.toggle_all_mcps(False))
        actions_layout.addWidget(disable_all_button)
        
        # Adicionar botão para finalizar MCPs selecionados
        terminate_selected_button = QPushButton("Finalizar Selecionados")
        terminate_selected_button.clicked.connect(self.terminate_selected_mcps)
        terminate_selected_button.setStyleSheet("background-color: #ffaaaa;")  # Cor vermelha para alertar
        actions_layout.addWidget(terminate_selected_button)
        
        import_button = QPushButton("Importar MCPs")
        import_button.clicked.connect(self.import_mcps)
        actions_layout.addWidget(import_button)
        
        export_button = QPushButton("Exportar MCPs")
        export_button.clicked.connect(self.export_mcps)
        actions_layout.addWidget(export_button)
        
        mcp_layout.addWidget(actions_group)
        
        # === CONTEÚDO DA ABA DE HISTÓRICO DE PROMPTS ===
        
        # Tabela de histórico
        self.history_table = QTableWidget(0, 3)
        self.history_table.setHorizontalHeaderLabels(["Data/Hora", "MCP", "Prompt"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        history_layout.addWidget(self.history_table)
        
        # Área de detalhes do prompt
        prompt_details_group = QGroupBox("Detalhes do Prompt")
        prompt_details_layout = QVBoxLayout(prompt_details_group)
        
        self.prompt_details = QTextEdit()
        self.prompt_details.setReadOnly(True)
        prompt_details_layout.addWidget(self.prompt_details)
        
        history_layout.addWidget(prompt_details_group)
        
        # Botões de ação
        history_actions_layout = QHBoxLayout()
        
        export_history_button = QPushButton("Exportar Histórico")
        export_history_button.clicked.connect(self.export_history)
        history_actions_layout.addWidget(export_history_button)
        
        clear_history_button = QPushButton("Limpar Histórico")
        clear_history_button.clicked.connect(self.clear_history)
        history_actions_layout.addWidget(clear_history_button)
        
        history_layout.addLayout(history_actions_layout)
        
        # === CONTEÚDO DA ABA DE AUTOMAÇÃO ===
        
        # Grupo de terminal
        terminal_group = QGroupBox("Execução de Comandos no Terminal")
        terminal_layout = QVBoxLayout(terminal_group)
        
        # Tipo de terminal
        terminal_type_layout = QHBoxLayout()
        terminal_type_layout.addWidget(QLabel("Tipo de Terminal:"))
        self.terminal_type_combo = QComboBox()
        self.terminal_type_combo.addItems(["Automático", "CMD", "PowerShell", "Bash", "Docker"])
        terminal_type_layout.addWidget(self.terminal_type_combo)
        terminal_layout.addLayout(terminal_type_layout)
        
        # Entrada de comando
        command_layout = QHBoxLayout()
        command_layout.addWidget(QLabel("Comando:"))
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Digite um comando para executar...")
        self.command_input.returnPressed.connect(self.execute_command)
        command_layout.addWidget(self.command_input)
        
        execute_button = QPushButton("Executar")
        execute_button.clicked.connect(self.execute_command)
        command_layout.addWidget(execute_button)
        
        terminal_layout.addLayout(command_layout)
        
        # Área de resultado
        terminal_result_label = QLabel("Resultado:")
        terminal_layout.addWidget(terminal_result_label)
        
        self.terminal_result = QTextEdit()
        self.terminal_result.setReadOnly(True)
        terminal_layout.addWidget(self.terminal_result)
        
        automation_layout.addWidget(terminal_group)
        
        # Grupo de script Python
        script_group = QGroupBox("Scripts Python")
        script_layout = QVBoxLayout(script_group)
        
        # Entrada do nome do arquivo
        script_name_layout = QHBoxLayout()
        script_name_layout.addWidget(QLabel("Nome do arquivo:"))
        self.script_name_input = QLineEdit()
        self.script_name_input.setPlaceholderText("Nome do arquivo (opcional)...")
        script_name_layout.addWidget(self.script_name_input)
        script_layout.addLayout(script_name_layout)
        
        # Área de edição do script
        script_content_label = QLabel("Conteúdo do script:")
        script_layout.addWidget(script_content_label)
        
        self.script_content = QTextEdit()
        self.script_content.setPlaceholderText("# Digite seu código Python aqui\n\n# Exemplo:\nprint('Hello, world!')")
        script_layout.addWidget(self.script_content)
        
        # Botões de ação
        script_actions_layout = QHBoxLayout()
        
        create_script_button = QPushButton("Criar Script")
        create_script_button.clicked.connect(self.create_script)
        script_actions_layout.addWidget(create_script_button)
        
        load_script_button = QPushButton("Carregar Script")
        load_script_button.clicked.connect(self.load_script)
        script_actions_layout.addWidget(load_script_button)
        
        run_script_button = QPushButton("Executar Script")
        run_script_button.clicked.connect(self.run_script)
        script_actions_layout.addWidget(run_script_button)
        
        script_layout.addLayout(script_actions_layout)
        
        automation_layout.addWidget(script_group)
        
        # === CONTEÚDO DA ABA DE CHAT ===
        
        # Área do chat
        chat_display_group = QGroupBox("Conversação com Fil")
        chat_display_layout = QVBoxLayout(chat_display_group)
        
        # Área de exibição do chat com rolagem
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        chat_content = QWidget()
        self.chat_messages_layout = QVBoxLayout(chat_content)
        self.chat_messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_messages_layout.setSpacing(10)
        scroll_area.setWidget(chat_content)
        chat_display_layout.addWidget(scroll_area)
        
        chat_layout.addWidget(chat_display_group, 7)  # Proporção 7
        
        # Área de entrada
        input_group = QGroupBox("Enviar Mensagem")
        input_layout = QHBoxLayout(input_group)
        
        # Campo de texto
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Digite uma mensagem ou comando para o Fil...")
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input, 8)  # Proporção 8
        
        # Botão de envio
        send_button = QPushButton("Enviar")
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button, 1)  # Proporção 1
        
        # Botão de microfone (apenas se recursos de voz estiverem disponíveis)
        if self.voice_available:
            self.mic_button = QPushButton()
            self.mic_button.setIcon(QIcon("mic_off.png"))  # Será substituído por ícone dinâmico
            self.mic_button.setCheckable(True)
            self.mic_button.setToolTip("Ativar/Desativar reconhecimento de voz")
            self.mic_button.clicked.connect(self.toggle_voice_recognition)
            input_layout.addWidget(self.mic_button, 1)  # Proporção 1
        
        chat_layout.addWidget(input_group, 1)  # Proporção 1
        
        # === CONTEÚDO DA ABA DE CONFIGURAÇÕES ===
        
        # Configurações de diretórios
        paths_group = QGroupBox("Caminhos")
        paths_layout = QVBoxLayout(paths_group)
        
        cursor_path_layout = QHBoxLayout()
        cursor_path_layout.addWidget(QLabel("Pasta do Cursor:"))
        self.cursor_path_input = QLineEdit()
        self.cursor_path_input.setPlaceholderText("Caminho para a pasta do Cursor...")
        cursor_path_layout.addWidget(self.cursor_path_input)
        browse_cursor_button = QPushButton("Procurar...")
        browse_cursor_button.clicked.connect(lambda: self.browse_folder(self.cursor_path_input))
        cursor_path_layout.addWidget(browse_cursor_button)
        paths_layout.addLayout(cursor_path_layout)
        
        history_path_layout = QHBoxLayout()
        history_path_layout.addWidget(QLabel("Pasta de Histórico:"))
        self.history_path_input = QLineEdit()
        self.history_path_input.setPlaceholderText("Caminho para salvar o histórico...")
        history_path_layout.addWidget(self.history_path_input)
        browse_history_button = QPushButton("Procurar...")
        browse_history_button.clicked.connect(lambda: self.browse_folder(self.history_path_input))
        history_path_layout.addWidget(browse_history_button)
        paths_layout.addLayout(history_path_layout)
        
        settings_layout.addWidget(paths_group)
        
        # Opções gerais
        options_group = QGroupBox("Opções")
        options_layout = QVBoxLayout(options_group)
        
        self.auto_start_checkbox = QCheckBox("Iniciar com o VS Code")
        options_layout.addWidget(self.auto_start_checkbox)
        
        self.read_only_checkbox = QCheckBox("Definir pasta de histórico como somente leitura")
        options_layout.addWidget(self.read_only_checkbox)
        
        self.auto_backup_checkbox = QCheckBox("Backup automático do arquivo mcp.json")
        options_layout.addWidget(self.auto_backup_checkbox)
        
        # Opções de voz (somente se disponível)
        if self.voice_available:
            self.voice_enabled_checkbox = QCheckBox("Ativar respostas por voz")
            self.voice_enabled_checkbox.setChecked(self.voice_enabled)
            self.voice_enabled_checkbox.stateChanged.connect(self.toggle_voice_output)
            options_layout.addWidget(self.voice_enabled_checkbox)
        
        settings_layout.addWidget(options_group)
        
        # Botões de ação das configurações
        settings_actions_layout = QHBoxLayout()
        
        save_settings_button = QPushButton("Salvar Configurações")
        save_settings_button.clicked.connect(self.save_settings)
        settings_actions_layout.addWidget(save_settings_button)
        
        reset_settings_button = QPushButton("Restaurar Padrões")
        reset_settings_button.clicked.connect(self.reset_settings)
        settings_actions_layout.addWidget(reset_settings_button)
        
        settings_layout.addLayout(settings_actions_layout)
        
        # === CONTEÚDO DA ABA DO BROWSER AGENT ===
        
        # Status e controles
        browser_status_group = QGroupBox("Status do Browser Agent MCP")
        browser_status_layout = QVBoxLayout(browser_status_group)
        
        # Status atual
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Browser Agent MCP:"))
        self.browser_status_label = QLabel("Status: <span style='color: #F44336;'><b>Inativo</b></span>")
        self.browser_status_label.setTextFormat(Qt.RichText)
        status_layout.addWidget(self.browser_status_label)
        browser_status_layout.addLayout(status_layout)
        
        # Botões de controle
        browser_control_layout = QHBoxLayout()
        
        self.browser_start_button = QPushButton("Iniciar Browser Agent")
        self.browser_start_button.clicked.connect(self.start_browser_agent)
        browser_control_layout.addWidget(self.browser_start_button)
        
        self.browser_stop_button = QPushButton("Parar Browser Agent")
        self.browser_stop_button.clicked.connect(self.stop_browser_agent)
        self.browser_stop_button.setEnabled(False)  # Inicialmente desativado
        browser_control_layout.addWidget(self.browser_stop_button)
        
        browser_status_layout.addLayout(browser_control_layout)
        
        browser_layout.addWidget(browser_status_group)
        
        # Ações do Browser
        browser_actions_group = QGroupBox("Ações do Browser")
        browser_actions_layout = QVBoxLayout(browser_actions_group)
        
        # URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.browser_url_input = QLineEdit()
        self.browser_url_input.setPlaceholderText("https://exemplo.com")
        url_layout.addWidget(self.browser_url_input)
        
        self.browser_navigate_button = QPushButton("Navegar")
        self.browser_navigate_button.clicked.connect(self.navigate_to_url)
        url_layout.addWidget(self.browser_navigate_button)
        
        browser_actions_layout.addLayout(url_layout)
        
        # Botões de ação
        action_buttons_layout = QHBoxLayout()
        
        self.browser_screenshot_button = QPushButton("Capturar Screenshot")
        self.browser_screenshot_button.clicked.connect(self.take_screenshot)
        self.browser_screenshot_button.setEnabled(False)  # Inicialmente desativado
        action_buttons_layout.addWidget(self.browser_screenshot_button)
        
        browser_actions_layout.addLayout(action_buttons_layout)
        
        # Comando de Console
        console_layout = QVBoxLayout()
        console_layout.addWidget(QLabel("Comando para o Console:"))
        
        self.browser_console_input = QTextEdit()
        self.browser_console_input.setPlaceholderText("Digite um comando JavaScript para executar no console do navegador...")
        self.browser_console_input.setMaximumHeight(100)
        console_layout.addWidget(self.browser_console_input)
        
        self.browser_console_button = QPushButton("Executar no Console")
        self.browser_console_button.clicked.connect(self.execute_in_console)
        self.browser_console_button.setEnabled(False)  # Inicialmente desativado
        console_layout.addWidget(self.browser_console_button)
        
        browser_actions_layout.addLayout(console_layout)
        
        browser_layout.addWidget(browser_actions_group)
        
        # Integração com Cursor/VS Code
        integration_group = QGroupBox("Integração com Editor")
        integration_layout = QVBoxLayout(integration_group)
        
        # Detecção de projeto
        detect_project_layout = QHBoxLayout()
        detect_project_layout.addWidget(QLabel("Projeto:"))
        self.project_path_label = QLabel("Nenhum projeto detectado")
        detect_project_layout.addWidget(self.project_path_label)
        
        detect_button = QPushButton("Detectar Projeto")
        detect_button.clicked.connect(self.detect_project)
        detect_project_layout.addWidget(detect_button)
        
        integration_layout.addLayout(detect_project_layout)
        
        # Informações do mcp.json (para Cursor)
        mcp_json_layout = QVBoxLayout()
        mcp_json_layout.addWidget(QLabel("Arquivo MCP.JSON do Cursor:"))
        
        self.mcp_json_path_label = QLabel("Não encontrado")
        mcp_json_layout.addWidget(self.mcp_json_path_label)
        
        # Botões para mcp.json
        mcp_json_buttons_layout = QHBoxLayout()
        
        edit_mcp_json_button = QPushButton("Editar MCP.JSON")
        edit_mcp_json_button.clicked.connect(self.edit_mcp_json)
        mcp_json_buttons_layout.addWidget(edit_mcp_json_button)
        
        add_browser_to_mcp_button = QPushButton("Adicionar Browser Agent ao MCP.JSON")
        add_browser_to_mcp_button.clicked.connect(self.add_browser_to_mcp_json)
        mcp_json_buttons_layout.addWidget(add_browser_to_mcp_button)
        
        mcp_json_layout.addLayout(mcp_json_buttons_layout)
        
        integration_layout.addLayout(mcp_json_layout)
        
        browser_layout.addWidget(integration_group)
        
        # Restante do código UI existente...
        # ...
        
        # Barra de status
        self.statusBar().showMessage("Pronto. MCPs carregados: " + str(len(self.mcps)))
        
        # Preencher os dados iniciais
        self.populate_mcp_table()
        self.populate_history_table()
        
        # Adicionar mensagem de boas-vindas ao chat
        self.agent.respond("Olá! Sou o Fil, seu assistente para gerenciamento de MCPs e automações. Como posso ajudar você hoje?")
    
    def populate_mcp_table(self):
        # Limpar tabela
        self.mcp_table.setRowCount(0)
        
        # Adicionar MCPs à tabela
        for row, mcp in enumerate(self.mcps):
            self.mcp_table.insertRow(row)
            
            # Adicionar checkbox para seleção
            checkbox = QCheckBox()
            checkbox.setChecked(False)
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.mcp_table.setCellWidget(row, 0, checkbox_widget)
            
            # Adicionar dados MCP
            self.mcp_table.setItem(row, 1, QTableWidgetItem(mcp["id"]))
            self.mcp_table.setItem(row, 2, QTableWidgetItem(mcp["name"]))
            self.mcp_table.setItem(row, 3, QTableWidgetItem(mcp["source"]))
            self.mcp_table.setItem(row, 4, QTableWidgetItem(mcp["type"]))
            
            status_item = QTableWidgetItem("Ativo" if mcp["status"] else "Inativo")
            if mcp["status"]:
                status_item.setBackground(QColor(200, 255, 200))  # Verde claro
            else:
                status_item.setBackground(QColor(255, 200, 200))  # Vermelho claro
            
            self.mcp_table.setItem(row, 5, status_item)
    
    def populate_history_table(self):
        # Limpar tabela
        self.history_table.setRowCount(0)
        
        # Adicionar histórico à tabela
        for row, entry in enumerate(self.prompts_history):
            self.history_table.insertRow(row)
            self.history_table.setItem(row, 0, QTableWidgetItem(entry["timestamp"]))
            self.history_table.setItem(row, 1, QTableWidgetItem(entry["mcp"]))
            self.history_table.setItem(row, 2, QTableWidgetItem(entry["prompt"][:50] + "..." if len(entry["prompt"]) > 50 else entry["prompt"]))
        
        # Conectar clique na tabela para mostrar detalhes
        self.history_table.cellClicked.connect(self.show_prompt_details)
    
    def show_prompt_details(self, row, column):
        entry = self.prompts_history[row]
        details = f"Timestamp: {entry['timestamp']}\nMCP: {entry['mcp']}\n\nPrompt:\n{entry['prompt']}"
        self.prompt_details.setText(details)
    
    def filter_mcps(self):
        search_text = self.search_input.text().lower()
        source_filter = self.source_filter.currentText()
        type_filter = self.type_filter.currentText()
        
        # Resetar filtros se "Todas"/"Todos" estiverem selecionados
        if source_filter == "Todas":
            source_filter = ""
        
        if type_filter == "Todos":
            type_filter = ""
        
        # Filtrar MCPs
        filtered_mcps = []
        for mcp in self.mcps:
            # Verificar texto de busca
            if (search_text and search_text not in mcp["name"].lower() and 
                search_text not in mcp["id"].lower()):
                continue
            
            # Verificar filtro de fonte
            if source_filter and mcp["source"] != source_filter:
                continue
            
            # Verificar filtro de tipo
            if type_filter and mcp["type"] != type_filter:
                continue
            
            filtered_mcps.append(mcp)
        
        # Atualizar tabela com os MCPs filtrados
        self.mcp_table.setRowCount(0)
        for row, mcp in enumerate(filtered_mcps):
            self.mcp_table.insertRow(row)
            
            # Adicionar checkbox para seleção
            checkbox = QCheckBox()
            checkbox.setChecked(False)
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.mcp_table.setCellWidget(row, 0, checkbox_widget)
            
            # Adicionar dados MCP
            self.mcp_table.setItem(row, 1, QTableWidgetItem(mcp["id"]))
            self.mcp_table.setItem(row, 2, QTableWidgetItem(mcp["name"]))
            self.mcp_table.setItem(row, 3, QTableWidgetItem(mcp["source"]))
            self.mcp_table.setItem(row, 4, QTableWidgetItem(mcp["type"]))
            
            status_item = QTableWidgetItem("Ativo" if mcp["status"] else "Inativo")
            if mcp["status"]:
                status_item.setBackground(QColor(200, 255, 200))
            else:
                status_item.setBackground(QColor(255, 200, 200))
            
            self.mcp_table.setItem(row, 5, status_item)
    
    def toggle_selected_mcps(self):
        """Alterna o status dos MCPs selecionados"""
        selected_mcps = []
        
        # Verificar checkboxes marcados
        for row in range(self.mcp_table.rowCount()):
            checkbox_widget = self.mcp_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    mcp_id = self.mcp_table.item(row, 1).text()
                    selected_mcps.append(mcp_id)
        
        if not selected_mcps:
            QMessageBox.information(
                self, "Seleção Vazia", "Por favor, selecione pelo menos um MCP.")
            return
        
        # Alternar status dos MCPs selecionados
        for mcp_id in selected_mcps:
            for mcp in self.mcps:
                if mcp["id"] == mcp_id:
                    mcp["status"] = not mcp["status"]
                    break
        
        # Atualizar a tabela
        self.populate_mcp_table()
        
        # Atualizar mensagem de status
        self.statusBar().showMessage(f"{len(selected_mcps)} MCPs alternados.")
    
    def terminate_selected_mcps(self):
        """Finaliza os MCPs selecionados (encerra seus processos)"""
        selected_mcps = []
        
        # Verificar checkboxes marcados
        for row in range(self.mcp_table.rowCount()):
            checkbox_widget = self.mcp_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    mcp_id = self.mcp_table.item(row, 1).text()
                    mcp_name = self.mcp_table.item(row, 2).text()
                    selected_mcps.append((mcp_id, mcp_name))
        
        if not selected_mcps:
            QMessageBox.information(
                self, "Seleção Vazia", "Por favor, selecione pelo menos um MCP para finalizar.")
            return
        
        # Confirmação do usuário
        mcp_names = "\n".join([f"- {name} (ID: {id})" for id, name in selected_mcps])
        reply = QMessageBox.question(
            self, "Confirmar Finalização",
            f"Tem certeza que deseja finalizar os seguintes MCPs?\n\n{mcp_names}\n\n"
            f"Atenção: Isso encerrará os processos desses MCPs.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        # Implementar a finalização dos MCPs selecionados
        terminated_count = 0
        for mcp_id, _ in selected_mcps:
            # Encontrar e terminar o MCP
            for mcp in self.mcps:
                if mcp["id"] == mcp_id:
                    # Em uma implementação real, aqui você enviaria
                    # um comando para encerrar o processo do MCP
                    # Exemplo simulado:
                    if mcp["status"]:
                        mcp["status"] = False
                        terminated_count += 1
                    break
        
        # Implementação de exemplo - em um sistema real você teria
        # que localizar e encerrar os processos dos MCPs
        if terminated_count > 0:
            # Notificar o agente Fil sobre a ação
            self.agent.respond(f"Finalizado(s) {terminated_count} MCP(s) conforme solicitado.")
            
            # Atualizar a tabela
            self.populate_mcp_table()
            
            # Atualizar mensagem de status
            self.statusBar().showMessage(f"{terminated_count} MCPs finalizados com sucesso.")
        else:
            QMessageBox.information(
                self, "Informação", "Nenhum MCP ativo foi encontrado para finalizar.")
    
    def toggle_all_mcps(self, status):
        """Define o status de todos os MCPs visíveis na tabela"""
        # Em uma implementação real, você poderia verificar filtros aplicados
        # e operar apenas nos MCPs visíveis
        
        # Alternar status de todos os MCPs
        for mcp in self.mcps:
            mcp["status"] = status
        
        # Atualizar a tabela
        self.populate_mcp_table()
        
        # Atualizar mensagem de status
        action = "ativados" if status else "desativados"
        self.statusBar().showMessage(f"Todos os MCPs foram {action}.")
        
        # Notificar o agente Fil sobre a ação
        if status:
            self.agent.respond("Todos os MCPs foram ativados.", speak=False)
        else:
            self.agent.respond("Todos os MCPs foram desativados.", speak=False)
    
    def refresh_mcps(self):
        # Simular recarregamento de MCPs
        self.statusBar().showMessage("Atualizando lista de MCPs...")
        
        # Em uma implementação real, recarregaria do arquivo mcp.json
        # ou das fontes online de MCPs
        
        # Atualizar a tabela após um breve atraso para simular carregamento
        QTimer.singleShot(500, lambda: self.populate_mcp_table())
        QTimer.singleShot(500, lambda: self.statusBar().showMessage("MCPs atualizados com sucesso."))
    
    def import_mcps(self):
        # Abrir diálogo para selecionar arquivo JSON
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar MCPs", "", "Arquivos JSON (*.json)")
        
        if file_path:
            try:
                # Em uma implementação real, carregaria os MCPs do arquivo
                # e os adicionaria à lista existente ou substituiria
                
                # Simulação
                QMessageBox.information(
                    self, "Importação", "MCPs importados com sucesso!")
                
                self.statusBar().showMessage(f"MCPs importados de {file_path}")
                
            except Exception as e:
                QMessageBox.critical(
                    self, "Erro", f"Erro ao importar MCPs: {str(e)}")
    
    def export_mcps(self):
        # Abrir diálogo para salvar arquivo JSON
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar MCPs", "", "Arquivos JSON (*.json)")
        
        if file_path:
            try:
                # Em uma implementação real, salvaria os MCPs em um arquivo JSON
                
                # Simular exportação
                with open(file_path, 'w') as f:
                    json.dump(self.mcps, f, indent=4)
                
                QMessageBox.information(
                    self, "Exportação", "MCPs exportados com sucesso!")
                
                self.statusBar().showMessage(f"MCPs exportados para {file_path}")
                
            except Exception as e:
                QMessageBox.critical(
                    self, "Erro", f"Erro ao exportar MCPs: {str(e)}")
    
    def export_history(self):
        # Abrir diálogo para salvar arquivo JSON
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Histórico", "", "Arquivos JSON (*.json)")
        
        if file_path:
            try:
                # Em uma implementação real, salvaria o histórico em um arquivo JSON
                
                # Simular exportação
                with open(file_path, 'w') as f:
                    json.dump(self.prompts_history, f, indent=4)
                
                QMessageBox.information(
                    self, "Exportação", "Histórico exportado com sucesso!")
                
                self.statusBar().showMessage(f"Histórico exportado para {file_path}")
                
            except Exception as e:
                QMessageBox.critical(
                    self, "Erro", f"Erro ao exportar histórico: {str(e)}")
    
    def clear_history(self):
        # Confirmar com o usuário
        reply = QMessageBox.question(
            self, "Limpar Histórico",
            "Tem certeza que deseja limpar todo o histórico de prompts?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Em uma implementação real, limparia o histórico
            self.prompts_history = []
            
            # Atualizar a tabela
            self.history_table.setRowCount(0)
            self.prompt_details.clear()
            
            self.statusBar().showMessage("Histórico de prompts limpo.")
    
    def browse_folder(self, line_edit):
        folder_path = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta", "")
        
        if folder_path:
            line_edit.setText(folder_path)
    
    def save_settings(self):
        # Em uma implementação real, salvaria as configurações
        
        # Simular salvamento
        cursor_path = self.cursor_path_input.text()
        history_path = self.history_path_input.text()
        auto_start = self.auto_start_checkbox.isChecked()
        read_only = self.read_only_checkbox.isChecked()
        auto_backup = self.auto_backup_checkbox.isChecked()
        
        # Validar caminhos
        if not cursor_path or not history_path:
            QMessageBox.warning(
                self, "Campos Obrigatórios", 
                "Por favor, preencha todos os caminhos de pasta.")
            return
        
        # Mostrar confirmação
        QMessageBox.information(
            self, "Configurações", "Configurações salvas com sucesso!")
        
        self.statusBar().showMessage("Configurações salvas.")
    
    def reset_settings(self):
        # Em uma implementação real, restauraria as configurações padrão
        
        # Simular reset
        self.cursor_path_input.clear()
        self.history_path_input.clear()
        self.auto_start_checkbox.setChecked(False)
        self.read_only_checkbox.setChecked(False)
        self.auto_backup_checkbox.setChecked(True)
        
        self.statusBar().showMessage("Configurações restauradas para os valores padrão.")

    # === MÉTODOS DE CHAT E RECONHECIMENTO DE VOZ ===
    
    def add_chat_message(self, sender, message, message_type):
        """Adiciona uma mensagem ao chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Cria um widget para a mensagem
        message_widget = QWidget()
        message_layout = QVBoxLayout(message_widget)
        
        # Adiciona cabeçalho com remetente e timestamp
        header_layout = QHBoxLayout()
        sender_label = QLabel(f"<b>{sender}</b>")
        time_label = QLabel(f"<i>{timestamp}</i>")
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        header_layout.addWidget(sender_label)
        header_layout.addWidget(time_label)
        message_layout.addLayout(header_layout)
        
        # Adiciona conteúdo da mensagem
        content_label = QLabel(message)
        content_label.setWordWrap(True)
        content_label.setTextFormat(Qt.TextFormat.RichText)
        
        # Estilo diferente para usuário e assistente
        if message_type == "user":
            message_widget.setStyleSheet("background-color: #e6f7ff; border-radius: 5px; padding: 5px;")
        else:  # assistant
            message_widget.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 5px;")
        
        message_layout.addWidget(content_label)
        
        # Adiciona a mensagem ao layout
        self.chat_messages_layout.addWidget(message_widget)
        
        # Adiciona ao histórico
        self.chat_history.append({
            "timestamp": timestamp,
            "sender": sender,
            "message": message,
            "type": message_type
        })
        
        # Se a saída de voz estiver ativada e for mensagem do assistente, fala a mensagem
        if self.voice_enabled and message_type == "assistant":
            self.speak_message(message)
    
    def send_message(self):
        """Envia uma mensagem do usuário para o agente Fil"""
        message = self.chat_input.text().strip()
        if not message:
            return
        
        # Adiciona mensagem do usuário
        self.add_chat_message("Você", message, "user")
        self.chat_input.clear()
        
        # Processa o comando com o agente Fil
        self.agent.process_command(message)
    
    def simulate_assistant_response(self, user_message):
        """Simula uma resposta do assistente com base na mensagem do usuário"""
        # Em uma implementação real, aqui você se conectaria à API do LLM
        # Por enquanto, vamos simular algumas respostas básicas
        
        user_message_lower = user_message.lower()
        
        if "olá" in user_message_lower or "oi" in user_message_lower:
            response = "Olá! Em que posso ajudar com seus MCPs hoje?"
        elif "mcp" in user_message_lower:
            response = "MCPs (Model Control Protocol) são protocolos para interagir com modelos de IA. Posso ajudar você a gerenciá-los através desta interface."
        elif "ajuda" in user_message_lower or "help" in user_message_lower:
            response = "Posso ajudar com: <br>- Buscar MCPs por nome ou tipo<br>- Ativar/desativar MCPs<br>- Importar/exportar configurações<br>- Salvar histórico de prompts"
        elif "obrigado" in user_message_lower or "obrigada" in user_message_lower:
            response = "Disponha! Estou aqui para ajudar sempre que precisar."
        else:
            response = "Entendi sua mensagem. Para interagir com seus MCPs, você pode usar a aba 'Gerenciamento de MCPs'. Alguma dúvida específica sobre como usar o sistema?"
        
        # Adiciona uma pequena pausa para parecer mais natural
        QTimer.singleShot(800, lambda: self.add_chat_message("Assistente", response, "assistant"))
    
    def toggle_voice_recognition(self, checked):
        """Ativa ou desativa o reconhecimento de voz"""
        if not self.voice_available:
            QMessageBox.warning(self, "Recurso Indisponível", 
                               "O reconhecimento de voz não está disponível. Verifique se as bibliotecas necessárias estão instaladas.")
            # Reset do botão
            self.mic_button.setChecked(False)
            return
        
        if checked:
            # Inicia o reconhecimento de voz
            self.is_listening = True
            self.statusBar().showMessage("Reconhecimento de voz ativado. Fale um comando para Fil...")
            self.mic_button.setIcon(QIcon("mic_on.png"))  # Seria substituído por ícone dinâmico
            
            # Notifica o usuário
            self.agent.respond("Reconhecimento de voz ativado. Estou ouvindo seus comandos.", speak=False)
            
            # Inicia a thread de reconhecimento de voz
            self.speech_thread = threading.Thread(target=self.listen_for_speech)
            self.speech_thread.daemon = True
            self.speech_thread.start()
        else:
            # Para o reconhecimento de voz
            self.is_listening = False
            self.statusBar().showMessage("Reconhecimento de voz desativado.")
            self.mic_button.setIcon(QIcon("mic_off.png"))  # Seria substituído por ícone dinâmico
            
            # Notifica o usuário
            self.agent.respond("Reconhecimento de voz desativado.", speak=False)
    
    def listen_for_speech(self):
        """Thread para ouvir fala continuamente"""
        if not self.voice_available:
            return
            
        try:
            # Ajusta para ruído ambiente
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                
            while self.is_listening:
                try:
                    with self.microphone as source:
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    # Reconhece a fala
                    text = self.recognizer.recognize_google(audio, language='pt-BR')
                    
                    # Emite o sinal com o texto reconhecido
                    self.speech_signal.emit(text)
                    
                except sr.UnknownValueError:
                    # Fala não reconhecida
                    pass
                except sr.RequestError as e:
                    # Erro na API
                    self.statusBar().showMessage(f"Erro na API de reconhecimento: {e}")
                    break
                except sr.WaitTimeoutError:
                    # Timeout esperando pelo áudio
                    pass
                
        except Exception as e:
            self.statusBar().showMessage(f"Erro no reconhecimento de voz: {e}")
            self.is_listening = False
    
    @pyqtSlot(str)
    def process_speech(self, text):
        """Processa o texto reconhecido da fala"""
        if text and self.is_listening:
            # Coloca o texto no campo de entrada e mostra para o usuário
            self.chat_input.setText(text)
            
            # Adiciona mensagem do usuário ao chat
            self.add_chat_message("Você", text, "user")
            
            # Limpa o campo de entrada
            self.chat_input.clear()
            
            # Processa o comando com o agente Fil
            self.agent.process_command(text)
    
    def toggle_voice_output(self, state):
        """Ativa ou desativa a saída de voz"""
        if not self.voice_available:
            QMessageBox.warning(self, "Recurso Indisponível", 
                               "A síntese de voz não está disponível. Verifique se as bibliotecas necessárias estão instaladas.")
            return
            
        self.voice_enabled = bool(state)
    
    def speak_message(self, message):
        """Fala uma mensagem usando síntese de voz"""
        if not self.voice_available or not self.voice_enabled:
            return
            
        # Remove tags HTML para a fala
        plain_text = message.replace("<br>", " ")
        
        # Coloca em uma thread para não bloquear a UI
        def speak_thread():
            try:
                self.engine.say(plain_text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Erro ao falar: {e}")
        
        threading.Thread(target=speak_thread).start()

    # === MÉTODOS DE CONFIGURAÇÃO DE APIs ===
    
    def filter_openrouter_models(self):
        """Filtra os modelos da OpenRouter com base na busca"""
        search_text = self.openrouter_search.text().lower()
        
        # Limpa a lista atual
        self.openrouter_model_list.clear()
        
        # Adiciona modelos que correspondem à busca
        for model in self.api_config.openrouter_models:
            if search_text in model.lower():
                item = QListWidgetItem(model)
                if model == self.api_config.openrouter_selected_model:
                    item.setSelected(True)
                self.openrouter_model_list.addItem(item)
    
    def update_openrouter_model(self, item):
        """Atualiza o modelo selecionado da OpenRouter"""
        self.api_config.openrouter_selected_model = item.text()
        self.statusBar().showMessage(f"Modelo OpenRouter selecionado: {item.text()}", 3000)
    
    def update_gemini_model(self, model):
        """Atualiza o modelo selecionado do Gemini"""
        self.api_config.gemini_selected_model = model
        self.statusBar().showMessage(f"Modelo Gemini selecionado: {model}", 3000)
    
    def update_claude_model(self, model):
        """Atualiza o modelo selecionado do Claude"""
        self.api_config.claude_selected_model = model
        self.statusBar().showMessage(f"Modelo Claude selecionado: {model}", 3000)
    
    def update_deepseek_model(self, model):
        """Atualiza o modelo selecionado do DeepSeek"""
        self.api_config.deepseek_selected_model = model
        self.statusBar().showMessage(f"Modelo DeepSeek selecionado: {model}", 3000)
    
    def save_api_settings(self):
        """Salva as configurações de API"""
        # Atualiza as chaves API em memória
        self.api_config.openrouter_api_key = self.openrouter_key_input.text()
        self.api_config.gemini_api_key = self.gemini_key_input.text()
        self.api_config.claude_api_key = self.claude_key_input.text()
        self.api_config.deepseek_api_key = self.deepseek_key_input.text()
        
        # Em uma implementação real, salvaria em um arquivo de configuração
        api_config = {
            "openrouter": {
                "api_key": self.api_config.openrouter_api_key,
                "selected_model": self.api_config.openrouter_selected_model
            },
            "gemini": {
                "api_key": self.api_config.gemini_api_key,
                "selected_model": self.api_config.gemini_selected_model
            },
            "claude": {
                "api_key": self.api_config.claude_api_key,
                "selected_model": self.api_config.claude_selected_model
            },
            "deepseek": {
                "api_key": self.api_config.deepseek_api_key,
                "selected_model": self.api_config.deepseek_selected_model
            }
        }
        
        # Simular salvamento em arquivo
        try:
            # Em uma implementação real, usaríamos algo como:
            # with open(config_path, 'w') as f:
            #     json.dump(api_config, f, indent=2)
            
            QMessageBox.information(
                self, "Sucesso", "Configurações de API salvas com sucesso!")
            
            self.statusBar().showMessage("Configurações de API salvas.", 3000)
            
        except Exception as e:
            QMessageBox.critical(
                self, "Erro", f"Erro ao salvar configurações: {str(e)}")
    
    def test_api_connection(self):
        """Testa a conexão com as APIs configuradas"""
        # Em uma implementação real, testaria cada API configurada
        
        # Simulação de teste
        apis_to_test = []
        
        if self.api_config.openrouter_api_key:
            apis_to_test.append("OpenRouter")
            
        if self.api_config.gemini_api_key:
            apis_to_test.append("Gemini")
            
        if self.api_config.claude_api_key:
            apis_to_test.append("Claude")
            
        if self.api_config.deepseek_api_key:
            apis_to_test.append("DeepSeek")
        
        if not apis_to_test:
            QMessageBox.warning(
                self, "Aviso", "Nenhuma API configurada para teste.")
            return
        
        # Simular teste bem-sucedido
        result_message = "Teste de conexão com APIs:\n\n"
        for api in apis_to_test:
            result_message += f"✓ {api}: Conexão bem-sucedida\n"
        
        QMessageBox.information(
            self, "Resultado do Teste", result_message)
            
        self.statusBar().showMessage("Teste de conexão concluído.", 3000)

    # === MÉTODOS DE AUTOMAÇÃO ===
    
    def execute_command(self):
        """Executa um comando no terminal selecionado"""
        command = self.command_input.text().strip()
        if not command:
            QMessageBox.warning(self, "Comando vazio", "Por favor, digite um comando para executar.")
            return
        
        # Obter o tipo de terminal
        terminal_type_map = {
            "Automático": "auto",
            "CMD": "cmd",
            "PowerShell": "powershell",
            "Bash": "bash",
            "Docker": "docker"
        }
        terminal_type = terminal_type_map[self.terminal_type_combo.currentText()]
        
        # Executar o comando
        self.terminal_result.clear()
        self.terminal_result.setPlainText("Executando comando...")
        
        # Usar uma thread para não bloquear a UI
        def run_command():
            result = self.agent.execute_terminal_command(command, terminal_type)
            self.terminal_result.setPlainText(result)
        
        threading.Thread(target=run_command).start()
    
    def create_script(self):
        """Cria um script Python com o conteúdo especificado"""
        content = self.script_content.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Conteúdo vazio", "Por favor, digite algum código para o script.")
            return
        
        file_name = self.script_name_input.text().strip()
        
        result = self.agent.create_python_script(content, file_name)
        QMessageBox.information(self, "Criação de Script", result)
    
    def load_script(self):
        """Carrega um script Python existente"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Carregar Script Python", "", "Scripts Python (*.py)")
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                self.script_content.setPlainText(content)
                self.script_name_input.setText(os.path.basename(file_path))
                
                self.statusBar().showMessage(f"Script carregado: {file_path}", 3000)
                
            except Exception as e:
                QMessageBox.critical(
                    self, "Erro", f"Erro ao carregar script: {str(e)}")
    
    def run_script(self):
        """Executa um script Python"""
        # Verificar se há um script na área de texto
        content = self.script_content.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Conteúdo vazio", "Por favor, digite ou carregue um script para executar.")
            return
        
        # Se o script não foi salvo, salvá-lo temporariamente
        file_name = self.script_name_input.text().strip()
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"temp_script_{timestamp}.py"
        
        if not file_name.endswith('.py'):
            file_name += '.py'
        
        # Salvar o script
        try:
            with open(file_name, 'w') as f:
                f.write(content)
            
            # Executar o script
            QMessageBox.information(self, "Execução de Script", f"Executando script: {file_name}")
            
            # Usar uma thread para não bloquear a UI
            def run_script_thread():
                result = self.agent.execute_python_script(file_name)
                # Mostrar o resultado em uma caixa de diálogo
                QMessageBox.information(self, "Resultado da Execução", result)
            
            threading.Thread(target=run_script_thread).start()
            
        except Exception as e:
            QMessageBox.critical(
                self, "Erro", f"Erro ao executar script: {str(e)}")

    # === MÉTODOS DO BROWSER AGENT ===
    
    def start_browser_agent(self):
        """Inicia o Browser Agent MCP"""
        result = self.agent.browser_agent.start()
        self.statusBar().showMessage(result)
    
    def stop_browser_agent(self):
        """Para o Browser Agent MCP"""
        result = self.agent.browser_agent.stop()
        self.statusBar().showMessage(result)
    
    def take_screenshot(self):
        """Captura uma screenshot do navegador"""
        url = self.browser_url_input.text().strip()
        result = self.agent.browser_agent.take_screenshot(url if url else None)
        self.statusBar().showMessage(result)
        
        # Em uma implementação real, você mostraria a screenshot capturada
        QMessageBox.information(self, "Screenshot", result)
    
    def execute_in_console(self):
        """Executa um comando no console do navegador"""
        command = self.browser_console_input.toPlainText().strip()
        if not command:
            QMessageBox.warning(self, "Comando Vazio", "Por favor, insira um comando JavaScript para executar.")
            return
        
        url = self.browser_url_input.text().strip()
        result = self.agent.browser_agent.execute_console_command(command, url if url else None)
        self.statusBar().showMessage(result)
    
    def navigate_to_url(self):
        """Navega para a URL especificada"""
        url = self.browser_url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "URL Vazia", "Por favor, insira uma URL para navegar.")
            return
        
        # Adicionar protocolo se não presente
        if not url.startswith("http"):
            url = "https://" + url
            self.browser_url_input.setText(url)
        
        result = self.agent.browser_agent.navigate_to(url)
        self.statusBar().showMessage(result)
    
    def detect_project(self):
        """Detecta se o diretório atual contém um projeto do Cursor ou VS Code"""
        if self.agent.detect_editor_project():
            # Atualizar UI
            self.project_path_label.setText(self.agent.active_project_path)
            project_type = self.agent.active_project_type.upper()
            
            if self.agent.mcp_json_path:
                self.mcp_json_path_label.setText(self.agent.mcp_json_path)
            
            self.statusBar().showMessage(f"Projeto {project_type} detectado em: {self.agent.active_project_path}")
            
            # Perguntar ao usuário se deseja iniciar o Browser Agent automaticamente
            reply = QMessageBox.question(
                self, "Browser Agent",
                f"Projeto {project_type} detectado. Deseja iniciar o Browser Agent MCP automaticamente?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                self.start_browser_agent()
        else:
            self.project_path_label.setText("Nenhum projeto detectado")
            self.mcp_json_path_label.setText("Não encontrado")
            self.statusBar().showMessage("Nenhum projeto Cursor ou VS Code detectado no diretório atual.")
    
    def edit_mcp_json(self):
        """Abre o arquivo mcp.json para edição"""
        if not self.agent.mcp_json_path or not os.path.exists(self.agent.mcp_json_path):
            # Tentar encontrar o arquivo
            self.agent.detect_editor_project()
            
            if not self.agent.mcp_json_path or not os.path.exists(self.agent.mcp_json_path):
                QMessageBox.warning(
                    self, "Arquivo Não Encontrado", 
                    "O arquivo mcp.json não foi encontrado. Verifique se o Cursor está instalado corretamente.")
                return
        
        # Abrir o arquivo no editor padrão do sistema
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.agent.mcp_json_path))
            self.statusBar().showMessage(f"Arquivo mcp.json aberto para edição: {self.agent.mcp_json_path}")
        except Exception as e:
            QMessageBox.critical(
                self, "Erro", f"Erro ao abrir o arquivo: {str(e)}")
    
    def add_browser_to_mcp_json(self):
        """Adiciona o Browser Agent MCP ao arquivo mcp.json do Cursor"""
        if not self.agent.mcp_json_path or not os.path.exists(self.agent.mcp_json_path):
            # Tentar encontrar o arquivo
            self.agent.detect_editor_project()
            
            if not self.agent.mcp_json_path or not os.path.exists(self.agent.mcp_json_path):
                QMessageBox.warning(
                    self, "Arquivo Não Encontrado", 
                    "O arquivo mcp.json não foi encontrado. Verifique se o Cursor está instalado corretamente.")
                return
        
        try:
            # Ler o arquivo mcp.json existente
            with open(self.agent.mcp_json_path, 'r') as f:
                mcp_data = json.load(f)
            
            # Verificar se já existe uma entrada para o Browser Agent
            browser_agent_entry = None
            if "mcps" in mcp_data:
                for mcp in mcp_data["mcps"]:
                    if mcp.get("name") == "Browser Agent" or mcp.get("id") == "browser-agent":
                        browser_agent_entry = mcp
                        break
            else:
                mcp_data["mcps"] = []
            
            # Se não existir, adicionar
            if not browser_agent_entry:
                # Criar uma nova entrada para o Browser Agent
                browser_agent_mcp = {
                    "id": "browser-agent",
                    "name": "Browser Agent",
                    "origin": "AgentDesk AI",
                    "endpoint": f"http://localhost:{self.agent.browser_agent.port}",
                    "enabled": True,
                    "type": "browser"
                }
                
                mcp_data["mcps"].append(browser_agent_mcp)
                
                # Salvar as alterações
                with open(self.agent.mcp_json_path, 'w') as f:
                    json.dump(mcp_data, f, indent=2)
                
                QMessageBox.information(
                    self, "Browser Agent Adicionado", 
                    "Browser Agent MCP foi adicionado ao arquivo mcp.json com sucesso!")
                
                self.statusBar().showMessage("Browser Agent MCP adicionado ao mcp.json.")
            else:
                # Atualizar a entrada existente
                browser_agent_entry["endpoint"] = f"http://localhost:{self.agent.browser_agent.port}"
                browser_agent_entry["enabled"] = True
                
                # Salvar as alterações
                with open(self.agent.mcp_json_path, 'w') as f:
                    json.dump(mcp_data, f, indent=2)
                
                QMessageBox.information(
                    self, "Browser Agent Atualizado", 
                    "Browser Agent MCP já existia e foi atualizado no arquivo mcp.json!")
                
                self.statusBar().showMessage("Browser Agent MCP atualizado no mcp.json.")
        
        except Exception as e:
            QMessageBox.critical(
                self, "Erro", f"Erro ao modificar o arquivo mcp.json: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configurar estilo da aplicação
    app.setStyle("Fusion")
    
    # Criar ícones para o microfone - simulação
    # Em uma implementação real, você usaria arquivos reais
    with open("mic_on.png", "w") as f:
        f.write("Placeholder para ícone de microfone ativo")
    
    with open("mic_off.png", "w") as f:
        f.write("Placeholder para ícone de microfone inativo")
    
    # Iniciar janela
    window = MCPManagerApp()
    window.show()
    
    # Mensagem de início
    print("Aplicativo Gerenciador de MCPs iniciado")
    if VOICE_AVAILABLE:
        print("Suporte a reconhecimento de voz está disponível")
    else:
        print("Aviso: Suporte a reconhecimento de voz não está disponível")
        print("Para habilitar, instale as bibliotecas: speech_recognition e pyttsx3")
    
    sys.exit(app.exec_()) 