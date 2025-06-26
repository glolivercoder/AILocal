#!/usr/bin/env python3
"""
Integração com Agent-S Framework
Baseado em: https://github.com/simular-ai/Agent-S.git
"""

import subprocess
import sys
import os
import platform
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class AgentSIntegration:
    def __init__(self):
        self.repo_url = "https://github.com/simular-ai/Agent-S.git"
        self.installation_path = Path("agents") / "agent-s"
        self.platform = platform.system().lower()
        
    def check_prerequisites(self) -> Tuple[bool, str]:
        """Verifica pré-requisitos para o Agent-S"""
        print("🔍 Verificando pré-requisitos para Agent-S...")
        
        # Verificar Python
        success, output = self.run_command("python --version", "Verificando Python")
        if not success:
            return False, "Python não encontrado"
        
        # Verificar pip
        success, output = self.run_command("pip --version", "Verificando pip")
        if not success:
            return False, "pip não encontrado"
        
        # Verificar git
        success, output = self.run_command("git --version", "Verificando git")
        if not success:
            return False, "git não encontrado"
        
        return True, "Todos os pré-requisitos atendidos"
    
    def run_command(self, command: str, description: str = "") -> Tuple[bool, str]:
        """Executa um comando e retorna o resultado"""
        if description:
            print(f"🔄 {description}...")
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                if description:
                    print(f"✅ {description} - Sucesso")
                return True, result.stdout
            else:
                if description:
                    print(f"❌ {description} - Erro: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            if description:
                print(f"❌ {description} - Exceção: {e}")
            return False, str(e)
    
    def install_agent_s(self) -> Tuple[bool, str]:
        """Instala o Agent-S framework"""
        print("\n📦 Instalando Agent-S Framework...")
        
        # Criar diretório
        self.installation_path.mkdir(parents=True, exist_ok=True)
        
        # Clonar repositório
        success, output = self.run_command(
            f"git clone {self.repo_url} {self.installation_path}",
            "Clonando repositório Agent-S"
        )
        if not success:
            return False, f"Erro ao clonar: {output}"
        
        # Instalar dependências Python
        requirements_file = self.installation_path / "requirements.txt"
        if requirements_file.exists():
            success, output = self.run_command(
                f"pip install -r {requirements_file}",
                "Instalando dependências Python"
            )
            if not success:
                return False, f"Erro ao instalar dependências: {output}"
        
        # Instalar o pacote
        success, output = self.run_command(
            f"cd {self.installation_path} && pip install -e .",
            "Instalando Agent-S"
        )
        if not success:
            return False, f"Erro ao instalar Agent-S: {output}"
        
        return True, f"Agent-S instalado em: {self.installation_path}"
    
    def create_agent_s_config(self) -> Tuple[bool, str]:
        """Cria configuração para o Agent-S"""
        print("\n⚙️ Criando configuração Agent-S...")
        
        config = {
            "agent_s": {
                "enabled": True,
                "installation_path": str(self.installation_path),
                "platform": self.platform,
                "models": {
                    "default_provider": "anthropic",
                    "default_model": "claude-3-5-sonnet-20241022",
                    "grounding_model_provider": "anthropic",
                    "grounding_model": "claude-3-5-sonnet-20241022"
                },
                "settings": {
                    "action_space": "pyautogui",
                    "observation_type": "screenshot",
                    "search_engine": "Perplexica",
                    "embedding_engine_type": "openai"
                }
            }
        }
        
        # Salvar configuração
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "agent_s_config.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return True, f"Configuração salva em: {config_file}"
    
    def create_agent_s_script(self) -> Tuple[bool, str]:
        """Cria script de exemplo para usar o Agent-S"""
        print("\n📝 Criando script de exemplo...")
        
        script_content = '''#!/usr/bin/env python3
"""
Exemplo de uso do Agent-S para automação de desktop
"""

import pyautogui
import io
import os
from pathlib import Path

# Adicionar o Agent-S ao path
agent_s_path = Path("agents/agent-s")
if agent_s_path.exists():
    sys.path.insert(0, str(agent_s_path))

try:
    from gui_agents.s2.agents.agent_s import AgentS2
    from gui_agents.s2.agents.grounding import OSWorldACI
except ImportError:
    print("❌ Agent-S não encontrado. Execute o instalador primeiro.")
    sys.exit(1)

def setup_agent_s():
    """Configura o Agent-S"""
    
    # Configuração do modelo principal
    engine_params = {
        "engine_type": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        # "base_url": "sua_url_custom",  # Opcional
        # "api_key": "sua_api_key"       # Opcional
    }
    
    # Configuração do modelo de grounding
    grounding_model_provider = "anthropic"
    grounding_model = "claude-3-5-sonnet-20241022"
    grounding_model_resize_width = 1366
    screen_width, screen_height = pyautogui.size()
    
    engine_params_for_grounding = {
        "engine_type": grounding_model_provider,
        "model": grounding_model,
        "grounding_width": grounding_model_resize_width,
        "grounding_height": screen_height * grounding_model_resize_width / screen_width,
    }
    
    # Criar agente de grounding
    grounding_agent = OSWorldACI(
        platform=platform.system().lower(),
        engine_params_for_generation=engine_params,
        engine_params_for_grounding=engine_params_for_grounding
    )
    
    # Criar Agent-S
    agent = AgentS2(
        engine_params,
        grounding_agent,
        platform=platform.system().lower(),
        action_space="pyautogui",
        observation_type="screenshot",
        search_engine="Perplexica",
        embedding_engine_type="openai"
    )
    
    return agent

def execute_automation(agent, instruction: str):
    """Executa uma automação"""
    print(f"🤖 Executando: {instruction}")
    
    # Capturar screenshot
    screenshot = pyautogui.screenshot()
    buffered = io.BytesIO()
    screenshot.save(buffered, format="PNG")
    screenshot_bytes = buffered.getvalue()
    
    # Observação
    obs = {
        "screenshot": screenshot_bytes,
    }
    
    # Prever ação
    info, action = agent.predict(instruction=instruction, observation=obs)
    
    # Executar ação
    if action and len(action) > 0:
        print(f"⚡ Executando ação: {action[0]}")
        exec(action[0])
        return True
    else:
        print("❌ Nenhuma ação gerada")
        return False

def main():
    """Função principal"""
    print("🚀 Agent-S Desktop Automation")
    print("=" * 40)
    
    # Configurar agente
    try:
        agent = setup_agent_s()
        print("✅ Agent-S configurado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao configurar Agent-S: {e}")
        return
    
    # Exemplos de automação
    examples = [
        "Abra o Notepad",
        "Digite 'Hello World' no Notepad",
        "Salve o arquivo como 'test.txt'",
        "Feche o Notepad"
    ]
    
    print("\n📋 Exemplos de automação:")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")
    
    print("\n💡 Digite sua instrução ou 'sair' para encerrar:")
    
    while True:
        try:
            instruction = input("🤖 Instrução: ").strip()
            
            if instruction.lower() in ['sair', 'exit', 'quit']:
                break
            
            if instruction:
                success = execute_automation(agent, instruction)
                if success:
                    print("✅ Automação executada com sucesso")
                else:
                    print("❌ Falha na automação")
            
        except KeyboardInterrupt:
            print("\n⏹️ Interrompido pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    print("\n👋 Encerrando Agent-S")

if __name__ == "__main__":
    main()
'''
        
        # Salvar script
        script_file = Path("scripts") / "agent_s_example.py"
        script_file.parent.mkdir(exist_ok=True)
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return True, f"Script salvo em: {script_file}"
    
    def create_mcp_integration(self) -> Tuple[bool, str]:
        """Cria integração MCP para o Agent-S"""
        print("\n🔗 Criando integração MCP...")
        
        mcp_config = {
            "mcpServers": {
                "agent-s": {
                    "command": "python",
                    "args": ["scripts/agent_s_mcp_server.py"],
                    "env": {}
                }
            }
        }
        
        # Salvar configuração MCP
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        mcp_file = config_dir / "agent_s_mcp_config.json"
        
        with open(mcp_file, 'w', encoding='utf-8') as f:
            json.dump(mcp_config, f, indent=2, ensure_ascii=False)
        
        # Criar servidor MCP
        server_script = '''#!/usr/bin/env python3
"""
Servidor MCP para Agent-S
"""

import json
import sys
from pathlib import Path

# Adicionar Agent-S ao path
agent_s_path = Path("agents/agent-s")
if agent_s_path.exists():
    sys.path.insert(0, str(agent_s_path))

try:
    from gui_agents.s2.agents.agent_s import AgentS2
    from gui_agents.s2.agents.grounding import OSWorldACI
    import pyautogui
    import io
except ImportError:
    print("❌ Agent-S não encontrado")
    sys.exit(1)

class AgentSMCP:
    def __init__(self):
        self.agent = self.setup_agent()
    
    def setup_agent(self):
        """Configura o Agent-S"""
        # Configuração básica
        engine_params = {
            "engine_type": "anthropic",
            "model": "claude-3-5-sonnet-20241022"
        }
        
        grounding_agent = OSWorldACI(
            platform=platform.system().lower(),
            engine_params_for_generation=engine_params,
            engine_params_for_grounding=engine_params
        )
        
        return AgentS2(
            engine_params,
            grounding_agent,
            platform=platform.system().lower(),
            action_space="pyautogui",
            observation_type="screenshot"
        )
    
    def execute_automation(self, instruction: str):
        """Executa automação"""
        try:
            # Capturar screenshot
            screenshot = pyautogui.screenshot()
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            screenshot_bytes = buffered.getvalue()
            
            # Observação
            obs = {"screenshot": screenshot_bytes}
            
            # Prever e executar ação
            info, action = self.agent.predict(instruction=instruction, observation=obs)
            
            if action and len(action) > 0:
                exec(action[0])
                return {"success": True, "action": action[0]}
            else:
                return {"success": False, "error": "Nenhuma ação gerada"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    """Servidor MCP"""
    agent_mcp = AgentSMCP()
    
    print("🚀 Agent-S MCP Server iniciado")
    print("📝 Use: agent_s_automate <instrução>")
    
    while True:
        try:
            line = input().strip()
            if not line:
                continue
            
            if line.startswith("agent_s_automate "):
                instruction = line[17:]  # Remove "agent_s_automate "
                result = agent_mcp.execute_automation(instruction)
                print(json.dumps(result))
            elif line == "quit":
                break
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}))

if __name__ == "__main__":
    main()
'''
        
        # Salvar servidor MCP
        server_file = Path("scripts") / "agent_s_mcp_server.py"
        server_file.parent.mkdir(exist_ok=True)
        
        with open(server_file, 'w', encoding='utf-8') as f:
            f.write(server_script)
        
        return True, f"Integração MCP criada: {mcp_file}"
    
    def create_installation_guide(self) -> Tuple[bool, str]:
        """Cria guia de instalação"""
        print("\n📖 Criando guia de instalação...")
        
        guide = f"""# Guia de Instalação - Agent-S Framework

## O que é o Agent-S

O [Agent-S](https://github.com/simular-ai/Agent-S.git) é um framework de automação de desktop que:
- **Usa computadores como humanos** - automação visual e de interface
- **Suporta múltiplas plataformas** - Windows, macOS, Linux
- **Integra com MCPs** - pode usar o protocolo MCP para comunicação
- **Usa screenshots** - automação baseada em visão computacional

## O que foi instalado

✅ Framework Agent-S clonado do repositório
✅ Dependências Python instaladas
✅ Configuração criada
✅ Scripts de exemplo gerados
✅ Integração MCP configurada

## Arquivos criados

```
agents/
└── agent-s/                    # Framework Agent-S
    ├── gui_agents/             # Bibliotecas principais
    ├── requirements.txt        # Dependências
    └── README.md               # Documentação

config/
├── agent_s_config.json         # Configuração do Agent-S
└── agent_s_mcp_config.json     # Configuração MCP

scripts/
├── agent_s_example.py          # Script de exemplo
└── agent_s_mcp_server.py       # Servidor MCP
```

## Como usar

### 1. Configuração básica

1. Configure suas chaves de API no arquivo `.env`:
```bash
ANTHROPIC_API_KEY=sua_chave_aqui
OPENAI_API_KEY=sua_chave_aqui
```

2. Execute o script de exemplo:
```bash
python scripts/agent_s_example.py
```

### 2. Exemplos de automação

```python
# Abrir aplicativo
execute_automation(agent, "Abra o Notepad")

# Digitar texto
execute_automation(agent, "Digite 'Hello World' no Notepad")

# Salvar arquivo
execute_automation(agent, "Salve o arquivo como 'test.txt'")

# Fechar aplicativo
execute_automation(agent, "Feche o Notepad")
```

### 3. Integração com MCP

O Agent-S pode ser usado como um servidor MCP:

1. Inicie o servidor MCP:
```bash
python scripts/agent_s_mcp_server.py
```

2. Configure no Cursor:
```json
{{
  "mcpServers": {{
    "agent-s": {{
      "command": "python",
      "args": ["scripts/agent_s_mcp_server.py"],
      "env": {{}}
    }}
  }}
}}
```

## Recursos

### Automações suportadas
- **Navegação de interface** - cliques, digitação, scroll
- **Manipulação de arquivos** - abrir, salvar, fechar
- **Controle de aplicativos** - iniciar, parar, configurar
- **Automação web** - navegação, preenchimento de formulários
- **Automação de desktop** - qualquer tarefa visual

### Modelos suportados
- **Anthropic Claude** - Claude 3.5 Sonnet, Claude 3 Opus
- **OpenAI GPT** - GPT-4, GPT-4 Turbo
- **Google Gemini** - Gemini Pro, Gemini Ultra
- **Modelos locais** - via HuggingFace, vLLM

## Troubleshooting

### Problemas comuns
- **Erro de API**: Verifique suas chaves de API
- **Erro de importação**: Execute `pip install -e .` no diretório agent-s
- **Erro de screenshot**: Verifique permissões de tela
- **Erro de automação**: Verifique se o elemento está visível na tela

### Logs
- Verifique a saída do console para erros
- Use `print()` para debug no script
- Consulte a documentação oficial do Agent-S

## Recursos adicionais

- [Repositório oficial](https://github.com/simular-ai/Agent-S.git)
- [Documentação](https://github.com/simular-ai/Agent-S#readme)
- [Exemplos](https://github.com/simular-ai/Agent-S/tree/main/examples)
- [Paper](https://arxiv.org/abs/2410.08164)

## Suporte

Para problemas específicos:
1. Verifique os logs do console
2. Consulte a documentação oficial
3. Abra uma issue no repositório GitHub
4. Verifique se todas as dependências estão instaladas
"""
        
        # Salvar guia
        guide_file = Path("config") / "AGENT_S_GUIDE.md"
        guide_file.parent.mkdir(exist_ok=True)
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)
        
        return True, f"Guia salvo em: {guide_file}"

