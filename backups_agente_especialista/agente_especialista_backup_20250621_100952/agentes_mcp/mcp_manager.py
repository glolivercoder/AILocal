#!/usr/bin/env python3
"""
Gerenciador de MCPs para Cursor
Instalação, controle de sessões e integração com Ollama
Suporte para instalação via npm e GitHub
"""

import os
import json
import subprocess
import threading
import time
import logging
import requests
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import platform
import tempfile
import shutil

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPConfig:
    """Configuração de um MCP"""
    name: str
    package: str
    command: str
    port: int
    description: str
    category: str
    enabled: bool = False
    process: Optional[subprocess.Popen] = None
    status: str = "stopped"
    github_url: Optional[str] = None
    installation_method: str = "npm"  # "npm" ou "github"

class GitHubMCPInstaller:
    """Instalador de MCPs via GitHub"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_api_base = "https://api.github.com"
        self.temp_dir = Path(tempfile.gettempdir()) / "mcp_installer"
        self.temp_dir.mkdir(exist_ok=True)
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        
        # Headers para API
        self.headers = {}
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
            logger.info("GitHub token configurado")
        else:
            logger.warning("GitHub token não configurado - rate limit reduzido")
    
    def search_mcp_on_github(self, mcp_name: str) -> List[Dict[str, Any]]:
        """Busca MCPs no GitHub"""
        try:
            # Buscar repositórios relacionados a MCP
            search_queries = [
                f"{mcp_name} mcp server",
                f"modelcontextprotocol {mcp_name}",
                f"mcp-server-{mcp_name}",
                f"{mcp_name} protocol server"
            ]
            
            results = []
            for query in search_queries:
                url = f"{self.github_api_base}/search/repositories"
                params = {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 10
                }
                
                response = requests.get(url, params=params, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    for repo in data.get("items", []):
                        # Verificar se é um MCP válido
                        if self._is_valid_mcp_repo(repo):
                            results.append({
                                "name": repo["name"],
                                "full_name": repo["full_name"],
                                "description": repo["description"],
                                "html_url": repo["html_url"],
                                "clone_url": repo["clone_url"],
                                "stars": repo["stargazers_count"],
                                "language": repo["language"],
                                "updated_at": repo["updated_at"]
                            })
                elif response.status_code == 403:
                    logger.error("Rate limit excedido. Configure GITHUB_TOKEN para aumentar o limite.")
                    break
                else:
                    logger.warning(f"Erro na busca: {response.status_code}")
            
            # Remover duplicatas e ordenar por estrelas
            unique_results = {}
            for result in results:
                key = result["full_name"]
                if key not in unique_results or result["stars"] > unique_results[key]["stars"]:
                    unique_results[key] = result
            
            return sorted(unique_results.values(), key=lambda x: x["stars"], reverse=True)
            
        except Exception as e:
            logger.error(f"Erro ao buscar no GitHub: {e}")
            return []
    
    def _is_valid_mcp_repo(self, repo: Dict[str, Any]) -> bool:
        """Verifica se um repositório é um MCP válido"""
        try:
            # Verificar se tem package.json
            package_url = f"{self.github_api_base}/repos/{repo['full_name']}/contents/package.json"
            response = requests.get(package_url, timeout=5)
            
            if response.status_code == 200:
                package_data = response.json()
                if "content" in package_data:
                    import base64
                    content = base64.b64decode(package_data["content"]).decode()
                    package_json = json.loads(content)
                    
                    # Verificar se tem scripts de MCP
                    scripts = package_json.get("scripts", {})
                    return any("mcp" in script.lower() for script in scripts.keys())
            
            return False
            
        except Exception:
            return False
    
    def install_from_github(self, repo_url: str, mcp_name: str) -> bool:
        """Instala MCP diretamente do GitHub"""
        try:
            logger.info(f"Instalando MCP {mcp_name} do GitHub: {repo_url}")
            
            # Criar diretório temporário
            install_dir = self.temp_dir / mcp_name
            if install_dir.exists():
                shutil.rmtree(install_dir)
            install_dir.mkdir(parents=True)
            
            # Clonar repositório
            clone_cmd = f"git clone {repo_url} {install_dir}"
            process = subprocess.run(clone_cmd, shell=True, capture_output=True, text=True)
            
            if process.returncode != 0:
                logger.error(f"Erro ao clonar repositório: {process.stderr}")
                return False
            
            # Verificar se tem package.json
            package_json_path = install_dir / "package.json"
            if not package_json_path.exists():
                logger.error("package.json não encontrado")
                return False
            
            # Instalar dependências
            install_cmd = f"cd {install_dir} && npm install"
            process = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
            
            if process.returncode != 0:
                logger.error(f"Erro ao instalar dependências: {process.stderr}")
                return False
            
            # Instalar globalmente
            global_install_cmd = f"cd {install_dir} && npm install -g ."
            process = subprocess.run(global_install_cmd, shell=True, capture_output=True, text=True)
            
            if process.returncode == 0:
                logger.info(f"MCP {mcp_name} instalado com sucesso do GitHub")
                return True
            else:
                logger.error(f"Erro na instalação global: {process.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao instalar do GitHub: {e}")
            return False
    
    def get_github_mcp_info(self, repo_url: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de um MCP no GitHub"""
        try:
            # Extrair owner/repo da URL
            match = re.search(r"github\.com/([^/]+/[^/]+)", repo_url)
            if not match:
                return None
            
            repo_path = match.group(1)
            url = f"{self.github_api_base}/repos/{repo_path}"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                repo = response.json()
                return {
                    "name": repo["name"],
                    "description": repo["description"],
                    "stars": repo["stargazers_count"],
                    "language": repo["language"],
                    "clone_url": repo["clone_url"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do GitHub: {e}")
            return None

class OllamaManager:
    """Gerenciador de modelos Ollama para Ryzen 5600"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.base_url = f"{ollama_url}/api"
        
        # Modelos otimizados para Ryzen 5600 (CPU only)
        self.recommended_models = {
            "llama3.2-3b": {
                "name": "llama3.2:3b",
                "description": "Llama 3.2 3B - Rápido e eficiente",
                "size": "1.8GB",
                "performance": "Muito bom para Ryzen 5600",
                "use_case": "Chat geral, código simples"
            },
            "llama3.2-7b": {
                "name": "llama3.2:7b", 
                "description": "Llama 3.2 7B - Equilibrado",
                "size": "4.1GB",
                "performance": "Bom para Ryzen 5600",
                "use_case": "Chat avançado, código complexo"
            },
            "codellama-7b": {
                "name": "codellama:7b",
                "description": "Code Llama 7B - Especializado em código",
                "size": "4.1GB", 
                "performance": "Bom para Ryzen 5600",
                "use_case": "Desenvolvimento, debugging"
            },
            "mistral-7b": {
                "name": "mistral:7b",
                "description": "Mistral 7B - Versátil e eficiente",
                "size": "4.1GB",
                "performance": "Excelente para Ryzen 5600",
                "use_case": "Chat geral, análise"
            },
            "phi3-mini": {
                "name": "microsoft/phi-3-mini",
                "description": "Phi-3 Mini - Muito rápido",
                "size": "1.8GB",
                "performance": "Ótimo para Ryzen 5600",
                "use_case": "Respostas rápidas, tarefas simples"
            },
            "qwen2.5-7b": {
                "name": "qwen2.5:7b",
                "description": "Qwen 2.5 7B - Multilingue",
                "size": "4.1GB",
                "performance": "Bom para Ryzen 5600",
                "use_case": "Chat multilingue, análise"
            }
        }
    
    def check_ollama_status(self) -> bool:
        """Verifica se o Ollama está rodando"""
        try:
            response = requests.get(f"{self.base_url}/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_installed_models(self) -> List[Dict[str, Any]]:
        """Lista modelos instalados"""
        try:
            response = requests.get(f"{self.base_url}/tags")
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
            return []
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {e}")
            return []
    
    def install_model(self, model_name: str) -> bool:
        """Instala um modelo"""
        try:
            logger.info(f"Instalando modelo: {model_name}")
            
            # Comando para instalar modelo
            cmd = f"ollama pull {model_name}"
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguardar conclusão
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Modelo {model_name} instalado com sucesso")
                return True
            else:
                logger.error(f"Erro ao instalar modelo {model_name}: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao instalar modelo {model_name}: {e}")
            return False
    
    def remove_model(self, model_name: str) -> bool:
        """Remove um modelo"""
        try:
            cmd = f"ollama rm {model_name}"
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if process.returncode == 0:
                logger.info(f"Modelo {model_name} removido com sucesso")
                return True
            else:
                logger.error(f"Erro ao remover modelo {model_name}: {process.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao remover modelo {model_name}: {e}")
            return False
    
    def chat_completion(self, model: str, message: str, system_prompt: str = "") -> Dict[str, Any]:
        """Envia mensagem para modelo Ollama"""
        try:
            payload = {
                "model": model,
                "messages": []
            }
            
            if system_prompt:
                payload["messages"].append({
                    "role": "system",
                    "content": system_prompt
                })
            
            payload["messages"].append({
                "role": "user", 
                "content": message
            })
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "response": response.json(),
                    "model": model
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class MCPManager:
    """Gerenciador principal de MCPs"""
    
    def __init__(self):
        self.mcps = {}
        self.cursor_config_path = self.find_cursor_config()
        self.ollama_manager = OllamaManager()
        self.github_installer = GitHubMCPInstaller()
        self.load_mcp_configs()
        
        # Caminhos para o mcp.json do Cursor
        self.cursor_mcp_paths = self.get_cursor_mcp_paths()
        
    def find_cursor_config(self) -> Optional[Path]:
        """Encontra arquivo de configuração do Cursor"""
        # Caminhos possíveis para configuração do Cursor
        possible_paths = [
            Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json",
            Path.home() / ".config" / "Cursor" / "User" / "settings.json",
            Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def load_mcp_configs(self):
        """Carrega configurações dos MCPs disponíveis"""
        self.mcps = {
            # MCPs Essenciais (Sistema e Desenvolvimento)
            "filesystem": MCPConfig(
                name="File System",
                package="@modelcontextprotocol/server-filesystem",
                command="npx @modelcontextprotocol/server-filesystem@latest --port {port}",
                port=3333,
                description="Acesso completo ao sistema de arquivos",
                category="system"
            ),
            "postgres": MCPConfig(
                name="PostgreSQL",
                package="@modelcontextprotocol/server-postgres",
                command="npx @modelcontextprotocol/server-postgres@latest --port {port}",
                port=3334,
                description="Banco de dados PostgreSQL",
                category="database"
            ),
            "brave-search": MCPConfig(
                name="Brave Search",
                package="@modelcontextprotocol/server-brave-search",
                command="npx @modelcontextprotocol/server-brave-search@latest --port {port}",
                port=3335,
                description="Busca na web via Brave",
                category="web"
            ),
            "puppeteer": MCPConfig(
                name="Puppeteer",
                package="@modelcontextprotocol/server-puppeteer",
                command="npx @modelcontextprotocol/server-puppeteer@latest --port {port}",
                port=3336,
                description="Automação web com Puppeteer",
                category="web"
            ),
            "slack": MCPConfig(
                name="Slack",
                package="@modelcontextprotocol/server-slack",
                command="npx @modelcontextprotocol/server-slack@latest --port {port}",
                port=3337,
                description="Integração Slack",
                category="communication"
            ),
            "github": MCPConfig(
                name="GitHub",
                package="@modelcontextprotocol/server-github",
                command="npx @modelcontextprotocol/server-github@latest --port {port}",
                port=3338,
                description="API do GitHub",
                category="development"
            ),
            "memory": MCPConfig(
                name="Memory",
                package="@modelcontextprotocol/server-memory",
                command="npx @modelcontextprotocol/server-memory@latest --port {port}",
                port=3339,
                description="Memória e knowledge graph",
                category="ai"
            ),
            "redis": MCPConfig(
                name="Redis",
                package="@modelcontextprotocol/server-redis",
                command="npx @modelcontextprotocol/server-redis@latest --port {port}",
                port=3340,
                description="Banco de dados Redis",
                category="database"
            ),
            "google-maps": MCPConfig(
                name="Google Maps",
                package="@modelcontextprotocol/server-google-maps",
                command="npx @modelcontextprotocol/server-google-maps@latest --port {port}",
                port=3341,
                description="API do Google Maps",
                category="web"
            ),
            "sequential-thinking": MCPConfig(
                name="Sequential Thinking",
                package="@modelcontextprotocol/server-sequential-thinking",
                command="npx @modelcontextprotocol/server-sequential-thinking@latest --port {port}",
                port=3342,
                description="Pensamento sequencial e resolução de problemas",
                category="ai"
            ),
            "everything": MCPConfig(
                name="Everything",
                package="@modelcontextprotocol/server-everything",
                command="npx @modelcontextprotocol/server-everything@latest --port {port}",
                port=3343,
                description="Testa todas as funcionalidades do MCP",
                category="testing"
            ),
            
            # MCPs de Controle de Editores (VS Code e Cursor)
            "vscode-mcp-server": MCPConfig(
                name="VS Code MCP Server",
                package="vscode-mcp-server",
                command="npx vscode-mcp-server@latest --port {port}",
                port=3344,
                description="Controle completo do VS Code via MCP (juehang)",
                category="editor",
                github_url="https://github.com/juehang/vscode-mcp-server",
                installation_method="github"
            ),
            "vscode-as-mcp-server": MCPConfig(
                name="VS Code as MCP Server",
                package="vscode-as-mcp-server",
                command="npx vscode-as-mcp-server@latest --port {port}",
                port=3345,
                description="Extensão completa do VS Code como servidor MCP (acomagu)",
                category="editor",
                github_url="https://github.com/acomagu/vscode-as-mcp-server",
                installation_method="github"
            ),
            "github-mcp-server": MCPConfig(
                name="GitHub MCP Server",
                package="@github/mcp-server",
                command="npx @github/mcp-server@latest --port {port}",
                port=3346,
                description="Servidor MCP oficial do GitHub com integração VS Code",
                category="development",
                github_url="https://github.com/github/github-mcp-server",
                installation_method="github"
            ),
            
            # MCPs de Terceiros
            "figma-mcp": MCPConfig(
                name="Figma",
                package="figma-mcp",
                command="npx figma-mcp@latest --port {port}",
                port=3347,
                description="Integração com Figma",
                category="design"
            ),
            "ref-tools-mcp": MCPConfig(
                name="Ref Tools",
                package="ref-tools-mcp",
                command="npx ref-tools-mcp@latest --port {port}",
                port=3348,
                description="Ferramentas Ref",
                category="development"
            ),
            "puppeteer-mcp-server": MCPConfig(
                name="Puppeteer MCP",
                package="puppeteer-mcp-server",
                command="npx puppeteer-mcp-server@latest --port {port}",
                port=3349,
                description="Automação web experimental",
                category="web"
            ),
            "valjs-mcp-alpha": MCPConfig(
                name="Val.js MCP",
                package="valjs-mcp-alpha",
                command="npx valjs-mcp-alpha@latest --port {port}",
                port=3350,
                description="Bridge para Val Town MCP tools",
                category="development"
            ),
            "xcodebuildmcp": MCPConfig(
                name="Xcode Build",
                package="xcodebuildmcp",
                command="npx xcodebuildmcp@latest --port {port}",
                port=3351,
                description="Gerenciamento de projetos Xcode",
                category="development"
            ),
            "mayar-mcp": MCPConfig(
                name="Mayar API",
                package="mayar-mcp",
                command="npx mayar-mcp@latest --port {port}",
                port=3352,
                description="API Mayar",
                category="api"
            ),
            "jsonresume-mcp": MCPConfig(
                name="JSON Resume",
                package="@jsonresume/mcp",
                command="npx @jsonresume/mcp@latest --port {port}",
                port=3353,
                description="Melhorias para JSON Resume",
                category="development"
            ),
            
            # MCPs de IA e Modelos (usando Ollama local)
            "ollama": MCPConfig(
                name="Ollama",
                package="@modelcontextprotocol/server-ollama",
                command="npx @modelcontextprotocol/server-ollama@latest --port {port}",
                port=3354,
                description="Modelos Ollama locais",
                category="ai"
            ),
            
            # MCPs de Navegação Web
            "browser-tools": MCPConfig(
                name="Browser Tools",
                package="@agentdeskai/browser-tools-server",
                command="npx @agentdeskai/browser-tools-server@latest --port {port}",
                port=3355,
                description="Automação de navegação web",
                category="web"
            )
        }
    
    def install_mcp(self, mcp_name: str) -> bool:
        """Instala um MCP via npm ou GitHub"""
        try:
            if mcp_name not in self.mcps:
                logger.error(f"MCP {mcp_name} não encontrado")
                return False
            
            mcp = self.mcps[mcp_name]
            logger.info(f"Instalando MCP: {mcp.name}")
            
            # Tentar instalar via npm primeiro
            success = self._install_via_npm(mcp)
            
            if success:
                mcp.installation_method = "npm"
                return True
            
            # Se falhar no npm, tentar GitHub
            logger.info(f"Falha no npm, tentando GitHub para {mcp.name}")
            success = self._install_via_github(mcp)
            
            if success:
                mcp.installation_method = "github"
                return True
            
            logger.error(f"Falha na instalação de {mcp.name} via npm e GitHub")
            return False
                
        except Exception as e:
            logger.error(f"Erro ao instalar MCP {mcp_name}: {e}")
            return False
    
    def _install_via_npm(self, mcp: MCPConfig) -> bool:
        """Instala MCP via npm"""
        try:
            cmd = f"npm install -g {mcp.package}"
            process = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True
            )
            
            if process.returncode == 0:
                logger.info(f"MCP {mcp.name} instalado com sucesso via npm")
                return True
            else:
                logger.warning(f"Erro ao instalar via npm: {process.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro na instalação npm: {e}")
            return False
    
    def _install_via_github(self, mcp: MCPConfig) -> bool:
        """Instala MCP via GitHub"""
        try:
            # Buscar no GitHub
            github_results = self.github_installer.search_mcp_on_github(mcp.name.lower())
            
            if not github_results:
                logger.warning(f"Nenhum MCP encontrado no GitHub para {mcp.name}")
                return False
            
            # Usar o primeiro resultado (mais popular)
            best_match = github_results[0]
            repo_url = best_match["clone_url"]
            
            logger.info(f"Instalando {mcp.name} do GitHub: {best_match['full_name']}")
            
            # Instalar via GitHub
            success = self.github_installer.install_from_github(repo_url, mcp.name)
            
            if success:
                # Atualizar configuração com URL do GitHub
                mcp.github_url = repo_url
                logger.info(f"MCP {mcp.name} instalado com sucesso do GitHub")
                return True
            else:
                logger.error(f"Falha na instalação via GitHub para {mcp.name}")
                return False
                
        except Exception as e:
            logger.error(f"Erro na instalação GitHub: {e}")
            return False
    
    def install_custom_mcp(self, mcp_name: str, github_url: Optional[str] = None, npm_package: Optional[str] = None) -> bool:
        """Instala um MCP customizado"""
        try:
            if github_url and github_url.strip():
                # Instalar do GitHub
                success = self.github_installer.install_from_github(github_url, mcp_name)
                if success:
                    # Adicionar à lista de MCPs
                    self.mcps[mcp_name] = MCPConfig(
                        name=mcp_name,
                        package=mcp_name,
                        command=f"npx {mcp_name}@latest --port {{port}}",
                        port=self._get_next_port(),
                        description=f"MCP customizado: {mcp_name}",
                        category="custom",
                        github_url=github_url,
                        installation_method="github"
                    )
                    return True
            
            elif npm_package and npm_package.strip():
                # Instalar via npm
                success = self._install_via_npm(MCPConfig(
                    name=mcp_name,
                    package=npm_package,
                    command="",
                    port=0,
                    description="",
                    category=""
                ))
                if success:
                    self.mcps[mcp_name] = MCPConfig(
                        name=mcp_name,
                        package=npm_package,
                        command=f"npx {npm_package}@latest --port {{port}}",
                        port=self._get_next_port(),
                        description=f"MCP customizado: {mcp_name}",
                        category="custom",
                        installation_method="npm"
                    )
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao instalar MCP customizado: {e}")
            return False
    
    def _get_next_port(self) -> int:
        """Obtém a próxima porta disponível"""
        used_ports = {mcp.port for mcp in self.mcps.values()}
        port = 3353  # Começar após os MCPs existentes
        while port in used_ports:
            port += 1
        return port
    
    def search_mcp_alternatives(self, mcp_name: str) -> List[Dict[str, Any]]:
        """Busca alternativas para um MCP no GitHub"""
        try:
            return self.github_installer.search_mcp_on_github(mcp_name)
        except Exception as e:
            logger.error(f"Erro ao buscar alternativas: {e}")
            return []
    
    def get_installation_status(self, mcp_name: str) -> Dict[str, Any]:
        """Obtém status detalhado de instalação de um MCP"""
        try:
            if mcp_name not in self.mcps:
                return {"error": "MCP não encontrado"}
            
            mcp = self.mcps[mcp_name]
            
            # Verificar se está instalado
            npm_check = subprocess.run(
                f"npm list -g {mcp.package}",
                shell=True,
                capture_output=True,
                text=True
            )
            
            is_installed = npm_check.returncode == 0
            
            return {
                "name": mcp.name,
                "package": mcp.package,
                "installed": is_installed,
                "installation_method": mcp.installation_method,
                "github_url": mcp.github_url,
                "status": mcp.status,
                "port": mcp.port,
                "category": mcp.category
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return {"error": str(e)}
    
    def start_mcp(self, mcp_name: str) -> bool:
        """Inicia um MCP"""
        try:
            if mcp_name not in self.mcps:
                logger.error(f"MCP {mcp_name} não encontrado")
                return False
            
            mcp = self.mcps[mcp_name]
            
            if mcp.process and mcp.process.poll() is None:
                logger.info(f"MCP {mcp.name} já está rodando")
                return True
            
            # Comando para iniciar MCP
            cmd = mcp.command.format(port=mcp.port)
            logger.info(f"Iniciando MCP {mcp.name}: {cmd}")
            
            mcp.process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguardar um pouco para verificar se iniciou
            time.sleep(2)
            
            if mcp.process.poll() is None:
                mcp.status = "running"
                mcp.enabled = True
                logger.info(f"MCP {mcp.name} iniciado na porta {mcp.port}")
                return True
            else:
                logger.error(f"Erro ao iniciar MCP {mcp.name}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao iniciar MCP {mcp_name}: {e}")
            return False
    
    def stop_mcp(self, mcp_name: str) -> bool:
        """Para um MCP"""
        try:
            if mcp_name not in self.mcps:
                logger.error(f"MCP {mcp_name} não encontrado")
                return False
            
            mcp = self.mcps[mcp_name]
            
            if not mcp.process or mcp.process.poll() is not None:
                logger.info(f"MCP {mcp.name} não está rodando")
                return True
            
            # Encerrar processo
            mcp.process.terminate()
            
            # Aguardar encerramento
            try:
                mcp.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                mcp.process.kill()
            
            mcp.status = "stopped"
            mcp.enabled = False
            logger.info(f"MCP {mcp.name} parado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar MCP {mcp_name}: {e}")
            return False
    
    def get_mcp_status(self) -> Dict[str, Any]:
        """Retorna status de todos os MCPs"""
        status = {}
        for name, mcp in self.mcps.items():
            # Verificar se processo ainda está rodando
            if mcp.process and mcp.process.poll() is not None:
                mcp.status = "stopped"
                mcp.enabled = False
            
            status[name] = {
                "name": mcp.name,
                "status": mcp.status,
                "enabled": mcp.enabled,
                "port": mcp.port,
                "description": mcp.description,
                "category": mcp.category
            }
        return status
    
    def analyze_prompt_for_mcps(self, prompt: str) -> List[str]:
        """Analisa o prompt e sugere MCPs necessários"""
        prompt_lower = prompt.lower()
        suggested_mcps = []
        
        # Análise baseada em palavras-chave
        if any(word in prompt_lower for word in ["web", "navegar", "site", "url", "browser"]):
            suggested_mcps.append("browser-tools")
        
        if any(word in prompt_lower for word in ["arquivo", "file", "ler", "escrever", "criar"]):
            suggested_mcps.append("filesystem")
        
        if any(word in prompt_lower for word in ["git", "commit", "push", "repositório"]):
            suggested_mcps.append("github")
        
        if any(word in prompt_lower for word in ["banco", "database", "sql", "query"]):
            suggested_mcps.append("postgres")
        
        if any(word in prompt_lower for word in ["ollama", "modelo local", "cpu"]):
            suggested_mcps.append("ollama")
        
        if any(word in prompt_lower for word in ["buscar", "pesquisar", "google"]):
            suggested_mcps.append("google-maps")
        
        return suggested_mcps
    
    def auto_manage_mcps(self, prompt: str) -> Dict[str, Any]:
        """Gerencia automaticamente MCPs baseado no prompt"""
        suggested_mcps = self.analyze_prompt_for_mcps(prompt)
        results = {
            "suggested_mcps": suggested_mcps,
            "started": [],
            "stopped": [],
            "errors": []
        }
        
        # Parar MCPs não necessários
        current_mcps = [name for name, mcp in self.mcps.items() if mcp.enabled]
        mcps_to_stop = [name for name in current_mcps if name not in suggested_mcps]
        
        for mcp_name in mcps_to_stop:
            if self.stop_mcp(mcp_name):
                results["stopped"].append(mcp_name)
            else:
                results["errors"].append(f"Erro ao parar {mcp_name}")
        
        # Iniciar MCPs necessários
        for mcp_name in suggested_mcps:
            if not self.mcps[mcp_name].enabled:
                if self.start_mcp(mcp_name):
                    results["started"].append(mcp_name)
                else:
                    results["errors"].append(f"Erro ao iniciar {mcp_name}")
        
        return results
    
    def update_cursor_config(self) -> bool:
        """Atualiza configuração do Cursor com MCPs ativos"""
        try:
            if not self.cursor_config_path:
                logger.warning("Configuração do Cursor não encontrada")
                return False
            
            # Ler configuração atual
            if self.cursor_config_path.exists():
                with open(self.cursor_config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {"mcpServers": {}}
            
            # Atualizar MCPs ativos
            active_mcps = {}
            for name, mcp in self.mcps.items():
                if mcp.enabled:
                    active_mcps[name] = {
                        "command": mcp.command.format(port=mcp.port),
                        "args": ["--port", str(mcp.port)]
                    }
            
            config["mcpServers"] = active_mcps
            
            # Salvar configuração
            with open(self.cursor_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("Configuração do Cursor atualizada")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar configuração do Cursor: {e}")
            return False

    def get_cursor_mcp_paths(self):
        """Retorna os possíveis caminhos para o mcp.json do Cursor"""
        system = platform.system()
        home = Path.home()
        
        paths = []
        
        if system == "Windows":
            # Windows - Cursor
            paths.extend([
                home / "AppData" / "Roaming" / "Cursor" / "User" / "mcp.json",
                home / "AppData" / "Local" / "Cursor" / "User" / "mcp.json",
                home / ".cursor" / "mcp.json"
            ])
        elif system == "Darwin":  # macOS
            paths.extend([
                home / "Library" / "Application Support" / "Cursor" / "User" / "mcp.json",
                home / ".cursor" / "mcp.json"
            ])
        else:  # Linux
            paths.extend([
                home / ".config" / "Cursor" / "User" / "mcp.json",
                home / ".cursor" / "mcp.json"
            ])
        
        return paths
    
    def find_cursor_mcp_file(self):
        """Encontra o arquivo mcp.json do Cursor"""
        for path in self.cursor_mcp_paths:
            if path.exists():
                return path
        return None
    
    def read_cursor_mcp_config(self):
        """Lê a configuração atual do mcp.json do Cursor"""
        mcp_file = self.find_cursor_mcp_file()
        
        if not mcp_file:
            return None, "Arquivo mcp.json do Cursor não encontrado"
        
        try:
            with open(mcp_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config, None
        except Exception as e:
            return None, f"Erro ao ler mcp.json: {e}"
    
    def write_cursor_mcp_config(self, config):
        """Escreve a configuração no mcp.json do Cursor"""
        mcp_file = self.find_cursor_mcp_file()
        
        if not mcp_file:
            # Tenta criar o diretório e arquivo
            for path in self.cursor_mcp_paths:
                try:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    mcp_file = path
                    break
                except:
                    continue
            
            if not mcp_file:
                return False, "Não foi possível criar o arquivo mcp.json"
        
        try:
            with open(mcp_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True, None
        except Exception as e:
            return False, f"Erro ao escrever mcp.json: {e}"
    
    def generate_mcp_config_for_cursor(self, selected_mcps=None):
        """Gera configuração MCP para o Cursor"""
        if selected_mcps is None:
            selected_mcps = list(self.mcps.keys())
        
        config = {
            "mcpServers": {}
        }
        
        for mcp_key in selected_mcps:
            if mcp_key in self.mcps:
                mcp = self.mcps[mcp_key]
                config["mcpServers"][mcp.name] = {
                    "command": "npx",
                    "args": [mcp.package, "--port", str(mcp.port)],
                    "env": {}
                }
        
        return config
    
    def install_mcps_to_cursor(self, selected_mcps=None):
        """Instala MCPs no Cursor"""
        if selected_mcps is None:
            selected_mcps = list(self.mcps.keys())
        
        # Gera a configuração
        config = self.generate_mcp_config_for_cursor(selected_mcps)
        
        # Escreve no arquivo do Cursor
        success, error = self.write_cursor_mcp_config(config)
        
        if success:
            return True, f"MCPs instalados com sucesso no Cursor: {', '.join(selected_mcps)}"
        else:
            return False, f"Erro ao instalar MCPs: {error}"
    
    def get_mcp_status_in_cursor(self):
        """Verifica quais MCPs estão instalados no Cursor"""
        config, error = self.read_cursor_mcp_config()
        
        if not config:
            return {}, error
        
        installed_mcps = {}
        for mcp_name, mcp_config in config.get("mcpServers", {}).items():
            # Tenta encontrar o MCP correspondente
            for key, mcp in self.mcps.items():
                if mcp.name == mcp_name:
                    installed_mcps[key] = {
                        "name": mcp_name,
                        "port": mcp.port,
                        "status": "installed"
                    }
                    break
        
        return installed_mcps, None
    
    def backup_cursor_mcp_config(self):
        """Faz backup da configuração atual do Cursor"""
        config, error = self.read_cursor_mcp_config()
        
        if not config:
            return False, error
        
        backup_path = Path("config") / "mcp_cursor_backup.json"
        backup_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True, f"Backup salvo em: {backup_path}"
        except Exception as e:
            return False, f"Erro ao fazer backup: {e}"
    
    def restore_cursor_mcp_config(self, backup_file=None):
        """Restaura configuração do Cursor a partir de backup"""
        if backup_file is None:
            backup_path = Path("config") / "mcp_cursor_backup.json"
        else:
            backup_path = Path(backup_file)
        
        if not backup_path.exists():
            return False, "Arquivo de backup não encontrado"
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            success, error = self.write_cursor_mcp_config(config)
            if success:
                return True, "Configuração restaurada com sucesso"
            else:
                return False, error
        except Exception as e:
            return False, f"Erro ao restaurar backup: {e}"
    
    def export_mcp_config(self, filename="mcp_config_export.json"):
        """Exporta configuração MCP para arquivo"""
        config = self.generate_mcp_config_for_cursor()
        
        export_path = Path("config") / filename
        export_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True, f"Configuração exportada para: {export_path}"
        except Exception as e:
            return False, f"Erro ao exportar: {e}"
    
    def get_cursor_info(self):
        """Retorna informações sobre o Cursor e MCPs"""
        mcp_file = self.find_cursor_mcp_file()
        
        info = {
            "cursor_mcp_file": str(mcp_file) if mcp_file else "Não encontrado",
            "cursor_mcp_exists": mcp_file is not None,
            "possible_paths": [str(p) for p in self.cursor_mcp_paths],
            "system": platform.system(),
            "home_dir": str(Path.home())
        }
        
        if mcp_file:
            config, error = self.read_cursor_mcp_config()
            if config:
                info["current_mcps"] = list(config.get("mcpServers", {}).keys())
                info["config_valid"] = True
            else:
                info["config_error"] = error
                info["config_valid"] = False
        
        return info

    def install_mcp_to_cursor(self, mcp_name: str) -> bool:
        """Instala MCP diretamente no Cursor"""
        try:
            if mcp_name not in self.mcps:
                logger.error(f"MCP {mcp_name} não encontrado")
                return False
            
            mcp = self.mcps[mcp_name]
            
            # Verificar se Cursor está instalado
            cursor_paths = self._find_cursor_installation()
            if not cursor_paths:
                logger.error("Cursor não encontrado")
                return False
            
            # Instalar MCP
            success = self.install_mcp(mcp_name)
            if not success:
                return False
            
            # Atualizar configuração do Cursor
            return self._update_cursor_mcp_config(mcp)
            
        except Exception as e:
            logger.error(f"Erro ao instalar MCP no Cursor: {e}")
            return False
    
    def install_mcp_to_vscode(self, mcp_name: str) -> bool:
        """Instala MCP no VS Code"""
        try:
            if mcp_name not in self.mcps:
                logger.error(f"MCP {mcp_name} não encontrado")
                return False
            
            mcp = self.mcps[mcp_name]
            
            # Verificar se VS Code está instalado
            vscode_paths = self._find_vscode_installation()
            if not vscode_paths:
                logger.error("VS Code não encontrado")
                return False
            
            # Instalar MCP
            success = self.install_mcp(mcp_name)
            if not success:
                return False
            
            # Atualizar configuração do VS Code
            return self._update_vscode_mcp_config(mcp)
            
        except Exception as e:
            logger.error(f"Erro ao instalar MCP no VS Code: {e}")
            return False
    
    def _find_cursor_installation(self) -> List[Path]:
        """Encontra instalações do Cursor"""
        possible_paths = [
            Path.home() / "AppData" / "Local" / "Programs" / "Cursor" / "Cursor.exe",
            Path.home() / "AppData" / "Roaming" / "Cursor",
            Path("/Applications/Cursor.app"),  # macOS
            Path.home() / ".local/share/Cursor"  # Linux
        ]
        
        found_paths = []
        for path in possible_paths:
            if path.exists():
                found_paths.append(path)
        
        return found_paths
    
    def _find_vscode_installation(self) -> List[Path]:
        """Encontra instalações do VS Code"""
        possible_paths = [
            Path.home() / "AppData" / "Local" / "Programs" / "Microsoft VS Code" / "Code.exe",
            Path.home() / "AppData" / "Roaming" / "Code",
            Path("/Applications/Visual Studio Code.app"),  # macOS
            Path.home() / ".vscode"  # Linux
        ]
        
        found_paths = []
        for path in possible_paths:
            if path.exists():
                found_paths.append(path)
        
        return found_paths
    
    def _update_cursor_mcp_config(self, mcp: MCPConfig) -> bool:
        """Atualiza configuração MCP do Cursor"""
        try:
            # Caminhos de configuração do Cursor
            config_paths = [
                Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json",
                Path.home() / ".config" / "Cursor" / "User" / "settings.json",
                Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"
            ]
            
            for config_path in config_paths:
                if config_path.exists():
                    # Ler configuração atual
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    # Adicionar MCP se não existir
                    if "mcpServers" not in config:
                        config["mcpServers"] = {}
                    
                    if mcp.name not in config["mcpServers"]:
                        config["mcpServers"][mcp.name] = {
                            "command": "npx",
                            "args": ["-y", mcp.package, "--port", str(mcp.port)]
                        }
                        
                        # Salvar configuração
                        with open(config_path, 'w', encoding='utf-8') as f:
                            json.dump(config, f, indent=2, ensure_ascii=False)
                        
                        logger.info(f"MCP {mcp.name} adicionado à configuração do Cursor")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao atualizar configuração do Cursor: {e}")
            return False
    
    def _update_vscode_mcp_config(self, mcp: MCPConfig) -> bool:
        """Atualiza configuração MCP do VS Code"""
        try:
            # Caminhos de configuração do VS Code
            config_paths = [
                Path.home() / "AppData" / "Roaming" / "Code" / "User" / "settings.json",
                Path.home() / ".config/Code/User/settings.json",
                Path.home() / "Library/Application Support/Code/User/settings.json"
            ]
            
            for config_path in config_paths:
                if config_path.exists():
                    # Ler configuração atual
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    # Adicionar MCP se não existir
                    if "mcp.servers" not in config:
                        config["mcp.servers"] = {}
                    
                    if mcp.name not in config["mcp.servers"]:
                        config["mcp.servers"][mcp.name] = {
                            "command": "npx",
                            "args": ["-y", mcp.package, "--port", str(mcp.port)]
                        }
                        
                        # Salvar configuração
                        with open(config_path, 'w', encoding='utf-8') as f:
                            json.dump(config, f, indent=2, ensure_ascii=False)
                        
                        logger.info(f"MCP {mcp.name} adicionado à configuração do VS Code")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao atualizar configuração do VS Code: {e}")
            return False
    
    def get_editor_status(self) -> Dict[str, Any]:
        """Obtém status dos editores instalados"""
        status = {
            "cursor": {
                "installed": False,
                "paths": [],
                "config_path": None
            },
            "vscode": {
                "installed": False,
                "paths": [],
                "config_path": None
            }
        }
        
        # Verificar Cursor
        cursor_paths = self._find_cursor_installation()
        if cursor_paths:
            status["cursor"]["installed"] = True
            status["cursor"]["paths"] = [str(p) for p in cursor_paths]
            
            # Encontrar arquivo de configuração
            config_paths = [
                Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json",
                Path.home() / ".config" / "Cursor" / "User" / "settings.json",
                Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"
            ]
            
            for config_path in config_paths:
                if config_path.exists():
                    status["cursor"]["config_path"] = str(config_path)
                    break
        
        # Verificar VS Code
        vscode_paths = self._find_vscode_installation()
        if vscode_paths:
            status["vscode"]["installed"] = True
            status["vscode"]["paths"] = [str(p) for p in vscode_paths]
            
            # Encontrar arquivo de configuração
            config_paths = [
                Path.home() / "AppData" / "Roaming" / "Code" / "User" / "settings.json",
                Path.home() / ".config/Code/User/settings.json",
                Path.home() / "Library/Application Support/Code/User/settings.json"
            ]
            
            for config_path in config_paths:
                if config_path.exists():
                    status["vscode"]["config_path"] = str(config_path)
                    break
        
        return status

# Função de teste
def test_mcp_manager():
    """Testa o gerenciador de MCPs"""
    print("=== Teste do Gerenciador de MCPs ===\n")
    
    manager = MCPManager()
    
    # Verificar status do Ollama
    ollama_status = manager.ollama_manager.check_ollama_status()
    print(f"Ollama rodando: {ollama_status}")
    
    # Listar modelos recomendados
    print("\nModelos recomendados para Ryzen 5600:")
    for name, info in manager.ollama_manager.recommended_models.items():
        print(f"- {name}: {info['description']} ({info['size']})")
    
    # Status dos MCPs
    print("\nStatus dos MCPs:")
    status = manager.get_mcp_status()
    for name, info in status.items():
        print(f"- {name}: {info['status']} (porta {info['port']})")
    
    # Teste de análise de prompt
    test_prompt = "Preciso navegar na web e ler um arquivo"
    suggested = manager.analyze_prompt_for_mcps(test_prompt)
    print(f"\nMCPs sugeridos para: '{test_prompt}'")
    print(f"- {suggested}")
    
    print("\n=== Teste concluído ===")

if __name__ == "__main__":
    test_mcp_manager() 