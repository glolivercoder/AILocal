#!/usr/bin/env python3
"""
Script para configurar MCPs nos editores (Cursor e VS Code)
Baseado na documentação oficial: https://github.com/modelcontextprotocol/servers
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

def setup_github_token():
    """Configura token do GitHub para evitar rate limiting"""
    print("🔑 Configuração do GitHub Token")
    print("=" * 50)
    
    token = input("Digite seu GitHub Personal Access Token (ou pressione Enter para pular): ").strip()
    
    if token:
        # Salvar em variável de ambiente
        os.environ["GITHUB_TOKEN"] = token
        
        # Salvar em arquivo .env
        env_file = Path(".env")
        with open(env_file, "a") as f:
            f.write(f"\nGITHUB_TOKEN={token}\n")
        
        print("✅ Token do GitHub configurado")
        return True
    else:
        print("⚠️ Token não configurado - rate limit reduzido")
        return False

def check_editors():
    """Verifica editores instalados"""
    print("\n🔍 Verificando Editores Instalados")
    print("=" * 50)
    
    editors = {
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
        },
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

def install_mcp_to_editor(editor_name: str, config_path: Path, mcp_name: str, mcp_package: str, port: int):
    """Instala MCP em um editor específico"""
    try:
        print(f"\n📦 Instalando {mcp_name} no {editor_name.upper()}")
        
        # Ler configuração atual
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Configurar MCP baseado no editor
        if editor_name == "cursor":
            if "mcpServers" not in config:
                config["mcpServers"] = {}
            
            config["mcpServers"][mcp_name] = {
                "command": "npx",
                "args": ["-y", mcp_package, "--port", str(port)]
            }
            
        elif editor_name == "vscode":
            if "mcp.servers" not in config:
                config["mcp.servers"] = {}
            
            config["mcp.servers"][mcp_name] = {
                "command": "npx",
                "args": ["-y", mcp_package, "--port", str(port)]
            }
        
        # Salvar configuração
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ {mcp_name} configurado no {editor_name.upper()}")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao configurar {mcp_name}: {e}")
        return False

def install_recommended_mcps(editors: Dict[str, Any]):
    """Instala MCPs recomendados"""
    print("\n🚀 Instalando MCPs Recomendados")
    print("=" * 50)
    
    # MCPs recomendados baseados na documentação oficial
    recommended_mcps = [
        {
            "name": "filesystem",
            "package": "@modelcontextprotocol/server-filesystem",
            "description": "Acesso seguro a arquivos",
            "port": 3333
        },
        {
            "name": "github",
            "package": "@modelcontextprotocol/server-github",
            "description": "API do GitHub",
            "port": 3334
        },
        {
            "name": "postgres",
            "package": "@modelcontextprotocol/server-postgres",
            "description": "Banco de dados PostgreSQL",
            "port": 3335
        },
        {
            "name": "brave-search",
            "package": "@modelcontextprotocol/server-brave-search",
            "description": "Busca na web",
            "port": 3336
        },
        {
            "name": "memory",
            "package": "@modelcontextprotocol/server-memory",
            "description": "Memória e knowledge graph",
            "port": 3337
        }
    ]
    
    for editor_name, editor_info in editors.items():
        print(f"\n📝 Configurando {editor_name.upper()}:")
        
        for mcp in recommended_mcps:
            success = install_mcp_to_editor(
                editor_name,
                editor_info["config_path"],
                mcp["name"],
                mcp["package"],
                mcp["port"]
            )
            
            if success:
                print(f"  ✅ {mcp['name']} - {mcp['description']}")
            else:
                print(f"  ❌ {mcp['name']} - Falha na instalação")

def create_mcp_config_template():
    """Cria template de configuração MCP"""
    print("\n📋 Criando Template de Configuração")
    print("=" * 50)
    
    template = {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
            },
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_TOKEN>"
                }
            },
            "postgres": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
            },
            "brave-search": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-brave-search"]
            },
            "memory": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-memory"]
            }
        }
    }
    
    # Salvar template
    template_file = Path("mcp_config_template.json")
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Template salvo em: {template_file}")
    print("\n💡 Use este template como base para configurar MCPs manualmente")

def main():
    """Função principal"""
    print("🎯 Configurador de MCPs para Editores")
    print("=" * 60)
    print("Baseado na documentação oficial: https://github.com/modelcontextprotocol/servers")
    print()
    
    # Configurar GitHub token
    setup_github_token()
    
    # Verificar editores
    editors = check_editors()
    
    if not editors:
        print("\n❌ Nenhum editor encontrado")
        print("Instale o Cursor ou VS Code primeiro")
        return
    
    # Instalar MCPs recomendados
    install_recommended_mcps(editors)
    
    # Criar template
    create_mcp_config_template()
    
    print("\n" + "=" * 60)
    print("✅ Configuração concluída!")
    print("\n📚 Próximos passos:")
    print("1. Reinicie o Cursor/VS Code")
    print("2. Configure tokens de API nos MCPs (GitHub, etc.)")
    print("3. Teste os MCPs com prompts como:")
    print("   - 'Liste os arquivos no diretório atual'")
    print("   - 'Busque informações sobre MCP no GitHub'")
    print("   - 'Conecte ao banco de dados PostgreSQL'")
    
    print("\n🔗 Recursos úteis:")
    print("- Documentação oficial: https://github.com/modelcontextprotocol/servers")
    print("- MCP Hub: https://mcp.natoma.id")
    print("- MCP Marketplace: https://mcp.run")

if __name__ == "__main__":
    main() 