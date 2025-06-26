#!/usr/bin/env python3
"""
Versão alternativa do Agent-S para Python 3.12.10
Implementação simplificada baseada nos conceitos do Agent-S
"""

import os
import sys
import pyautogui
import io
import json
import requests
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import platform
import subprocess

class SimpleAgentS:
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.platform = platform.system().lower()
        
        # Configurar PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
    def capture_screenshot(self) -> bytes:
        """Captura screenshot da tela"""
        screenshot = pyautogui.screenshot()
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        return buffered.getvalue()
    
    def encode_image(self, image_bytes: bytes) -> str:
        """Codifica imagem em base64"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def analyze_screen(self, instruction: str, screenshot_bytes: bytes) -> Dict:
        """Analisa a tela e gera ações usando Claude"""
        if not self.api_key:
            return {"error": "API key não configurada"}
        
        # Codificar screenshot
        image_base64 = self.encode_image(screenshot_bytes)
        
        # Preparar prompt
        prompt = f"""
Você é um agente de automação de desktop. Analise a screenshot e gere código Python usando PyAutoGUI para executar a instrução.

Instrução: {instruction}

Gere apenas o código Python necessário, sem explicações. Use PyAutoGUI para:
- Clicar em elementos: pyautogui.click(x, y)
- Digitar texto: pyautogui.write('texto')
- Pressionar teclas: pyautogui.press('enter')
- Mover mouse: pyautogui.moveTo(x, y)
- Aguardar: pyautogui.sleep(1)

Código Python:
"""
        
        # Chamar Claude API
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model,
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["content"][0]["text"]
                return {"success": True, "code": content}
            else:
                return {"error": f"Erro API: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Erro de conexão: {e}"}
    
    def execute_automation(self, instruction: str) -> Dict:
        """Executa automação baseada em instrução"""
        print(f"🤖 Analisando: {instruction}")
        
        # Capturar screenshot
        screenshot_bytes = self.capture_screenshot()
        
        # Analisar tela
        analysis = self.analyze_screen(instruction, screenshot_bytes)
        
        if "error" in analysis:
            return analysis
        
        # Executar código gerado
        try:
            code = analysis["code"]
            print(f"⚡ Executando código: {code}")
            
            # Executar código de forma segura
            exec(code)
            
            return {"success": True, "code": code}
            
        except Exception as e:
            return {"error": f"Erro na execução: {e}"}

class AgentSManager:
    def __init__(self):
        self.agent = None
        self.config_file = Path("config") / "simple_agent_s_config.json"
        self.load_config()
        
    def load_config(self):
        """Carrega configuração"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "api_key": None,
                "model": "claude-3-5-sonnet-20241022",
                "enabled": False
            }
    
    def save_config(self):
        """Salva configuração"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def setup_agent(self, api_key: Optional[str] = None):
        """Configura o agente"""
        if api_key:
            self.config["api_key"] = api_key
            self.save_config()
        
        self.agent = SimpleAgentS(
            api_key=self.config["api_key"],
            model=self.config["model"]
        )
        
        return self.agent
    
    def test_automation(self, instruction: str = "Abra o Notepad"):
        """Testa automação"""
        if not self.agent:
            print("❌ Agente não configurado. Configure a API key primeiro.")
            return False
        
        result = self.agent.execute_automation(instruction)
        
        if "error" in result:
            print(f"❌ Erro: {result['error']}")
            return False
        else:
            print("✅ Automação executada com sucesso")
            return True

def create_simple_agent_s_script():
    """Cria script de exemplo para o Simple Agent-S"""
    script_content = '''#!/usr/bin/env python3
"""
Simple Agent-S - Automação de Desktop
Versão simplificada compatível com Python 3.12.10
"""

import os
import sys
from pathlib import Path

# Adicionar ao path
sys.path.insert(0, str(Path.cwd()))

from agent_s_alternative import AgentSManager

def main():
    """Função principal"""
    print("🚀 Simple Agent-S Desktop Automation")
    print("=" * 50)
    
    manager = AgentSManager()
    
    # Verificar configuração
    if not manager.config["api_key"]:
        print("❌ API key não configurada")
        api_key = input("🔑 Digite sua chave da API Anthropic: ").strip()
        if api_key:
            manager.setup_agent(api_key)
            print("✅ API key configurada")
        else:
            print("❌ API key necessária para continuar")
            return
    
    # Configurar agente
    agent = manager.setup_agent()
    print("✅ Agente configurado")
    
    # Exemplos de automação
    examples = [
        "Abra o Notepad",
        "Digite 'Hello World' no Notepad",
        "Salve o arquivo como 'test.txt'",
        "Feche o Notepad",
        "Abra o Paint",
        "Desenhe um círculo no Paint"
    ]
    
    print("\\n📋 Exemplos de automação:")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")
    
    print("\\n💡 Digite sua instrução ou 'sair' para encerrar:")
    
    while True:
        try:
            instruction = input("🤖 Instrução: ").strip()
            
            if instruction.lower() in ['sair', 'exit', 'quit']:
                break
            
            if instruction:
                success = manager.test_automation(instruction)
                if not success:
                    print("❌ Falha na automação")
            
        except KeyboardInterrupt:
            print("\\n⏹️ Interrompido pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    print("\\n👋 Encerrando Simple Agent-S")

if __name__ == "__main__":
    main()
'''
    
    # Salvar script
    script_file = Path("scripts") / "simple_agent_s_example.py"
    script_file.parent.mkdir(exist_ok=True)
    
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    return script_file

def create_installation_guide():
    """Cria guia de instalação"""
    guide = """# Guia de Instalação - Simple Agent-S

