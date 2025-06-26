#!/usr/bin/env python3
"""
Instalador do Cursor Control MCP Server
Configura automaticamente o servidor MCP para controle avançado do Cursor

Funcionalidades instaladas:
- Controle de terminal do Cursor
- Gerenciamento de prompts e conversas
- Envio de comandos para IA
- Armazenamento persistente
- Backup automático de configurações
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

class CursorControlMCPInstaller:
    def __init__(self):
        self.system = platform.system()
        self.home = Path.home()
        self.current_dir = Path(__file__).parent
        self.cursor_config_paths = self.get_cursor_config_paths()
        
    def get_cursor_config_paths(self) -> List[Path]:
        """Retorna caminhos de configuração do Cursor"""
        if self.system == "Windows":
            return [
                self.home / "AppData" / "Roaming" / "Cursor" / "User",
                self.home / "AppData" / "Local" / "Cursor" / "User",
                self.home / ".cursor"
            ]
        elif self.system == "Darwin":
            return [
                self.home / "Library" / "Application Support" / "Cursor" / "User",
                self.home / ".cursor"
            ]
        else:
            return [
                self.home / ".config" / "Cursor" / "User",
                self.home / ".cursor"
            ]
    
    def find_cursor_mcp_file(self) -> Optional[Path]:
        """Encontra o arquivo mcp.json do Cursor"""
        for config_path in self.cursor_config_paths:
            mcp_file = config_path / "mcp.json"
            if mcp_file.exists():
                return mcp_file
        return None
    
    def check_python_version(self) -> bool:
        """Verifica se a versão do Python é compatível"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            return True
        return False
    
    def check_cursor_installation(self) -> bool:
        """Verifica se o Cursor está instalado"""
        possible_paths = []
        
        if self.system == "Windows":
            possible_paths = [
                self.home / "AppData" / "Local" / "Programs" / "cursor" / "Cursor.exe",
                "cursor.exe"
            ]
        elif self.system == "Darwin":
            possible_paths = [
                "/Applications/Cursor.app",
                "/usr/local/bin/cursor"
            ]
        else:
            possible_paths = [
                "/usr/bin/cursor",
                "/usr/local/bin/cursor",
                self.home / ".local" / "bin" / "cursor"
            ]
        
        for path in possible_paths:
            if isinstance(path, str):
                try:
                    subprocess.run([path, "--version"], capture_output=True, timeout=5)
                    return True
                except:
                    continue
            else:
                if path.exists():
                    return True
        
        return False
    
    def create_server_script(self) -> bool:
        """Cria o script do servidor MCP na localização correta"""
        try:
            # Verificar se o arquivo do servidor existe
            server_file = self.current_dir / "cursor_control_mcp_server.py"
            if not server_file.exists():
                print("❌ Arquivo cursor_control_mcp_server.py não encontrado")
                return False
            
            # Copiar para diretório de configuração do Cursor
            target_dir = self.cursor_config_paths[0]
            target_dir.mkdir(parents=True, exist_ok=True)
            
            target_file = target_dir / "cursor_control_mcp_server.py"
            shutil.copy2(server_file, target_file)
            
            # Tornar executável no Linux/macOS
            if self.system != "Windows":
                os.chmod(target_file, 0o755)
            
            print(f"✅ Servidor MCP copiado para: {target_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar script do servidor: {e}")
            return False
    
    def install_mcp_server(self) -> bool:
        """Instala o servidor MCP no Cursor"""
        try:
            # Encontrar ou criar arquivo mcp.json
            mcp_file = self.find_cursor_mcp_file()
            
            if not mcp_file:
                # Criar novo arquivo
                mcp_file = self.cursor_config_paths[0] / "mcp.json"
                mcp_file.parent.mkdir(parents=True, exist_ok=True)
                config = {"mcpServers": {}}
            else:
                # Ler configuração existente
                with open(mcp_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if "mcpServers" not in config:
                    config["mcpServers"] = {}
            
            # Configuração do servidor MCP
            server_path = mcp_file.parent / "cursor_control_mcp_server.py"
            
            config["mcpServers"]["cursor-control"] = {
                "command": "python",
                "args": [str(server_path)],
                "env": {},
                "description": "Servidor MCP avançado para controle total do Cursor IDE"
            }
            
            # Salvar configuração
            with open(mcp_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Servidor MCP configurado em: {mcp_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao instalar servidor MCP: {e}")
            return False
    
    def create_workspace_config(self) -> bool:
        """Cria configuração MCP específica para o workspace atual"""
        try:
            workspace_cursor_dir = Path(".cursor")
            workspace_cursor_dir.mkdir(exist_ok=True)
            
            workspace_mcp_file = workspace_cursor_dir / "mcp.json"
            
            # Configuração para o workspace atual
            config = {
                "mcpServers": {
                    "cursor-control-local": {
                        "command": "python",
                        "args": [str(self.current_dir / "cursor_control_mcp_server.py")],
                        "env": {
                            "WORKSPACE_PATH": str(Path.cwd())
                        },
                        "description": "Servidor MCP de controle do Cursor para este workspace"
                    }
                }
            }
            
            with open(workspace_mcp_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configuração do workspace criada: {workspace_mcp_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar configuração do workspace: {e}")
            return False
    
    def create_usage_examples(self) -> bool:
        """Cria exemplos de uso do servidor MCP"""
        try:
            examples_dir = Path(".cursor") / "examples"
            examples_dir.mkdir(parents=True, exist_ok=True)
            
            # Exemplo de prompts
            prompts_example = {
                "prompts_examples": [
                    {
                        "title": "Análise de Código",
                        "content": "Analise o código em {file_path} e sugira melhorias de performance e legibilidade.",
                        "category": "code-review",
                        "tags": "análise, performance, legibilidade"
                    },
                    {
                        "title": "Documentação Automática",
                        "content": "Crie documentação completa para a função {function_name} incluindo parâmetros, retorno e exemplos de uso.",
                        "category": "documentation",
                        "tags": "docs, função, exemplos"
                    },
                    {
                        "title": "Debug de Erro",
                        "content": "Analise o erro: {error_message} e sugira soluções específicas para o contexto do projeto.",
                        "category": "debugging",
                        "tags": "erro, debug, solução"
                    }
                ]
            }
            
            with open(examples_dir / "prompts_examples.json", 'w', encoding='utf-8') as f:
                json.dump(prompts_example, f, indent=2, ensure_ascii=False)
            
            # Exemplo de comandos
            commands_example = {
                "terminal_commands": [
                    {
                        "name": "Executar testes",
                        "command": "python -m pytest tests/ -v",
                        "description": "Executa todos os testes com verbose"
                    },
                    {
                        "name": "Instalar dependências",
                        "command": "pip install -r requirements.txt",
                        "description": "Instala dependências do projeto"
                    },
                    {
                        "name": "Análise de código",
                        "command": "flake8 . --max-line-length=88",
                        "description": "Executa análise de código com flake8"
                    }
                ]
            }
            
            with open(examples_dir / "commands_examples.json", 'w', encoding='utf-8') as f:
                json.dump(commands_example, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Exemplos criados em: {examples_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar exemplos: {e}")
            return False
    
    def create_readme(self) -> bool:
        """Cria README com instruções de uso"""
        try:
            readme_content = """# Cursor Control MCP Server

## Funcionalidades Instaladas

### 🖥️ Controle de Terminal
- `execute_terminal_command`: Executa comandos no terminal
- `create_terminal_session`: Cria sessões persistentes de terminal
- `list_terminal_sessions`: Lista sessões ativas

### 💬 Gerenciamento de Prompts
- `save_prompt`: Salva prompts para reutilização
- `search_prompts`: Busca prompts por categoria/tags
- `use_prompt`: Usa prompts salvos com substituição de variáveis

### 🤖 Controle de Conversas
- `start_conversation`: Inicia nova conversa com IA
- `send_message_to_cursor`: Envia mensagens para IA do Cursor
- `get_conversation_history`: Recupera histórico de conversas

### 📁 Controle do Editor
- `open_file_in_cursor`: Abre arquivos no Cursor
- `create_file_in_cursor`: Cria novos arquivos
- `execute_cursor_command`: Executa comandos do Cursor

### ⚙️ Configuração e Status
- `get_cursor_status`: Obtém status do Cursor e MCPs
- `configure_cursor_mcp`: Configura novos MCPs
- `backup_cursor_config`: Faz backup das configurações

## Como Usar

### 1. Comandos de Terminal
```
Prompt: "Execute o comando 'python --version' no terminal"
Prompt: "Crie uma sessão de terminal chamada 'dev' no diretório src/"
```

### 2. Gerenciamento de Prompts
```
Prompt: "Salve este prompt: 'Analise o código em {file_path}' na categoria 'code-review'"
Prompt: "Busque prompts relacionados a 'documentação'"
Prompt: "Use o prompt de análise de código para o arquivo main.py"
```

### 3. Controle de Conversas
```
Prompt: "Inicie uma conversa sobre 'Refatoração do módulo auth'"
Prompt: "Envie mensagem para o Cursor: 'Como melhorar a performance desta função?'"
```

### 4. Controle do Editor
```
Prompt: "Abra o arquivo src/main.py na linha 45"
Prompt: "Crie um novo arquivo config.py com configurações básicas"
```

## Arquivos Criados

- `.cursor/mcp.json`: Configuração MCP do workspace
- `.cursor/conversations.db`: Banco de conversas
- `.cursor/prompts.db`: Banco de prompts
- `.cursor/examples/`: Exemplos de uso
- `.cursor/backups/`: Backups automáticos

## Próximos Passos

1. Reinicie o Cursor para carregar o servidor MCP
2. Teste com: "Qual é o status do Cursor e MCPs?"
3. Explore os exemplos em `.cursor/examples/`
4. Configure prompts personalizados para seu workflow
"""
            
            with open(".cursor/README_MCP.md", 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print("✅ README criado: .cursor/README_MCP.md")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar README: {e}")
            return False
    
    def run_installation(self) -> bool:
        """Executa o processo completo de instalação"""
        print("🎯 Cursor Control MCP Server - Instalador")
        print("=" * 50)
        
        # Verificações preliminares
        print("\n📋 Verificando pré-requisitos...")
        
        if not self.check_python_version():
            print("❌ Python 3.8+ é necessário")
            return False
        print("✅ Python compatível")
        
        if not self.check_cursor_installation():
            print("⚠️  Cursor não encontrado (pode ser instalado depois)")
        else:
            print("✅ Cursor encontrado")
        
        # Instalação
        print("\n🚀 Iniciando instalação...")
        
        steps = [
            ("Criando script do servidor", self.create_server_script),
            ("Instalando servidor MCP", self.install_mcp_server),
            ("Configurando workspace", self.create_workspace_config),
            ("Criando exemplos", self.create_usage_examples),
            ("Gerando documentação", self.create_readme)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📦 {step_name}...")
            if not step_func():
                print(f"❌ Falha em: {step_name}")
                return False
        
        return True
    
    def show_final_instructions(self):
        """Mostra instruções finais"""
        print("\n" + "=" * 50)
        print("✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 50)
        
        print("\n📚 Próximos passos:")
        print("1. Reinicie o Cursor para carregar o servidor MCP")
        print("2. Teste com: 'Qual é o status do Cursor e MCPs?'")
        print("3. Explore os exemplos em .cursor/examples/")
        print("4. Leia a documentação em .cursor/README_MCP.md")
        
        print("\n🔧 Comandos de teste:")
        print("- 'Execute o comando ls no terminal'")
        print("- 'Salve um prompt de análise de código'")
        print("- 'Abra o arquivo main.py no Cursor'")
        print("- 'Crie uma sessão de terminal para desenvolvimento'")
        
        print("\n💾 Arquivos criados:")
        print("- Configuração MCP global e local")
        print("- Banco de dados de conversas e prompts")
        print("- Exemplos e documentação")
        print("- Sistema de backup automático")
        
        print("\n🎉 O Cursor agora possui controle total via MCP!")

def main():
    """Função principal"""
    installer = CursorControlMCPInstaller()
    
    try:
        if installer.run_installation():
            installer.show_final_instructions()
        else:
            print("\n❌ Instalação falhou")
            print("Verifique os erros acima e tente novamente")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Instalação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 