def main():
    """Função principal"""
    print("🚀 Instalador Agent-S Framework")
    print("=" * 50)
    print("Baseado em: https://github.com/simular-ai/Agent-S.git")
    print()
    
    integration = AgentSIntegration()
    
    # Verificar pré-requisitos
    success, message = integration.check_prerequisites()
    if not success:
        print(f"❌ {message}")
        return
    
    # Instalar Agent-S
    success, message = integration.install_agent_s()
    if not success:
        print(f"❌ {message}")
        return
    
    # Criar configuração
    success, message = integration.create_agent_s_config()
    if not success:
        print(f"❌ {message}")
        return
    
    # Criar script de exemplo
    success, message = integration.create_agent_s_script()
    if not success:
        print(f"❌ {message}")
        return
    
    # Criar integração MCP
    success, message = integration.create_mcp_integration()
    if not success:
        print(f"❌ {message}")
        return
    
    # Criar guia
    success, message = integration.create_installation_guide()
    if not success:
        print(f"❌ {message}")
        return
    
    print("\n" + "=" * 50)
    print("✅ Instalação concluída!")
    print("\n📋 Resumo:")
    print("- Framework Agent-S instalado")
    print("- Configurações criadas")
    print("- Scripts de exemplo gerados")
    print("- Integração MCP configurada")
    print("\n📖 Consulte: config/AGENT_S_GUIDE.md")
    print("⚙️ Configuração: config/agent_s_config.json")
    print("🚀 Exemplo: python scripts/agent_s_example.py")
    print("\n🎯 Próximo passo: Configure suas chaves de API e teste a automação")

if __name__ == "__main__":
    main() 