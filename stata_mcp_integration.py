#!/usr/bin/env python3
"""
Integração com Stata MCP Extension
Baseado em: https://github.com/hanlulong/stata-mcp.git
"""

import json
import os
import platform
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class StataMCPIntegration:
    def __init__(self):
        self.extension_name = "stata-mcp"
        self.extension_package = "deepecon.stata-mcp"
        self.mcp_server_url = "http://localhost:4000/mcp"
        self.extension_paths = self.get_extension_paths()
        
    def get_extension_paths(self) -> Dict[str, Path]:
        """Retorna os caminhos para a extensão Stata MCP"""
        system = platform.system()
        home = Path.home()
        
        paths = {}
        
        if system == "Windows":
            paths.update({
                "vscode": home / ".vscode" / "extensions",
                "cursor": home / ".cursor" / "extensions",
                "cline_config": home / "AppData" / "Roaming" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
            })
        elif system == "Darwin":  # macOS
            paths.update({
                "vscode": home / ".vscode" / "extensions",
                "cursor": home / ".cursor" / "extensions",
                "cline_config": home / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
            })
        else:  # Linux
            paths.update({
                "vscode": home / ".config" / "Code" / "User" / "extensions",
                "cursor": home / ".cursor" / "extensions",
                "cline_config": home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
            })
        
        return paths
    
    def check_extension_installed(self) -> Tuple[bool, str]:
        """Verifica se a extensão Stata MCP está instalada"""
        for editor, path in self.extension_paths.items():
            if editor in ["vscode", "cursor"]:
                if path.exists():
                    # Procura por pastas que começam com o nome da extensão
                    for item in path.iterdir():
                        if item.is_dir() and item.name.startswith(self.extension_package):
                            return True, f"Encontrada em {editor}: {item}"
        
        return False, "Extensão não encontrada"
    
    def install_extension_via_marketplace(self) -> Tuple[bool, str]:
        """Instala a extensão via marketplace do VS Code/Cursor"""
        try:
            # Comando para instalar via code
            command = f"code --install-extension {self.extension_package}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "Extensão instalada com sucesso via marketplace"
            else:
                return False, f"Erro ao instalar: {result.stderr}"
                
        except Exception as e:
            return False, f"Erro na instalação: {e}"
    
    def install_extension_via_git(self) -> Tuple[bool, str]:
        """Instala a extensão diretamente do repositório Git"""
        try:
            # Clona o repositório
            repo_url = "https://github.com/hanlulong/stata-mcp.git"
            temp_dir = Path("temp") / "stata-mcp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Clone do repositório
            clone_cmd = f"git clone {repo_url} {temp_dir}"
            result = subprocess.run(clone_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, f"Erro ao clonar repositório: {result.stderr}"
            
            # Instala dependências Python (se necessário)
            if (temp_dir / "requirements.txt").exists():
                install_cmd = f"pip install -r {temp_dir / 'requirements.txt'}"
                result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode != 0:
                    return False, f"Erro ao instalar dependências: {result.stderr}"
            
            return True, f"Extensão instalada via Git em: {temp_dir}"
            
        except Exception as e:
            return False, f"Erro na instalação via Git: {e}"
    
    def configure_cline_mcp(self) -> Tuple[bool, str]:
        """Configura o Stata MCP para Cline"""
        try:
            config_file = self.extension_paths["cline_config"]
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Configuração MCP para Cline
            config = {
                "mcpServers": {
                    "stata-mcp": {
                        "url": self.mcp_server_url,
                        "transport": "sse"
                    }
                }
            }
            
            # Lê configuração existente se existir
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
                
                # Adiciona o Stata MCP à configuração existente
                if "mcpServers" not in existing_config:
                    existing_config["mcpServers"] = {}
                
                existing_config["mcpServers"]["stata-mcp"] = config["mcpServers"]["stata-mcp"]
                config = existing_config
            
            # Escreve a configuração
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True, f"Configuração Cline salva em: {config_file}"
            
        except Exception as e:
            return False, f"Erro ao configurar Cline: {e}"
    
    def configure_cursor_mcp(self) -> Tuple[bool, str]:
        """Configura o Stata MCP para Cursor"""
        try:
            # Usa o gerenciador de MCP do Cursor
            from cursor_mcp_manager import CursorMCPManager
            
            cursor_manager = CursorMCPManager()
            
            # Adiciona o Stata MCP à configuração
            stata_config = {
                "name": "Stata MCP",
                "package": "stata-mcp",
                "port": 4000,
                "description": "Integração Stata via MCP",
                "category": "statistics"
            }
            
            # Adiciona à lista de MCPs
            cursor_manager.mcps["stata-mcp"] = stata_config
            
            # Instala no Cursor
            success, message = cursor_manager.install_mcps_to_cursor(["stata-mcp"])
            
            if success:
                return True, f"Stata MCP configurado no Cursor: {message}"
            else:
                return False, f"Erro ao configurar no Cursor: {message}"
                
        except Exception as e:
            return False, f"Erro ao configurar Cursor: {e}"
    
    def check_stata_installation(self) -> Tuple[bool, str]:
        """Verifica se o Stata está instalado no sistema"""
        system = platform.system()
        
        if system == "Windows":
            # Verifica caminhos comuns do Stata no Windows
            stata_paths = [
                "C:\\Program Files\\Stata17\\StataMP-64.exe",
                "C:\\Program Files\\Stata17\\StataSE-64.exe",
                "C:\\Program Files\\Stata17\\StataBE-64.exe",
                "C:\\Program Files\\Stata18\\StataMP-64.exe",
                "C:\\Program Files\\Stata18\\StataSE-64.exe",
                "C:\\Program Files\\Stata18\\StataBE-64.exe"
            ]
            
            for path in stata_paths:
                if Path(path).exists():
                    return True, f"Stata encontrado em: {path}"
            
            return False, "Stata não encontrado no Windows"
            
        elif system == "Darwin":  # macOS
            # Verifica caminhos comuns do Stata no macOS
            stata_paths = [
                "/Applications/Stata/stata",
                "/Applications/StataMP.app/Contents/MacOS/stata",
                "/Applications/StataSE.app/Contents/MacOS/stata",
                "/Applications/StataBE.app/Contents/MacOS/stata"
            ]
            
            for path in stata_paths:
                if Path(path).exists():
                    return True, f"Stata encontrado em: {path}"
            
            return False, "Stata não encontrado no macOS"
            
        else:  # Linux
            # Verifica se o comando stata está disponível
            result = subprocess.run(["which", "stata"], capture_output=True, text=True)
            if result.returncode == 0:
                return True, f"Stata encontrado em: {result.stdout.strip()}"
            else:
                return False, "Stata não encontrado no Linux"
    
    def test_mcp_connection(self) -> Tuple[bool, str]:
        """Testa a conexão com o servidor MCP do Stata"""
        try:
            response = requests.get(self.mcp_server_url, timeout=5)
            if response.status_code == 200:
                return True, "Conexão MCP estabelecida com sucesso"
            else:
                return False, f"Servidor MCP respondeu com status: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return False, "Servidor MCP não está rodando"
        except Exception as e:
            return False, f"Erro ao testar conexão: {e}"
    
    def start_stata_mcp_server(self) -> Tuple[bool, str]:
        """Inicia o servidor MCP do Stata"""
        try:
            # Verifica se a extensão está instalada
            installed, message = self.check_extension_installed()
            if not installed:
                return False, f"Extensão não instalada: {message}"
            
            # Comando para iniciar o servidor (pode variar dependendo da instalação)
            command = "stata-mcp-server"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "Servidor MCP iniciado com sucesso"
            else:
                return False, f"Erro ao iniciar servidor: {result.stderr}"
                
        except Exception as e:
            return False, f"Erro ao iniciar servidor: {e}"
    
    def get_installation_guide(self) -> str:
        """Retorna um guia de instalação completo"""
        guide = """
# Guia de Instalação - Stata MCP Extension

## 1. Pré-requisitos

### Stata
- Stata 17 ou superior instalado
- Edição MP, SE ou BE

### Python
- Python 3.11 ou superior
- UV (gerenciador de pacotes Python)

### Editores
- VS Code ou Cursor IDE

## 2. Instalação da Extensão

### Opção A: Via Marketplace (Recomendado)
1. Abra VS Code/Cursor
2. Vá para Extensions (Ctrl+Shift+X)
3. Pesquise por "Stata MCP"
4. Instale a extensão "deepecon.stata-mcp"

### Opção B: Via Git
```bash
git clone https://github.com/hanlulong/stata-mcp.git
cd stata-mcp
pip install -r requirements.txt
```

## 3. Configuração

### Para Cursor
1. Abra as configurações do Cursor
2. Adicione ao mcp.json:
```json
{
  "mcpServers": {
    "stata-mcp": {
      "command": "npx",
      "args": ["stata-mcp-server", "--port", "4000"],
      "env": {}
    }
  }
}
```

### Para Cline
1. Localize o arquivo de configuração:
   - Windows: %APPDATA%/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
   - macOS: ~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
   - Linux: ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

2. Adicione a configuração:
```json
{
  "mcpServers": {
    "stata-mcp": {
      "url": "http://localhost:4000/mcp",
      "transport": "sse"
    }
  }
}
```

## 4. Uso

1. Abra um arquivo .do no VS Code/Cursor
2. A extensão deve aparecer na barra de status
3. Use Ctrl+Shift+P e digite "Stata" para ver comandos disponíveis
4. Execute comandos Stata diretamente do editor

## 5. Troubleshooting

### Problemas Comuns
- **Extensão não carrega**: Verifique se o Python 3.11+ está instalado
- **Servidor não inicia**: Verifique se o Stata está no PATH
- **Erro de conexão**: Verifique se a porta 4000 está livre

### Logs
- VS Code: View > Output > Stata MCP
- Cursor: Help > Toggle Developer Tools > Console

## 6. Recursos Avançados

### Configuração de Edição do Stata
```json
{
  "stata-vscode.stataEdition": "MP"
}
```

### Configuração de Caminho Personalizado
```json
{
  "stata-vscode.stataPath": "C:\\Program Files\\Stata17\\StataMP-64.exe"
}
```
"""
        return guide

def main():
    """Função principal para demonstração"""
    print("🚀 Integração Stata MCP Extension")
    print("=" * 50)
    
    stata_integration = StataMCPIntegration()
    
    # Verificar instalação da extensão
    print("🔍 Verificando instalação da extensão...")
    installed, message = stata_integration.check_extension_installed()
    print(f"Status: {'✅' if installed else '❌'} {message}")
    
    # Verificar instalação do Stata
    print("\n📊 Verificando instalação do Stata...")
    stata_installed, stata_message = stata_integration.check_stata_installation()
    print(f"Status: {'✅' if stata_installed else '❌'} {stata_message}")
    
    # Testar conexão MCP
    print("\n🌐 Testando conexão MCP...")
    connected, conn_message = stata_integration.test_mcp_connection()
    print(f"Status: {'✅' if connected else '❌'} {conn_message}")
    
    # Mostrar opções de instalação
    print("\n📦 Opções de instalação:")
    print("1. Via Marketplace (Recomendado)")
    print("2. Via Git (Desenvolvimento)")
    print("3. Configurar Cline")
    print("4. Configurar Cursor")
    
    # Perguntar ação
    print(f"\n🤔 Qual ação deseja realizar? (1-4): ", end="")
    
    try:
        choice = input().strip()
        
        if choice == "1":
            success, message = stata_integration.install_extension_via_marketplace()
            print(f"Resultado: {'✅' if success else '❌'} {message}")
            
        elif choice == "2":
            success, message = stata_integration.install_extension_via_git()
            print(f"Resultado: {'✅' if success else '❌'} {message}")
            
        elif choice == "3":
            success, message = stata_integration.configure_cline_mcp()
            print(f"Resultado: {'✅' if success else '❌'} {message}")
            
        elif choice == "4":
            success, message = stata_integration.configure_cursor_mcp()
            print(f"Resultado: {'✅' if success else '❌'} {message}")
            
        else:
            print("Opção inválida")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Operação interrompida pelo usuário")
    
    # Mostrar guia de instalação
    print(f"\n📖 Deseja ver o guia completo de instalação? (s/n): ", end="")
    
    try:
        show_guide = input().lower().strip()
        if show_guide in ['s', 'sim', 'y', 'yes']:
            print("\n" + "=" * 50)
            print(stata_integration.get_installation_guide())
    except KeyboardInterrupt:
        pass
    
    print("\n✅ Demonstração concluída!")

if __name__ == "__main__":
    main() 