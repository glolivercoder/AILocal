#!/usr/bin/env python3
"""
Gerenciador de MCP para Cursor
Permite instalar, configurar e gerenciar MCPs no Cursor
"""

import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class CursorMCPManager:
    def __init__(self):
        self.cursor_mcp_paths = self.get_cursor_mcp_paths()
        self.mcps = self.load_mcp_configs()
        
    def get_cursor_mcp_paths(self) -> List[Path]:
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
    
    def load_mcp_configs(self) -> Dict:
        """Carrega configurações dos MCPs disponíveis"""
        return {
            "filesystem": {
                "name": "File System",
                "package": "@modelcontextprotocol/server-filesystem",
                "port": 3333,
                "description": "Acesso completo ao sistema de arquivos",
                "category": "system"
            },
            "postgres": {
                "name": "PostgreSQL",
                "package": "@modelcontextprotocol/server-postgres",
                "port": 3334,
                "description": "Banco de dados PostgreSQL",
                "category": "database"
            },
            "brave-search": {
                "name": "Brave Search",
                "package": "@modelcontextprotocol/server-brave-search",
                "port": 3335,
                "description": "Busca na web via Brave",
                "category": "web"
            },
            "puppeteer": {
                "name": "Puppeteer",
                "package": "@modelcontextprotocol/server-puppeteer",
                "port": 3336,
                "description": "Automação web com Puppeteer",
                "category": "web"
            },
            "slack": {
                "name": "Slack",
                "package": "@modelcontextprotocol/server-slack",
                "port": 3337,
                "description": "Integração Slack",
                "category": "communication"
            },
            "github": {
                "name": "GitHub",
                "package": "@modelcontextprotocol/server-github",
                "port": 3338,
                "description": "API do GitHub",
                "category": "development"
            },
            "memory": {
                "name": "Memory",
                "package": "@modelcontextprotocol/server-memory",
                "port": 3339,
                "description": "Memória e knowledge graph",
                "category": "ai"
            },
            "redis": {
                "name": "Redis",
                "package": "@modelcontextprotocol/server-redis",
                "port": 3340,
                "description": "Banco de dados Redis",
                "category": "database"
            },
            "google-maps": {
                "name": "Google Maps",
                "package": "@modelcontextprotocol/server-google-maps",
                "port": 3341,
                "description": "API do Google Maps",
                "category": "web"
            },
            "sequential-thinking": {
                "name": "Sequential Thinking",
                "package": "@modelcontextprotocol/server-sequential-thinking",
                "port": 3342,
                "description": "Pensamento sequencial e resolução de problemas",
                "category": "ai"
            },
            "everything": {
                "name": "Everything",
                "package": "@modelcontextprotocol/server-everything",
                "port": 3343,
                "description": "Testa todas as funcionalidades do MCP",
                "category": "testing"
            },
            "ollama": {
                "name": "Ollama",
                "package": "@modelcontextprotocol/server-ollama",
                "port": 3351,
                "description": "Modelos Ollama locais",
                "category": "ai"
            },
            "browser-tools": {
                "name": "Browser Tools",
                "package": "@agentdeskai/browser-tools-server",
                "port": 3352,
                "description": "Automação de navegação web",
                "category": "web"
            },
            "stata-mcp": {
                "name": "Stata MCP",
                "package": "stata-mcp",
                "port": 4000,
                "description": "Integração Stata via MCP (análise estatística)",
                "category": "statistics"
            }
        }
    
    def find_cursor_mcp_file(self) -> Optional[Path]:
        """Encontra o arquivo mcp.json do Cursor"""
        for path in self.cursor_mcp_paths:
            if path.exists():
                return path
        return None
    
    def read_cursor_mcp_config(self) -> Tuple[Optional[Dict], Optional[str]]:
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
    
    def write_cursor_mcp_config(self, config: Dict) -> Tuple[bool, Optional[str]]:
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
    
    def generate_mcp_config_for_cursor(self, selected_mcps: Optional[List[str]] = None) -> Dict:
        """Gera configuração MCP para o Cursor"""
        if selected_mcps is None:
            selected_mcps = list(self.mcps.keys())
        
        config = {
            "mcpServers": {}
        }
        
        for mcp_key in selected_mcps:
            if mcp_key in self.mcps:
                mcp = self.mcps[mcp_key]
                config["mcpServers"][mcp["name"]] = {
                    "command": "npx",
                    "args": [mcp["package"], "--port", str(mcp["port"])],
                    "env": {}
                }
        
        return config
    
    def install_mcps_to_cursor(self, selected_mcps: Optional[List[str]] = None) -> Tuple[bool, str]:
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
            return False, f"Erro ao instalar MCPs: {error or 'Erro desconhecido'}"
    
    def get_mcp_status_in_cursor(self) -> Tuple[Dict, Optional[str]]:
        """Verifica quais MCPs estão instalados no Cursor"""
        config, error = self.read_cursor_mcp_config()
        
        if not config:
            return {}, error
        
        installed_mcps = {}
        for mcp_name, mcp_config in config.get("mcpServers", {}).items():
            # Tenta encontrar o MCP correspondente
            for key, mcp in self.mcps.items():
                if mcp["name"] == mcp_name:
                    installed_mcps[key] = {
                        "name": mcp_name,
                        "port": mcp["port"],
                        "status": "installed"
                    }
                    break
        
        return installed_mcps, None
    
    def backup_cursor_mcp_config(self) -> Tuple[bool, str]:
        """Faz backup da configuração atual do Cursor"""
        config, error = self.read_cursor_mcp_config()
        
        if not config:
            return False, error or "Erro desconhecido"
        
        backup_path = Path("config") / "mcp_cursor_backup.json"
        backup_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True, f"Backup salvo em: {backup_path}"
        except Exception as e:
            return False, f"Erro ao fazer backup: {e}"
    
    def restore_cursor_mcp_config(self, backup_file: Optional[str] = None) -> Tuple[bool, str]:
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
                return False, error or "Erro desconhecido"
        except Exception as e:
            return False, f"Erro ao restaurar backup: {e}"
    
    def export_mcp_config(self, filename: str = "mcp_config_export.json") -> Tuple[bool, str]:
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
    
    def get_cursor_info(self) -> Dict:
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
    
    def test_mcp_installation(self, mcp_name: str) -> Tuple[bool, str]:
        """Testa se um MCP pode ser instalado via npm"""
        if mcp_name not in self.mcps:
            return False, f"MCP '{mcp_name}' não encontrado"
        
        mcp = self.mcps[mcp_name]
        package = mcp["package"]
        
        try:
            # Verifica se o pacote existe no npm
            result = subprocess.run(
                ["npm", "view", package, "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return True, f"MCP '{mcp_name}' disponível no npm"
            else:
                return False, f"MCP '{mcp_name}' não encontrado no npm"
                
        except subprocess.TimeoutExpired:
            return False, f"Timeout ao verificar MCP '{mcp_name}'"
        except Exception as e:
            return False, f"Erro ao verificar MCP '{mcp_name}': {e}"

def main():
    """Função principal para demonstração"""
    print("🚀 Gerenciador de MCP para Cursor")
    print("=" * 50)
    
    manager = CursorMCPManager()
    
    # Mostrar informações do Cursor
    info = manager.get_cursor_info()
    print(f"Sistema: {info['system']}")
    print(f"Arquivo MCP: {info['cursor_mcp_file']}")
    print(f"MCP existe: {info['cursor_mcp_exists']}")
    
    if info['cursor_mcp_exists']:
        print(f"MCPs atuais: {info.get('current_mcps', [])}")
    else:
        print("Arquivo mcp.json não encontrado - será criado automaticamente")
    
    print("\n📋 MCPs disponíveis:")
    for key, mcp in manager.mcps.items():
        print(f"  - {key}: {mcp['name']} ({mcp['category']})")
    
    # Testar instalação de alguns MCPs
    print("\n🧪 Testando disponibilidade dos MCPs:")
    test_mcps = ["filesystem", "postgres", "brave-search", "puppeteer"]
    
    for mcp_name in test_mcps:
        success, message = manager.test_mcp_installation(mcp_name)
        status = "✅" if success else "❌"
        print(f"  {status} {mcp_name}: {message}")
    
    # Perguntar se quer instalar MCPs
    print(f"\n🤔 Deseja instalar MCPs no Cursor? (s/n): ", end="")
    
    try:
        response = input().lower().strip()
        if response in ['s', 'sim', 'y', 'yes']:
            print("\n📦 Instalando MCPs essenciais...")
            
            # Instalar MCPs essenciais
            essential_mcps = ["filesystem", "postgres", "brave-search"]
            success, message = manager.install_mcps_to_cursor(essential_mcps)
            
            if success:
                print(f"✅ {message}")
                
                # Mostrar configuração gerada
                config = manager.generate_mcp_config_for_cursor(essential_mcps)
                print(f"\n📄 Configuração gerada:")
                print(json.dumps(config, indent=2, ensure_ascii=False))
            else:
                print(f"❌ {message}")
        else:
            print("Instalação pulada.")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Operação interrompida pelo usuário")
    
    print("\n✅ Demonstração concluída!")

if __name__ == "__main__":
    main() 