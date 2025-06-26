#!/usr/bin/env python3
"""
Script de instalação e configuração do Stata MCP
Baseado em: https://github.com/hanlulong/stata-mcp.git
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description=""):
    """Executa um comando e retorna o resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Sucesso")
            return True, result.stdout
        else:
            print(f"❌ {description} - Erro: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {description} - Exceção: {e}")
        return False, str(e)

def check_prerequisites():
    """Verifica pré-requisitos"""
    print("🔍 Verificando pré-requisitos...")
    
    # Verificar Python
    success, output = run_command("python --version", "Verificando Python")
    if not success:
        print("❌ Python não encontrado. Instale Python 3.11+ primeiro.")
        return False
    
    # Verificar npm
    success, output = run_command("npm --version", "Verificando npm")
    if not success:
        print("❌ npm não encontrado. Instale Node.js primeiro.")
        return False
    
    # Verificar git
    success, output = run_command("git --version", "Verificando git")
    if not success:
        print("❌ git não encontrado. Instale Git primeiro.")
        return False
    
    print("✅ Todos os pré-requisitos atendidos!")
    return True

def install_stata_mcp_extension():
    """Instala a extensão Stata MCP"""
    print("\n📦 Instalando extensão Stata MCP...")
    
    # Opção 1: Via marketplace (se code estiver disponível)
    success, output = run_command("code --version", "Verificando VS Code CLI")
    if success:
        print("🔄 Tentando instalar via marketplace...")
        success, output = run_command(
            "code --install-extension deepecon.stata-mcp",
            "Instalando extensão via marketplace"
        )
        if success:
            return True
    
    # Opção 2: Via Git
    print("🔄 Instalando via Git...")
    
    # Criar diretório temporário
    temp_dir = Path("temp") / "stata-mcp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Clonar repositório
    success, output = run_command(
        f"git clone https://github.com/hanlulong/stata-mcp.git {temp_dir}",
        "Clonando repositório Stata MCP"
    )
    if not success:
        return False
    
    # Verificar se há requirements.txt
    requirements_file = temp_dir / "requirements.txt"
    if requirements_file.exists():
        success, output = run_command(
            f"pip install -r {requirements_file}",
            "Instalando dependências Python"
        )
        if not success:
            return False
    
    # Verificar se há package.json
    package_file = temp_dir / "package.json"
    if package_file.exists():
        success, output = run_command(
            f"cd {temp_dir} && npm install",
            "Instalando dependências Node.js"
        )
        if not success:
            return False
    
    print(f"✅ Extensão instalada em: {temp_dir}")
    return True

def configure_cursor_mcp():
    """Configura o Stata MCP no Cursor"""
    print("\n⚙️ Configurando Stata MCP no Cursor...")
    
    try:
        from cursor_mcp_manager import CursorMCPManager
        
        manager = CursorMCPManager()
        
        # Adicionar Stata MCP à configuração
        stata_config = {
            "name": "Stata MCP",
            "package": "stata-mcp",
            "port": 4000,
            "description": "Integração Stata via MCP (análise estatística)",
            "category": "statistics"
        }
        
        manager.mcps["stata-mcp"] = stata_config
        
        # Instalar no Cursor
        success, message = manager.install_mcps_to_cursor(["stata-mcp"])
        
        if success:
            print(f"✅ {message}")
            return True
        else:
            print(f"❌ {message}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao configurar Cursor: {e}")
        return False

def create_stata_mcp_config():
    """Cria arquivo de configuração para o Stata MCP"""
    print("\n📄 Criando configuração Stata MCP...")
    
    config = {
        "mcpServers": {
            "stata-mcp": {
                "command": "npx",
                "args": ["stata-mcp-server", "--port", "4000"],
                "env": {}
            }
        }
    }
    
    # Salvar configuração
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "stata_mcp_config.json"
    
    import json
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuração salva em: {config_file}")
    return True

def create_installation_guide():
    """Cria guia de instalação"""
    print("\n📖 Criando guia de instalação...")
    
    guide = """# Guia de Instalação - Stata MCP

## O que foi instalado

✅ Extensão Stata MCP clonada do repositório
✅ Dependências Python instaladas
✅ Configuração MCP criada
✅ Integração com Cursor configurada

## Próximos passos

### 1. Instalar Stata
- Baixe e instale Stata 17+ (MP, SE ou BE)
- Certifique-se de que o Stata está no PATH do sistema

### 2. Configurar Cursor
1. Abra o Cursor
2. Vá para Configurações (Ctrl+,)
3. Procure por "MCP" ou "Model Context Protocol"
4. Adicione a configuração do arquivo: config/stata_mcp_config.json

### 3. Testar integração
1. Abra um arquivo .do no Cursor
2. A extensão deve aparecer na barra de status
3. Use Ctrl+Shift+P e digite "Stata" para ver comandos

### 4. Configuração avançada
Para configurar edição específica do Stata:
```json
{
  "stata-vscode.stataEdition": "MP"
}
```

## Troubleshooting

### Problemas comuns:
- **Extensão não carrega**: Verifique Python 3.11+
- **Stata não encontrado**: Verifique instalação e PATH
- **Erro de conexão**: Verifique se porta 4000 está livre

### Logs:
- VS Code: View > Output > Stata MCP
- Cursor: Help > Toggle Developer Tools > Console

## Recursos

- [Repositório original](https://github.com/hanlulong/stata-mcp.git)
- [Documentação oficial](https://github.com/hanlulong/stata-mcp#readme)
- [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=deepecon.stata-mcp)

## Suporte

Para problemas específicos:
1. Verifique os logs do editor
2. Consulte a documentação oficial
3. Abra uma issue no repositório GitHub
"""
    
    guide_file = Path("config") / "STATA_MCP_GUIDE.md"
    guide_file.parent.mkdir(exist_ok=True)
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"✅ Guia salvo em: {guide_file}")
    return True

def main():
    """Função principal"""
    print("🚀 Instalador Stata MCP Extension")
    print("=" * 50)
    print("Baseado em: https://github.com/hanlulong/stata-mcp.git")
    print()
    
    # Verificar pré-requisitos
    if not check_prerequisites():
        print("\n❌ Pré-requisitos não atendidos. Instale as dependências primeiro.")
        return
    
    # Instalar extensão
    if not install_stata_mcp_extension():
        print("\n❌ Falha na instalação da extensão.")
        return
    
    # Configurar Cursor
    if not configure_cursor_mcp():
        print("\n⚠️ Falha na configuração do Cursor, mas continuando...")
    
    # Criar configuração
    if not create_stata_mcp_config():
        print("\n❌ Falha na criação da configuração.")
        return
    
    # Criar guia
    if not create_installation_guide():
        print("\n⚠️ Falha na criação do guia.")
    
    print("\n" + "=" * 50)
    print("✅ Instalação concluída!")
    print("\n📋 Resumo:")
    print("- Extensão Stata MCP instalada")
    print("- Configuração MCP criada")
    print("- Guia de instalação gerado")
    print("\n📖 Consulte: config/STATA_MCP_GUIDE.md")
    print("⚙️ Configuração: config/stata_mcp_config.json")
    print("\n🎯 Próximo passo: Instalar Stata e configurar no Cursor")

if __name__ == "__main__":
    main() 