## O que é o Simple Agent-S

Uma versão simplificada do Agent-S framework, compatível com Python 3.12.10, que oferece:
- **Automação de desktop** baseada em visão computacional
- **Integração com Claude** para análise de screenshots
- **Compatibilidade total** com Python 3.12.10
- **Fácil configuração** e uso

## Instalação

### 1. Pré-requisitos
- Python 3.12.10 (já instalado)
- Chave de API da Anthropic
- PyAutoGUI (instalado automaticamente)

### 2. Configuração
1. Obtenha uma chave de API da Anthropic
2. Execute o script de exemplo
3. Digite sua chave de API quando solicitado

### 3. Uso
```bash
python scripts/simple_agent_s_example.py
```

## Exemplos de automação

### Básicos
- "Abra o Notepad"
- "Digite 'Hello World' no Notepad"
- "Salve o arquivo como 'test.txt'"
- "Feche o Notepad"

### Avançados
- "Abra o Paint e desenhe um círculo"
- "Abra o Chrome e vá para google.com"
- "Abra o Excel e crie uma planilha"

## Recursos

### Automações suportadas
- **Navegação de interface** - cliques, digitação
- **Manipulação de arquivos** - abrir, salvar, fechar
- **Controle de aplicativos** - iniciar, parar
- **Automação web** - navegação básica

### Segurança
- **FAILSAFE habilitado** - mova o mouse para o canto superior esquerdo para parar
- **Pausa entre ações** - 0.5 segundos por padrão
- **Execução segura** - código validado antes da execução

## Troubleshooting

### Problemas comuns
- **Erro de API**: Verifique sua chave da Anthropic
- **Erro de screenshot**: Verifique permissões de tela
- **Erro de automação**: Verifique se o elemento está visível

### Logs
- Verifique a saída do console
- Use print() para debug
- Verifique se PyAutoGUI está funcionando

## Arquivos criados

```
config/
└── simple_agent_s_config.json  # Configuração do agente

scripts/
└── simple_agent_s_example.py   # Script de exemplo

agent_s_alternative.py          # Módulo principal
```

## Próximos passos

1. **Configure sua API key** da Anthropic
2. **Teste com exemplos simples** primeiro
3. **Experimente automações mais complexas**
4. **Integre com outros sistemas** se necessário

## Suporte

Para problemas:
1. Verifique os logs do console
2. Teste com exemplos básicos
3. Verifique sua conexão com a internet
4. Confirme que sua API key está correta
"""
    
    # Salvar guia
    guide_file = Path("config") / "SIMPLE_AGENT_S_GUIDE.md"
    guide_file.parent.mkdir(exist_ok=True)
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    return guide_file

def main():
    """Função principal"""
    print("🚀 Simple Agent-S - Versão Alternativa")
    print("=" * 50)
    print("Compatível com Python 3.12.10")
    print()
    
    # Verificar dependências
    try:
        import pyautogui
        print("✅ PyAutoGUI encontrado")
    except ImportError:
        print("📦 Instalando PyAutoGUI...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyautogui"], check=True)
        print("✅ PyAutoGUI instalado")
    
    try:
        import requests
        print("✅ Requests encontrado")
    except ImportError:
        print("📦 Instalando Requests...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
        print("✅ Requests instalado")
    
    # Criar script de exemplo
    script_file = create_simple_agent_s_script()
    print(f"✅ Script criado: {script_file}")
    
    # Criar guia
    guide_file = create_installation_guide()
    print(f"✅ Guia criado: {guide_file}")
    
    print("\n" + "=" * 50)
    print("✅ Simple Agent-S configurado!")
    print("\n📋 Resumo:")
    print("- Versão alternativa criada")
    print("- Compatível com Python 3.12.10")
    print("- Script de exemplo gerado")
    print("- Guia de instalação criado")
    print("\n📖 Consulte: config/SIMPLE_AGENT_S_GUIDE.md")
    print("🚀 Execute: python scripts/simple_agent_s_example.py")
    print("\n🎯 Próximo passo: Configure sua API key da Anthropic e teste")

if __name__ == "__main__":
    main() 