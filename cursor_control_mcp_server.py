#!/usr/bin/env python3
"""
Cursor Control MCP Server
Servidor MCP avançado para controlar o Cursor IDE diretamente

Funcionalidades:
- Controle de terminal
- Gerenciamento de prompts e conversas
- Envio de comandos para IA
- Armazenamento de sessões
- Controle de funcionalidades do editor
"""

import asyncio
import json
import os
import platform
import subprocess
import sqlite3
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Dependências MCP básicas (sem dependências externas complexas)
class MCPServer:
    def __init__(self, name: str):
        self.name = name
        self.tools = []
        self.tool_handlers = {}
    
    def list_tools(self):
        def decorator(func):
            self._list_tools_handler = func
            return func
        return decorator
    
    def call_tool(self):
        def decorator(func):
            self._call_tool_handler = func
            return func
        return decorator

class Tool:
    def __init__(self, name: str, description: str, inputSchema: dict):
        self.name = name
        self.description = description
        self.inputSchema = inputSchema

class CallToolResult:
    def __init__(self, content: List[Any]):
        self.content = content

class TextContent:
    def __init__(self, type: str, text: str):
        self.type = type
        self.text = text

class CursorControlMCPServer:
    def __init__(self):
        self.server = MCPServer("cursor-control")
        self.cursor_path = self.find_cursor_executable()
        self.workspace_path = os.getcwd()
        self.conversations_db = self.init_conversations_db()
        self.prompts_db = self.init_prompts_db()
        self.terminal_sessions = {}
        
        # Configuração de caminhos do Cursor
        self.cursor_config_paths = self.get_cursor_config_paths()
        self.cursor_mcp_file = self.find_cursor_mcp_file()
        
        # Registrar ferramentas
        self.register_tools()
    
    def find_cursor_executable(self) -> Optional[str]:
        """Encontra o executável do Cursor no sistema"""
        system = platform.system()
        
        if system == "Windows":
            possible_paths = [
                os.path.expanduser("~/AppData/Local/Programs/cursor/Cursor.exe"),
                "C:/Users/{}/AppData/Local/Programs/cursor/Cursor.exe".format(os.getenv("USERNAME")),
                "cursor.exe"
            ]
        elif system == "Darwin":  # macOS
            possible_paths = [
                "/Applications/Cursor.app/Contents/MacOS/Cursor",
                "/usr/local/bin/cursor",
                "cursor"
            ]
        else:  # Linux
            possible_paths = [
                "/usr/bin/cursor",
                "/usr/local/bin/cursor",
                os.path.expanduser("~/.local/bin/cursor"),
                "cursor"
            ]
        
        for path in possible_paths:
            if os.path.exists(path) or self.command_exists(path):
                return path
        
        return None
    
    def command_exists(self, command: str) -> bool:
        """Verifica se um comando existe no PATH"""
        try:
            subprocess.run([command, "--version"], capture_output=True, timeout=5)
            return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_cursor_config_paths(self) -> List[Path]:
        """Retorna caminhos de configuração do Cursor"""
        system = platform.system()
        home = Path.home()
        
        if system == "Windows":
            return [
                home / "AppData" / "Roaming" / "Cursor" / "User",
                home / "AppData" / "Local" / "Cursor" / "User",
                home / ".cursor"
            ]
        elif system == "Darwin":
            return [
                home / "Library" / "Application Support" / "Cursor" / "User",
                home / ".cursor"
            ]
        else:
            return [
                home / ".config" / "Cursor" / "User",
                home / ".cursor"
            ]
    
    def find_cursor_mcp_file(self) -> Optional[Path]:
        """Encontra o arquivo mcp.json do Cursor"""
        for config_path in self.cursor_config_paths:
            mcp_file = config_path / "mcp.json"
            if mcp_file.exists():
                return mcp_file
        return None
    
    def init_conversations_db(self) -> str:
        """Inicializa banco de dados de conversas"""
        db_path = os.path.join(self.workspace_path, ".cursor", "conversations.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        return db_path
    
    def init_prompts_db(self) -> str:
        """Inicializa banco de dados de prompts"""
        db_path = os.path.join(self.workspace_path, ".cursor", "prompts.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompts (
                id TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                category TEXT,
                tags TEXT,
                created_at TIMESTAMP,
                used_count INTEGER DEFAULT 0,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_usage (
                id TEXT PRIMARY KEY,
                prompt_id TEXT,
                used_at TIMESTAMP,
                context TEXT,
                result TEXT,
                FOREIGN KEY (prompt_id) REFERENCES prompts (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        return db_path
    
    def register_tools(self):
        """Registra todas as ferramentas MCP"""
        
        # Simular decoradores MCP
        self.tools = [
            # Controle de Terminal
            Tool(
                name="execute_terminal_command",
                description="Executa comando no terminal do Cursor",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Comando a ser executado"},
                        "working_directory": {"type": "string", "description": "Diretório de trabalho (opcional)"},
                        "session_id": {"type": "string", "description": "ID da sessão do terminal (opcional)"}
                    },
                    "required": ["command"]
                }
            ),
            Tool(
                name="create_terminal_session",
                description="Cria nova sessão de terminal",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_name": {"type": "string", "description": "Nome da sessão"},
                        "working_directory": {"type": "string", "description": "Diretório inicial"}
                    },
                    "required": ["session_name"]
                }
            ),
            Tool(
                name="list_terminal_sessions",
                description="Lista sessões de terminal ativas",
                inputSchema={"type": "object", "properties": {}}
            ),
            
            # Gerenciamento de Prompts
            Tool(
                name="save_prompt",
                description="Salva um prompt para reutilização",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Título do prompt"},
                        "content": {"type": "string", "description": "Conteúdo do prompt"},
                        "category": {"type": "string", "description": "Categoria do prompt"},
                        "tags": {"type": "string", "description": "Tags separadas por vírgula"}
                    },
                    "required": ["title", "content"]
                }
            ),
            Tool(
                name="search_prompts",
                description="Busca prompts salvos",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Termo de busca"},
                        "category": {"type": "string", "description": "Filtrar por categoria"},
                        "tags": {"type": "string", "description": "Filtrar por tags"}
                    }
                }
            ),
            Tool(
                name="use_prompt",
                description="Usa um prompt salvo",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt_id": {"type": "string", "description": "ID do prompt"},
                        "variables": {"type": "object", "description": "Variáveis para substituição"}
                    },
                    "required": ["prompt_id"]
                }
            ),
            
            # Gerenciamento de Conversas
            Tool(
                name="start_conversation",
                description="Inicia nova conversa com a IA do Cursor",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Título da conversa"},
                        "initial_message": {"type": "string", "description": "Mensagem inicial"},
                        "context": {"type": "object", "description": "Contexto adicional"}
                    },
                    "required": ["title", "initial_message"]
                }
            ),
            Tool(
                name="send_message_to_cursor",
                description="Envia mensagem para a IA do Cursor",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Mensagem para enviar"},
                        "conversation_id": {"type": "string", "description": "ID da conversa"},
                        "mode": {"type": "string", "enum": ["chat", "composer"], "description": "Modo de interação"}
                    },
                    "required": ["message"]
                }
            ),
            Tool(
                name="get_conversation_history",
                description="Recupera histórico de conversa",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "conversation_id": {"type": "string", "description": "ID da conversa"},
                        "limit": {"type": "integer", "description": "Limite de mensagens"}
                    },
                    "required": ["conversation_id"]
                }
            ),
            
            # Controle do Editor
            Tool(
                name="open_file_in_cursor",
                description="Abre arquivo no Cursor",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Caminho do arquivo"},
                        "line_number": {"type": "integer", "description": "Número da linha (opcional)"},
                        "column": {"type": "integer", "description": "Número da coluna (opcional)"}
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="create_file_in_cursor",
                description="Cria novo arquivo no Cursor",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Caminho do novo arquivo"},
                        "content": {"type": "string", "description": "Conteúdo inicial"},
                        "open_after_create": {"type": "boolean", "description": "Abrir após criar"}
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="execute_cursor_command",
                description="Executa comando do Cursor via CLI",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Comando do Cursor"},
                        "args": {"type": "array", "items": {"type": "string"}, "description": "Argumentos"}
                    },
                    "required": ["command"]
                }
            ),
            
            # Configuração e Status
            Tool(
                name="get_cursor_status",
                description="Obtém status do Cursor e MCPs",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="configure_cursor_mcp",
                description="Configura MCP no Cursor",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "server_name": {"type": "string", "description": "Nome do servidor MCP"},
                        "command": {"type": "string", "description": "Comando para executar"},
                        "args": {"type": "array", "items": {"type": "string"}, "description": "Argumentos"},
                        "env": {"type": "object", "description": "Variáveis de ambiente"}
                    },
                    "required": ["server_name", "command"]
                }
            ),
            Tool(
                name="backup_cursor_config",
                description="Faz backup da configuração do Cursor",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "backup_name": {"type": "string", "description": "Nome do backup"}
                    }
                }
            )
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Chama ferramenta específica"""
        try:
            if name == "execute_terminal_command":
                return await self.execute_terminal_command(arguments)
            elif name == "create_terminal_session":
                return await self.create_terminal_session(arguments)
            elif name == "list_terminal_sessions":
                return await self.list_terminal_sessions(arguments)
            elif name == "save_prompt":
                return await self.save_prompt(arguments)
            elif name == "search_prompts":
                return await self.search_prompts(arguments)
            elif name == "use_prompt":
                return await self.use_prompt(arguments)
            elif name == "start_conversation":
                return await self.start_conversation(arguments)
            elif name == "send_message_to_cursor":
                return await self.send_message_to_cursor(arguments)
            elif name == "get_conversation_history":
                return await self.get_conversation_history(arguments)
            elif name == "open_file_in_cursor":
                return await self.open_file_in_cursor(arguments)
            elif name == "create_file_in_cursor":
                return await self.create_file_in_cursor(arguments)
            elif name == "execute_cursor_command":
                return await self.execute_cursor_command(arguments)
            elif name == "get_cursor_status":
                return await self.get_cursor_status(arguments)
            elif name == "configure_cursor_mcp":
                return await self.configure_cursor_mcp(arguments)
            elif name == "backup_cursor_config":
                return await self.backup_cursor_config(arguments)
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Ferramenta desconhecida: {name}")]
                )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao executar {name}: {str(e)}")]
            )
    
    # Implementação das ferramentas
    
    async def execute_terminal_command(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Executa comando no terminal"""
        command = arguments["command"]
        working_directory = arguments.get("working_directory", self.workspace_path)
        session_id = arguments.get("session_id")
        
        try:
            if session_id and session_id in self.terminal_sessions:
                # Usar sessão existente
                process = self.terminal_sessions[session_id]["process"]
                process.stdin.write(f"{command}\n".encode())
                process.stdin.flush()
                
                # Aguardar saída (timeout de 10 segundos)
                await asyncio.sleep(1)
                output = ""
                if process.stdout.readable():
                    data = process.stdout.read(8192)
                    if data:
                        output = data.decode('utf-8', errors='ignore')
            else:
                # Executar comando único
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=working_directory,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                output = f"Exit code: {result.returncode}\n"
                output += f"STDOUT:\n{result.stdout}\n"
                if result.stderr:
                    output += f"STDERR:\n{result.stderr}\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=output)]
            )
            
        except subprocess.TimeoutExpired:
            return CallToolResult(
                content=[TextContent(type="text", text="Comando expirou (timeout 30s)")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao executar comando: {str(e)}")]
            )
    
    async def create_terminal_session(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Cria nova sessão de terminal"""
        session_name = arguments["session_name"]
        working_directory = arguments.get("working_directory", self.workspace_path)
        
        try:
            # Criar processo de terminal persistente
            if platform.system() == "Windows":
                process = subprocess.Popen(
                    ["cmd"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    cwd=working_directory,
                    text=True
                )
            else:
                process = subprocess.Popen(
                    ["/bin/bash"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    cwd=working_directory,
                    text=True
                )
            
            session_id = str(uuid.uuid4())
            self.terminal_sessions[session_id] = {
                "name": session_name,
                "process": process,
                "created_at": datetime.now(),
                "working_directory": working_directory
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=f"Sessão de terminal criada: {session_name} (ID: {session_id})"
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao criar sessão: {str(e)}")]
            )
    
    async def list_terminal_sessions(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Lista sessões de terminal ativas"""
        if not self.terminal_sessions:
            return CallToolResult(
                content=[TextContent(type="text", text="Nenhuma sessão de terminal ativa")]
            )
        
        sessions_info = []
        for session_id, session in self.terminal_sessions.items():
            status = "ativo" if session["process"].poll() is None else "finalizado"
            sessions_info.append(
                f"ID: {session_id}\n"
                f"Nome: {session['name']}\n"
                f"Status: {status}\n"
                f"Criado: {session['created_at']}\n"
                f"Diretório: {session['working_directory']}\n"
            )
        
        return CallToolResult(
            content=[TextContent(type="text", text="\n".join(sessions_info))]
        )
    
    async def save_prompt(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Salva um prompt para reutilização"""
        title = arguments["title"]
        content = arguments["content"]
        category = arguments.get("category", "general")
        tags = arguments.get("tags", "")
        
        try:
            conn = sqlite3.connect(self.prompts_db)
            cursor = conn.cursor()
            
            prompt_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO prompts (id, title, content, category, tags, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (prompt_id, title, content, category, tags, datetime.now(), "{}"))
            
            conn.commit()
            conn.close()
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Prompt salvo com ID: {prompt_id}")]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao salvar prompt: {str(e)}")]
            )
    
    async def search_prompts(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Busca prompts salvos"""
        query = arguments.get("query", "")
        category = arguments.get("category")
        tags = arguments.get("tags")
        
        try:
            conn = sqlite3.connect(self.prompts_db)
            cursor = conn.cursor()
            
            sql = "SELECT id, title, content, category, tags, used_count FROM prompts WHERE 1=1"
            params = []
            
            if query:
                sql += " AND (title LIKE ? OR content LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            if category:
                sql += " AND category = ?"
                params.append(category)
            
            if tags:
                sql += " AND tags LIKE ?"
                params.append(f"%{tags}%")
            
            sql += " ORDER BY used_count DESC, created_at DESC"
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return CallToolResult(
                    content=[TextContent(type="text", text="Nenhum prompt encontrado")]
                )
            
            prompts_info = []
            for row in results:
                prompts_info.append(
                    f"ID: {row[0]}\n"
                    f"Título: {row[1]}\n"
                    f"Categoria: {row[3]}\n"
                    f"Tags: {row[4]}\n"
                    f"Usado: {row[5]} vezes\n"
                    f"Conteúdo: {row[2][:100]}...\n"
                )
            
            return CallToolResult(
                content=[TextContent(type="text", text="\n---\n".join(prompts_info))]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao buscar prompts: {str(e)}")]
            )
    
    async def use_prompt(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Usa um prompt salvo"""
        prompt_id = arguments["prompt_id"]
        variables = arguments.get("variables", {})
        
        try:
            conn = sqlite3.connect(self.prompts_db)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT content, title FROM prompts WHERE id = ?", 
                (prompt_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return CallToolResult(
                    content=[TextContent(type="text", text="Prompt não encontrado")]
                )
            
            content, title = result
            
            # Substituir variáveis no conteúdo
            for key, value in variables.items():
                content = content.replace(f"{{{key}}}", str(value))
            
            # Atualizar contador de uso
            cursor.execute(
                "UPDATE prompts SET used_count = used_count + 1 WHERE id = ?",
                (prompt_id,)
            )
            
            # Registrar uso
            cursor.execute("""
                INSERT INTO prompt_usage (id, prompt_id, used_at, context, result)
                VALUES (?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), prompt_id, datetime.now(), json.dumps(variables), ""))
            
            conn.commit()
            conn.close()
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=f"Prompt '{title}' carregado:\n\n{content}"
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao usar prompt: {str(e)}")]
            )
    
    async def start_conversation(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Inicia nova conversa com a IA do Cursor"""
        title = arguments["title"]
        initial_message = arguments["initial_message"]
        context = arguments.get("context", {})
        
        try:
            conn = sqlite3.connect(self.conversations_db)
            cursor = conn.cursor()
            
            conversation_id = str(uuid.uuid4())
            now = datetime.now()
            
            # Criar conversa
            cursor.execute("""
                INSERT INTO conversations (id, title, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (conversation_id, title, now, now, json.dumps(context)))
            
            # Adicionar mensagem inicial
            message_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO messages (id, conversation_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (message_id, conversation_id, "user", initial_message, now, "{}"))
            
            conn.commit()
            conn.close()
            
            # Tentar enviar para o Cursor se disponível
            cursor_response = await self._send_to_cursor_ai(initial_message, conversation_id)
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=f"Conversa iniciada (ID: {conversation_id})\n"
                         f"Título: {title}\n"
                         f"Mensagem inicial enviada.\n"
                         f"Resposta do Cursor: {cursor_response}"
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao iniciar conversa: {str(e)}")]
            )
    
    async def send_message_to_cursor(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Envia mensagem para a IA do Cursor"""
        message = arguments["message"]
        conversation_id = arguments.get("conversation_id")
        mode = arguments.get("mode", "chat")
        
        try:
            # Salvar mensagem no banco se há conversation_id
            if conversation_id:
                conn = sqlite3.connect(self.conversations_db)
                cursor = conn.cursor()
                
                message_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO messages (id, conversation_id, role, content, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (message_id, conversation_id, "user", message, datetime.now(), json.dumps({"mode": mode})))
                
                conn.commit()
                conn.close()
            
            # Enviar para o Cursor
            response = await self._send_to_cursor_ai(message, conversation_id, mode)
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Mensagem enviada para Cursor.\nResposta: {response}")]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao enviar mensagem: {str(e)}")]
            )
    
    async def _send_to_cursor_ai(self, message: str, conversation_id: Optional[str] = None, mode: str = "chat") -> str:
        """Envia mensagem para a IA do Cursor (implementação via CLI ou API)"""
        if not self.cursor_path:
            return "Cursor não encontrado no sistema"
        
        try:
            # Tentar usar CLI do Cursor para enviar comando
            if mode == "composer":
                # Usar Composer mode
                cmd = [self.cursor_path, "--composer", message]
            else:
                # Usar Chat mode
                cmd = [self.cursor_path, "--chat", message]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.workspace_path
            )
            
            if result.returncode == 0:
                response = result.stdout.strip() or "Comando enviado com sucesso"
            else:
                response = f"Erro: {result.stderr}"
            
            # Salvar resposta no banco se há conversation_id
            if conversation_id:
                conn = sqlite3.connect(self.conversations_db)
                cursor = conn.cursor()
                
                message_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO messages (id, conversation_id, role, content, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (message_id, conversation_id, "assistant", response, datetime.now(), "{}"))
                
                conn.commit()
                conn.close()
            
            return response
            
        except subprocess.TimeoutExpired:
            return "Timeout ao comunicar com Cursor"
        except Exception as e:
            return f"Erro na comunicação: {str(e)}"
    
    async def get_conversation_history(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Recupera histórico de conversa"""
        conversation_id = arguments["conversation_id"]
        limit = arguments.get("limit", 50)
        
        try:
            conn = sqlite3.connect(self.conversations_db)
            cursor = conn.cursor()
            
            # Buscar informações da conversa
            cursor.execute(
                "SELECT title, created_at, metadata FROM conversations WHERE id = ?",
                (conversation_id,)
            )
            conv_info = cursor.fetchone()
            
            if not conv_info:
                conn.close()
                return CallToolResult(
                    content=[TextContent(type="text", text="Conversa não encontrada")]
                )
            
            # Buscar mensagens
            cursor.execute("""
                SELECT role, content, timestamp FROM messages 
                WHERE conversation_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (conversation_id, limit))
            
            messages = cursor.fetchall()
            conn.close()
            
            # Formatar histórico
            history = f"Conversa: {conv_info[0]}\n"
            history += f"Criada em: {conv_info[1]}\n\n"
            
            for role, content, timestamp in reversed(messages):
                history += f"[{timestamp}] {role.upper()}: {content}\n\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=history)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao recuperar histórico: {str(e)}")]
            )
    
    async def open_file_in_cursor(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Abre arquivo no Cursor"""
        file_path = arguments["file_path"]
        line_number = arguments.get("line_number")
        column = arguments.get("column")
        
        try:
            if not self.cursor_path:
                return CallToolResult(
                    content=[TextContent(type="text", text="Cursor não encontrado")]
                )
            
            # Construir comando
            cmd = [self.cursor_path, file_path]
            
            if line_number:
                if column:
                    cmd.extend(["-g", f"{line_number}:{column}"])
                else:
                    cmd.extend(["-g", str(line_number)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Arquivo aberto: {file_path}")]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Erro ao abrir arquivo: {result.stderr}")]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao abrir arquivo: {str(e)}")]
            )
    
    async def create_file_in_cursor(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Cria novo arquivo no Cursor"""
        file_path = arguments["file_path"]
        content = arguments.get("content", "")
        open_after_create = arguments.get("open_after_create", True)
        
        try:
            # Criar diretório se necessário
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Escrever arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Abrir no Cursor se solicitado
            if open_after_create and self.cursor_path:
                subprocess.run([self.cursor_path, file_path], timeout=10)
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Arquivo criado e aberto: {file_path}")]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Arquivo criado: {file_path}")]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao criar arquivo: {str(e)}")]
            )
    
    async def execute_cursor_command(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Executa comando do Cursor via CLI"""
        command = arguments["command"]
        args = arguments.get("args", [])
        
        try:
            if not self.cursor_path:
                return CallToolResult(
                    content=[TextContent(type="text", text="Cursor não encontrado")]
                )
            
            cmd = [self.cursor_path, f"--{command}"] + args
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            output = f"Exit code: {result.returncode}\n"
            if result.stdout:
                output += f"Output: {result.stdout}\n"
            if result.stderr:
                output += f"Error: {result.stderr}\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=output)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao executar comando: {str(e)}")]
            )
    
    async def get_cursor_status(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Obtém status do Cursor e MCPs"""
        try:
            status = {
                "cursor_path": self.cursor_path,
                "cursor_found": self.cursor_path is not None,
                "workspace_path": self.workspace_path,
                "mcp_file": str(self.cursor_mcp_file) if self.cursor_mcp_file else None,
                "terminal_sessions": len(self.terminal_sessions),
                "conversations_db": os.path.exists(self.conversations_db),
                "prompts_db": os.path.exists(self.prompts_db)
            }
            
            # Verificar MCPs configurados
            if self.cursor_mcp_file and self.cursor_mcp_file.exists():
                with open(self.cursor_mcp_file, 'r') as f:
                    mcp_config = json.load(f)
                    status["mcp_servers"] = list(mcp_config.get("mcpServers", {}).keys())
            else:
                status["mcp_servers"] = []
            
            # Verificar se Cursor está rodando
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(
                        ["tasklist", "/FI", "IMAGENAME eq Cursor.exe"],
                        capture_output=True, text=True
                    )
                    status["cursor_running"] = "Cursor.exe" in result.stdout
                else:
                    result = subprocess.run(
                        ["pgrep", "-f", "cursor"],
                        capture_output=True, text=True
                    )
                    status["cursor_running"] = bool(result.stdout.strip())
            except:
                status["cursor_running"] = "unknown"
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(status, indent=2))]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao obter status: {str(e)}")]
            )
    
    async def configure_cursor_mcp(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Configura MCP no Cursor"""
        server_name = arguments["server_name"]
        command = arguments["command"]
        args = arguments.get("args", [])
        env = arguments.get("env", {})
        
        try:
            # Ler configuração atual
            config = {"mcpServers": {}}
            
            if self.cursor_mcp_file and self.cursor_mcp_file.exists():
                with open(self.cursor_mcp_file, 'r') as f:
                    config = json.load(f)
            
            # Adicionar/atualizar servidor
            config["mcpServers"][server_name] = {
                "command": command,
                "args": args,
                "env": env
            }
            
            # Criar diretório se necessário
            if not self.cursor_mcp_file:
                # Usar primeiro caminho disponível
                mcp_path = self.cursor_config_paths[0] / "mcp.json"
                mcp_path.parent.mkdir(parents=True, exist_ok=True)
                self.cursor_mcp_file = mcp_path
            
            # Salvar configuração
            with open(self.cursor_mcp_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=f"MCP '{server_name}' configurado em {self.cursor_mcp_file}"
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao configurar MCP: {str(e)}")]
            )
    
    async def backup_cursor_config(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Faz backup da configuração do Cursor"""
        backup_name = arguments.get("backup_name", f"cursor_backup_{int(time.time())}")
        
        try:
            backup_dir = Path(self.workspace_path) / ".cursor" / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_file = backup_dir / f"{backup_name}.json"
            
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "cursor_path": self.cursor_path,
                "workspace_path": self.workspace_path,
                "mcp_config": None,
                "config_paths": [str(p) for p in self.cursor_config_paths]
            }
            
            # Incluir configuração MCP se existir
            if self.cursor_mcp_file and self.cursor_mcp_file.exists():
                with open(self.cursor_mcp_file, 'r') as f:
                    backup_data["mcp_config"] = json.load(f)
            
            # Salvar backup
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=f"Backup criado: {backup_file}"
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erro ao criar backup: {str(e)}")]
            )

# Função principal para executar o servidor
def main():
    """Função principal do servidor MCP"""
    import json
    import sys
    
    server = CursorControlMCPServer()
    
    # Simular protocolo MCP básico via stdin/stdout
    print("Cursor Control MCP Server iniciado", file=sys.stderr)
    
    try:
        while True:
            line = input()
            if not line:
                break
            
            try:
                request = json.loads(line)
                
                if request.get("method") == "tools/list":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "tools": [
                                {
                                    "name": tool.name,
                                    "description": tool.description,
                                    "inputSchema": tool.inputSchema
                                }
                                for tool in server.tools
                            ]
                        }
                    }
                    print(json.dumps(response))
                
                elif request.get("method") == "tools/call":
                    params = request.get("params", {})
                    name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    # Executar ferramenta de forma síncrona
                    import asyncio
                    result = asyncio.run(server.call_tool(name, arguments))
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "content": [
                                {
                                    "type": content.type,
                                    "text": content.text
                                }
                                for content in result.content
                            ]
                        }
                    }
                    print(json.dumps(response))
                
                else:
                    # Método não suportado
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": "Method not found"
                        }
                    }
                    print(json.dumps(response))
                    
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Erro: {e}", file=sys.stderr)
                
    except KeyboardInterrupt:
        print("Servidor MCP finalizado", file=sys.stderr)
    except EOFError:
        pass

if __name__ == "__main__":
    main() 