#!/usr/bin/env python3
"""
Script para instalar MCPs de controle de editores (VS Code e Cursor)
Baseado nos servidores MCP mais populares para controle de editores
"""

import os
import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

def check_editor_installations():
    """Verifica se VS Code e Cursor estão instalados"""
    print("🔍 Verificando Editores Instalados")
    print("=" * 50)
    
    editors = {
        "vscode": {
            "paths": [
                Path.home() / "AppData" / "Local" / "Programs" / "Microsoft VS Code" / "Code.exe",
                Path.home() / "AppData" / "Roaming" / "Code",
                Path("/Applications/Visual Studio Code.app"),
                Path.home() / ".vscode"
            ],
            "config_paths": [
                Path.home() / "AppData" / "Roaming" / "Code" / "User" / "settings.json",
                Path.home() / ".config/Code/User/settings.json",
                Path.home() / "Library/Application Support/Code/User/settings.json"
            ]
        },
        "cursor": {
            "paths": [
                Path.home() / "AppData" / "Local" / "Programs" / "Cursor" / "Cursor.exe",
                Path.home() / "AppData" / "Roaming" / "Cursor",
                Path("/Applications/Cursor.app"),
                Path.home() / ".local/share/Cursor"
            ],
            "config_paths": [
                Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json",
                Path.home() / ".config" / "Cursor" / "User" / "settings.json",
                Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"
            ]
        }
    }
    
    found_editors = {}
    
    for editor_name, editor_info in editors.items():
        print(f"\n{editor_name.upper()}:")
        
        # Verificar instalação
        installed = False
        for path in editor_info["paths"]:
            if path.exists():
                print(f"  ✅ Instalado em: {path}")
                installed = True
                break
        
        if not installed:
            print(f"  ❌ Não encontrado")
            continue
        
        # Verificar configuração
        config_found = False
        for config_path in editor_info["config_paths"]:
            if config_path.exists():
                print(f"  ✅ Configuração em: {config_path}")
                config_found = True
                found_editors[editor_name] = {
                    "installed": True,
                    "config_path": config_path
                }
                break
        
        if not config_found:
            print(f"  ⚠️ Arquivo de configuração não encontrado")
    
    return found_editors

def install_editor_mcps():
    """Instala MCPs específicos para controle de editores"""
    print("\n🚀 Instalando MCPs de Controle de Editores")
    print("=" * 50)
    
    # MCPs de controle de editores
    editor_mcps = [
        {
            "name": "vscode-mcp-server",
            "description": "Controle completo do VS Code via MCP (juehang)",
            "github_url": "https://github.com/juehang/vscode-mcp-server",
            "npm_package": "vscode-mcp-server",
            "port": 3344,
            "features": [
                "Controle de edição no VS Code",
                "Navegação de arquivos",
                "Execução de comandos",
                "Controle do cursor"
            ]
        },
        {
            "name": "vscode-as-mcp-server",
            "description": "Extensão completa do VS Code como servidor MCP (acomagu)",
            "github_url": "https://github.com/acomagu/vscode-as-mcp-server",
            "npm_package": "vscode-as-mcp-server",
            "port": 3345,
            "features": [
                "Edição de código avançada",
                "Comandos integrados",
                "Terminal integrado",
                "Foco no editor",
                "Automação completa"
            ]
        },
        {
            "name": "github-mcp-server",
            "description": "Servidor MCP oficial do GitHub com integração VS Code",
            "github_url": "https://github.com/github/github-mcp-server",
            "npm_package": "@github/mcp-server",
            "port": 3346,
            "features": [
                "Integração com GitHub",
                "Controle de repositórios",
                "Automação de código",
                "Integração VS Code"
            ]
        }
    ]
    
    installed_mcps = []
    
    for mcp in editor_mcps:
        print(f"\n📦 Instalando: {mcp['name']}")
        print(f"   Descrição: {mcp['description']}")
        print(f"   Recursos:")
        for feature in mcp['features']:
            print(f"     • {feature}")
        
        # Tentar instalar via npm primeiro
        print(f"   Tentando instalação via npm...")
        success = install_via_npm(mcp['npm_package'])
        
        if not success:
            print(f"   Tentando instalação via GitHub...")
            success = install_via_github(mcp['github_url'], mcp['name'])
        
        if success:
            print(f"   ✅ {mcp['name']} instalado com sucesso")
            installed_mcps.append(mcp)
        else:
            print(f"   ❌ Falha na instalação de {mcp['name']}")
    
    return installed_mcps

def install_via_npm(package_name: str) -> bool:
    """Instala MCP via npm"""
    try:
        cmd = f"npm install -g {package_name}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"     Erro npm: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"     Erro: {e}")
        return False

