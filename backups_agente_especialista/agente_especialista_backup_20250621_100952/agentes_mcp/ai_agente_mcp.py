#!/usr/bin/env python3
"""
AiAgenteMCP - Agente MCP Inteligente Aprimorado
Integração com OpenRouter, múltiplos modelos e funcionalidades avançadas
"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import threading
import time

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_agent_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuração de modelo de IA"""
    name: str
    provider: str
    api_key: str
    base_url: str
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    is_free: bool = False

@dataclass
class AgentResponse:
    """Resposta do agente"""
    content: str
    model_used: str
    tokens_used: int
    response_time: float
    success: bool
    error_message: Optional[str] = None

class OpenRouterClient:
    """Cliente para integração com OpenRouter"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ailocal.com",
            "X-Title": "AILocal Agent"
        })
        
        # Modelos disponíveis (free e premium)
        self.free_models = [
            "google/gemini-1.5-flash",
            "meta-llama/llama-3-8b-instruct",
            "microsoft/phi-3-mini",
            "nousresearch/nous-hermes-2-mixtral-8x7b-dpo",
            "openchat/openchat-3.5",
            "qwen/qwen2.5-7b-instruct",
            "snowflake/snowflake-arctic-instruct"
        ]
        
        self.premium_models = [
            "anthropic/claude-3-opus",
            "anthropic/claude-3-sonnet",
            "anthropic/claude-3-haiku",
            "google/gemini-pro",
            "google/gemini-1.5-pro",
            "mistralai/mistral-large",
            "mistralai/mistral-medium",
            "meta-llama/llama-3-70b-instruct",
            "openai/gpt-4-turbo",
            "openai/gpt-4o",
            "openai/gpt-3.5-turbo",
            "deepseek/deepseek-coder",
            "cohere/command-r-plus"
        ]
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Retorna todos os modelos disponíveis"""
        return {
            "free": self.free_models,
            "premium": self.premium_models,
            "all": self.free_models + self.premium_models
        }
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       model: str = "anthropic/claude-3-opus",
                       max_tokens: int = 4096,
                       temperature: float = 0.7) -> AgentResponse:
        """Envia mensagem para o modelo via OpenRouter"""
        start_time = time.time()
        
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                tokens_used = data['usage']['total_tokens']
                
                return AgentResponse(
                    content=content,
                    model_used=model,
                    tokens_used=tokens_used,
                    response_time=time.time() - start_time,
                    success=True
                )
            else:
                return AgentResponse(
                    content="",
                    model_used=model,
                    tokens_used=0,
                    response_time=time.time() - start_time,
                    success=False,
                    error_message=f"API Error: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            logger.error(f"Erro na comunicação com OpenRouter: {e}")
            return AgentResponse(
                content="",
                model_used=model,
                tokens_used=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )

class MCPTools:
    """Ferramentas MCP disponíveis para o agente"""
    
    def __init__(self):
        self.tools = {
            "file_system": self.file_system_tools,
            "terminal": self.terminal_tools,
            "web_browser": self.web_browser_tools,
            "database": self.database_tools,
            "git": self.git_tools
        }
    
    def file_system_tools(self) -> Dict[str, Any]:
        """Ferramentas do sistema de arquivos"""
        return {
            "read_file": {
                "description": "Lê conteúdo de um arquivo",
                "parameters": {"path": "string"}
            },
            "write_file": {
                "description": "Escreve conteúdo em um arquivo",
                "parameters": {"path": "string", "content": "string"}
            },
            "list_directory": {
                "description": "Lista conteúdo de um diretório",
                "parameters": {"path": "string"}
            },
            "create_directory": {
                "description": "Cria um novo diretório",
                "parameters": {"path": "string"}
            },
            "delete_file": {
                "description": "Deleta um arquivo",
                "parameters": {"path": "string"}
            }
        }
    
    def terminal_tools(self) -> Dict[str, Any]:
        """Ferramentas do terminal"""
        return {
            "execute_command": {
                "description": "Executa um comando no terminal",
                "parameters": {"command": "string", "working_directory": "string"}
            },
            "get_process_list": {
                "description": "Lista processos em execução",
                "parameters": {}
            },
            "kill_process": {
                "description": "Mata um processo",
                "parameters": {"pid": "integer"}
            }
        }
    
    def web_browser_tools(self) -> Dict[str, Any]:
        """Ferramentas do navegador web"""
        return {
            "navigate": {
                "description": "Navega para uma URL",
                "parameters": {"url": "string"}
            },
            "take_screenshot": {
                "description": "Captura screenshot da página atual",
                "parameters": {"filename": "string"}
            },
            "execute_script": {
                "description": "Executa JavaScript na página",
                "parameters": {"script": "string"}
            },
            "get_page_content": {
                "description": "Obtém conteúdo da página atual",
                "parameters": {}
            }
        }
    
    def database_tools(self) -> Dict[str, Any]:
        """Ferramentas de banco de dados"""
        return {
            "connect": {
                "description": "Conecta a um banco de dados",
                "parameters": {"connection_string": "string"}
            },
            "execute_query": {
                "description": "Executa uma query SQL",
                "parameters": {"query": "string"}
            },
            "get_tables": {
                "description": "Lista tabelas do banco",
                "parameters": {}
            }
        }
    
    def git_tools(self) -> Dict[str, Any]:
        """Ferramentas Git"""
        return {
            "clone": {
                "description": "Clona um repositório",
                "parameters": {"url": "string", "path": "string"}
            },
            "commit": {
                "description": "Faz commit das mudanças",
                "parameters": {"message": "string"}
            },
            "push": {
                "description": "Faz push das mudanças",
                "parameters": {}
            },
            "pull": {
                "description": "Faz pull das mudanças",
                "parameters": {}
            },
            "status": {
                "description": "Mostra status do repositório",
                "parameters": {}
            }
        }

class AiAgenteMCP:
    """Agente MCP Inteligente Principal"""
    
    def __init__(self, config_file: str = "config/agent_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
        # Inicializar clientes de API
        self.openrouter_client = None
        if self.config.get("openrouter_api_key"):
            self.openrouter_client = OpenRouterClient(self.config["openrouter_api_key"])
        
        # Ferramentas MCP
        self.mcp_tools = MCPTools()
        
        # Estado do agente
        self.conversation_history = []
        self.current_model = self.config.get("default_model", "anthropic/claude-3-opus")
        self.agent_mode = self.config.get("agent_mode", "assistant")
        
        # Cache para respostas
        self.response_cache = {}
        
        # Threading para operações assíncronas
        self.lock = threading.Lock()
        
        logger.info("AiAgenteMCP inicializado com sucesso")
    
    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Configuração padrão
                default_config = {
                    "openrouter_api_key": "",
                    "default_model": "anthropic/claude-3-opus",
                    "agent_mode": "assistant",
                    "max_tokens": 4096,
                    "temperature": 0.7,
                    "timeout": 30,
                    "voice_enabled": False,
                    "browser_agent_enabled": False,
                    "cache_enabled": True,
                    "cache_ttl": 3600
                }
                
                # Criar diretório de configuração se não existir
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                
                # Salvar configuração padrão
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
                
                return default_config
                
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return {}
    
    def save_config(self):
        """Salva configuração atual"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
    
    def update_config(self, key: str, value: Any):
        """Atualiza uma configuração específica"""
        self.config[key] = value
        self.save_config()
    
    def get_available_models(self) -> Dict[str, Any]:
        """Retorna modelos disponíveis"""
        if self.openrouter_client:
            return self.openrouter_client.get_available_models()
        return {"error": "OpenRouter não configurado"}
    
    def switch_model(self, model_name: str) -> bool:
        """Muda o modelo atual"""
        if self.openrouter_client:
            available_models = self.openrouter_client.get_available_models()
            if model_name in available_models["all"]:
                self.current_model = model_name
                self.update_config("default_model", model_name)
                logger.info(f"Modelo alterado para: {model_name}")
                return True
        return False
    
    def switch_mode(self, mode: str) -> bool:
        """Muda o modo do agente"""
        valid_modes = ["assistant", "developer", "analyst", "creative"]
        if mode in valid_modes:
            self.agent_mode = mode
            self.update_config("agent_mode", mode)
            logger.info(f"Modo alterado para: {mode}")
            return True
        return False
    
    def add_to_history(self, role: str, content: str):
        """Adiciona mensagem ao histórico"""
        with self.lock:
            self.conversation_history.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            
            # Manter apenas as últimas 50 mensagens
            if len(self.conversation_history) > 50:
                self.conversation_history = self.conversation_history[-50:]
    
    def get_context_prompt(self) -> str:
        """Gera prompt de contexto baseado no modo atual"""
        base_prompt = f"""Você é um agente MCP inteligente operando no modo '{self.agent_mode}'.
        
        Modo atual: {self.agent_mode}
        
        Capacidades disponíveis:
        - Sistema de arquivos (leitura, escrita, listagem)
        - Terminal (execução de comandos)
        - Navegador web (navegação, screenshots, execução de scripts)
        - Banco de dados (consultas SQL)
        - Git (controle de versão)
        
        Instruções específicas do modo:
        """
        
        mode_instructions = {
            "assistant": "Seja útil e prestativo. Responda perguntas de forma clara e concisa.",
            "developer": "Foque em desenvolvimento de software. Gere código, debugue problemas, sugira melhorias.",
            "analyst": "Analise dados e informações. Gere relatórios, identifique padrões e tendências.",
            "creative": "Seja criativo e artístico. Gere conteúdo original, ideias inovadoras e soluções criativas."
        }
        
        return base_prompt + mode_instructions.get(self.agent_mode, "")
    
    def process_message(self, message: str, use_cache: bool = True) -> AgentResponse:
        """Processa uma mensagem e retorna resposta do agente"""
        start_time = time.time()
        
        # Verificar cache
        if use_cache and self.config.get("cache_enabled", True):
            cache_key = f"{self.current_model}:{message}"
            if cache_key in self.response_cache:
                cached_response = self.response_cache[cache_key]
                if time.time() - cached_response["timestamp"] < self.config.get("cache_ttl", 3600):
                    logger.info("Resposta obtida do cache")
                    return AgentResponse(
                        content=cached_response["content"],
                        model_used=self.current_model,
                        tokens_used=cached_response["tokens_used"],
                        response_time=time.time() - start_time,
                        success=True
                    )
        
        # Adicionar mensagem ao histórico
        self.add_to_history("user", message)
        
        # Preparar mensagens para o modelo
        messages = [
            {"role": "system", "content": self.get_context_prompt()}
        ]
        
        # Adicionar histórico recente (últimas 10 mensagens)
        recent_history = self.conversation_history[-10:]
        for msg in recent_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Obter resposta do modelo
        if self.openrouter_client:
            response = self.openrouter_client.chat_completion(
                messages=messages,
                model=self.current_model,
                max_tokens=self.config.get("max_tokens", 4096),
                temperature=self.config.get("temperature", 0.7)
            )
            
            if response.success:
                # Adicionar resposta ao histórico
                self.add_to_history("assistant", response.content)
                
                # Salvar no cache
                if use_cache and self.config.get("cache_enabled", True):
                    cache_key = f"{self.current_model}:{message}"
                    self.response_cache[cache_key] = {
                        "content": response.content,
                        "tokens_used": response.tokens_used,
                        "timestamp": time.time()
                    }
                
                logger.info(f"Resposta gerada com sucesso usando {self.current_model}")
                return response
            else:
                logger.error(f"Erro ao gerar resposta: {response.error_message}")
                return response
        else:
            error_msg = "OpenRouter não configurado. Configure a API key primeiro."
            logger.error(error_msg)
            return AgentResponse(
                content=error_msg,
                model_used=self.current_model,
                tokens_used=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=error_msg
            )
    
    def execute_tool(self, tool_category: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma ferramenta MCP específica"""
        try:
            if tool_category not in self.mcp_tools.tools:
                return {"success": False, "error": f"Categoria de ferramenta '{tool_category}' não encontrada"}
            
            tools = self.mcp_tools.tools[tool_category]()
            if tool_name not in tools:
                return {"success": False, "error": f"Ferramenta '{tool_name}' não encontrada em '{tool_category}'"}
            
            # Aqui você implementaria a execução real das ferramentas
            # Por enquanto, retornamos uma resposta simulada
            logger.info(f"Executando ferramenta: {tool_category}.{tool_name} com parâmetros: {parameters}")
            
            return {
                "success": True,
                "result": f"Ferramenta {tool_name} executada com sucesso",
                "parameters": parameters
            }
            
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta: {e}")
            return {"success": False, "error": str(e)}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Retorna status atual do agente"""
        return {
            "model": self.current_model,
            "mode": self.agent_mode,
            "conversation_length": len(self.conversation_history),
            "openrouter_configured": self.openrouter_client is not None,
            "config_file": self.config_file,
            "cache_enabled": self.config.get("cache_enabled", True),
            "voice_enabled": self.config.get("voice_enabled", False),
            "browser_agent_enabled": self.config.get("browser_agent_enabled", False)
        }
    
    def clear_history(self):
        """Limpa o histórico de conversa"""
        with self.lock:
            self.conversation_history.clear()
        logger.info("Histórico de conversa limpo")
    
    def export_conversation(self, filepath: str) -> bool:
        """Exporta conversa para arquivo"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
            logger.info(f"Conversa exportada para: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao exportar conversa: {e}")
            return False
    
    def import_conversation(self, filepath: str) -> bool:
        """Importa conversa de arquivo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_history = json.load(f)
            
            with self.lock:
                self.conversation_history = imported_history
            
            logger.info(f"Conversa importada de: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao importar conversa: {e}")
            return False

# Função principal para teste
def main():
    """Função principal para teste do agente"""
    print("=== AiAgenteMCP - Teste de Funcionalidades ===\n")
    
    # Criar instância do agente
    agent = AiAgenteMCP()
    
    # Mostrar status inicial
    print("Status inicial:")
    print(json.dumps(agent.get_agent_status(), indent=2))
    print()
    
    # Mostrar modelos disponíveis
    print("Modelos disponíveis:")
    models = agent.get_available_models()
    print(json.dumps(models, indent=2))
    print()
    
    # Teste de processamento de mensagem (se OpenRouter estiver configurado)
    if agent.openrouter_client:
        print("Testando processamento de mensagem...")
        response = agent.process_message("Olá! Como você pode me ajudar hoje?")
        print(f"Resposta: {response.content}")
        print(f"Modelo usado: {response.model_used}")
        print(f"Tokens usados: {response.tokens_used}")
        print(f"Tempo de resposta: {response.response_time:.2f}s")
        print(f"Sucesso: {response.success}")
        if not response.success:
            print(f"Erro: {response.error_message}")
    else:
        print("OpenRouter não configurado. Configure a API key para testar.")
    
    print("\n=== Teste concluído ===")

if __name__ == "__main__":
    main() 