def install_via_github(repo_url: str, mcp_name: str) -> bool:
    """Instala MCP via GitHub"""
    try:
        # Criar diretório temporário
        temp_dir = Path.home() / "AppData" / "Local" / "Temp" / f"mcp_{mcp_name}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Clonar repositório
        clone_cmd = f"git clone {repo_url} {temp_dir}"
        result = subprocess.run(clone_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"     Erro ao clonar: {result.stderr}")
            return False
        
        # Instalar dependências
        install_cmd = f"cd {temp_dir} && npm install"
        result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"     Erro ao instalar dependências: {result.stderr}")
            return False
        
        # Instalar globalmente
        global_cmd = f"cd {temp_dir} && npm install -g ."
        result = subprocess.run(global_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"     Erro na instalação global: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"     Erro: {e}")
        return False

def configure_editor_mcps(editors: Dict[str, Any], installed_mcps: List[Dict[str, Any]]):
    """Configura MCPs nos editores"""
    print("\n⚙️ Configurando MCPs nos Editores")
    print("=" * 50)
    
    for editor_name, editor_info in editors.items():
        print(f"\n📝 Configurando {editor_name.upper()}:")
        
        config_path = editor_info["config_path"]
        
        # Ler configuração atual
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
        
        # Configurar MCPs baseado no editor
        if editor_name == "cursor":
            if "mcpServers" not in config:
                config["mcpServers"] = {}
            
            for mcp in installed_mcps:
                config["mcpServers"][mcp["name"]] = {
                    "command": "npx",
                    "args": ["-y", mcp["npm_package"], "--port", str(mcp["port"])]
                }
                
        elif editor_name == "vscode":
            if "mcp.servers" not in config:
                config["mcp.servers"] = {}
            
            for mcp in installed_mcps:
                config["mcp.servers"][mcp["name"]] = {
                    "command": "npx",
                    "args": ["-y", mcp["npm_package"], "--port", str(mcp["port"])]
                }
        
        # Salvar configuração
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ {len(installed_mcps)} MCPs configurados")
            
        except Exception as e:
            print(f"  ❌ Erro ao salvar configuração: {e}")

def create_usage_examples(installed_mcps: List[Dict[str, Any]]):
    """Cria exemplos de uso dos MCPs instalados"""
    print("\n📚 Exemplos de Uso")
    print("=" * 50)
    
    examples_file = Path("editor_mcp_examples.md")
    
    with open(examples_file, 'w', encoding='utf-8') as f:
        f.write("# 🎯 Exemplos de Uso - MCPs de Controle de Editores\n\n")
        
        for mcp in installed_mcps:
            f.write(f"## {mcp['name']}\n\n")
            f.write(f"**Descrição**: {mcp['description']}\n\n")
            f.write("**Recursos**:\n")
            for feature in mcp['features']:
                f.write(f"- {feature}\n")
            f.write("\n")
            
            f.write("**Exemplos de Prompts**:\n")
            if "vscode-mcp-server" in mcp['name']:
                f.write("- 'Abra o arquivo main.js no VS Code'\n")
                f.write("- 'Navegue para a linha 50 do arquivo atual'\n")
                f.write("- 'Execute o comando de formatação no arquivo'\n")
            elif "vscode-as-mcp-server" in mcp['name']:
                f.write("- 'Crie uma nova função JavaScript no arquivo atual'\n")
                f.write("- 'Abra o terminal integrado e execute npm install'\n")
                f.write("- 'Mova o cursor para o final da linha'\n")
            elif "github-mcp-server" in mcp['name']:
                f.write("- 'Clone o repositório https://github.com/user/repo'\n")
                f.write("- 'Faça commit das mudanças com a mensagem \"Update code\"'\n")
                f.write("- 'Crie uma nova branch chamada feature'\n")
            
            f.write("\n---\n\n")
    
    print(f"✅ Exemplos salvos em: {examples_file}")

def main():
    """Função principal"""
    print("🎯 Instalador de MCPs de Controle de Editores")
    print("=" * 60)
    print("Baseado nos servidores MCP mais populares:")
    print("- vscode-mcp-server (juehang)")
    print("- vscode-as-mcp-server (acomagu)")
    print("- github-mcp-server (GitHub)")
    print()
    
    # Verificar editores
    editors = check_editor_installations()
    
    if not editors:
        print("\n❌ Nenhum editor encontrado")
        print("Instale o Cursor ou VS Code primeiro")
        return
    
    # Instalar MCPs
    installed_mcps = install_editor_mcps()
    
    if not installed_mcps:
        print("\n❌ Nenhum MCP foi instalado")
        return
    
    # Configurar editores
    configure_editor_mcps(editors, installed_mcps)
    
    # Criar exemplos
    create_usage_examples(installed_mcps)
    
    print("\n" + "=" * 60)
    print("✅ Instalação concluída!")
    print(f"\n📦 MCPs instalados: {len(installed_mcps)}")
    for mcp in installed_mcps:
        print(f"  • {mcp['name']} - {mcp['description']}")
    
    print("\n📚 Próximos passos:")
    print("1. Reinicie o Cursor/VS Code")
    print("2. Teste os MCPs com prompts como:")
    print("   - 'Abra o arquivo main.js no editor'")
    print("   - 'Navegue para a linha 50'")
    print("   - 'Execute o comando de formatação'")
    
    print("\n🔗 Recursos úteis:")
    print("- vscode-mcp-server: https://github.com/juehang/vscode-mcp-server")
    print("- vscode-as-mcp-server: https://github.com/acomagu/vscode-as-mcp-server")
    print("- github-mcp-server: https://github.com/github/github-mcp-server")
    print("- Documentação VS Code: https://code.visualstudio.com/docs/copilot/chat/mcp-servers")

if __name__ == "__main__":
    main() 