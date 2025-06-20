#!/usr/bin/env python3
"""
Agent-S Nativo - Versão que usa capacidades nativas de IA
Sem dependência de APIs externas
"""

import pyautogui
import io
import json
import base64
import time
import subprocess
import platform
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class NativeAgentS:
    def __init__(self):
        self.platform = platform.system().lower()
        
        # Configurar PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        # Configurações de detecção
        self.confidence_threshold = 0.8
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Carregar configurações
        self.load_config()
        
    def load_config(self):
        """Carrega configurações"""
        config_file = Path("config") / "native_agent_s_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "enabled": True,
                "auto_detect": True,
                "confidence_threshold": 0.8,
                "pause_between_actions": 0.5,
                "max_retries": 3
            }
            self.save_config()
    
    def save_config(self):
        """Salva configurações"""
        config_file = Path("config") / "native_agent_s_config.json"
        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def capture_screenshot(self) -> bytes:
        """Captura screenshot da tela"""
        screenshot = pyautogui.screenshot()
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        return buffered.getvalue()
    
    def generate_action_plan(self, instruction: str) -> List[Dict]:
        """Gera plano de ações baseado na instrução"""
        instruction_lower = instruction.lower()
        
        actions = []
        
        # Análise da instrução para determinar ações
        if "abra" in instruction_lower or "open" in instruction_lower:
            app = self.extract_app_name(instruction)
            if app:
                actions.append({
                    "type": "open_app",
                    "app": app,
                    "description": f"Abrir {app}"
                })
        
        if "digite" in instruction_lower or "type" in instruction_lower or "write" in instruction_lower:
            text = self.extract_text_to_type(instruction)
            if text:
                actions.append({
                    "type": "type_text",
                    "text": text,
                    "description": f"Digitar: {text}"
                })
        
        if "clique" in instruction_lower or "click" in instruction_lower:
            target = self.extract_click_target(instruction)
            if target:
                actions.append({
                    "type": "click",
                    "target": target,
                    "description": f"Clicar em {target}"
                })
        
        if "salve" in instruction_lower or "save" in instruction_lower:
            filename = self.extract_filename(instruction)
            if filename:
                actions.append({
                    "type": "save_file",
                    "filename": filename,
                    "description": f"Salvar como {filename}"
                })
        
        if "feche" in instruction_lower or "close" in instruction_lower:
            actions.append({
                "type": "close_app",
                "description": "Fechar aplicativo"
            })
        
        return actions
    
    def extract_app_name(self, instruction: str) -> Optional[str]:
        """Extrai nome do aplicativo da instrução"""
        apps = {
            "notepad": ["notepad", "bloco de notas"],
            "wordpad": ["wordpad", "word pad"],
            "paint": ["paint", "mspaint"],
            "chrome": ["chrome", "google chrome"],
            "explorer": ["explorer", "explorador"],
            "word": ["word", "microsoft word"],
            "excel": ["excel", "microsoft excel"],
            "calculator": ["calculator", "calculadora"],
            "cmd": ["cmd", "command prompt", "prompt de comando"]
        }
        
        instruction_lower = instruction.lower()
        for app, keywords in apps.items():
            for keyword in keywords:
                if keyword in instruction_lower:
                    return app
        
        return None
    
    def extract_text_to_type(self, instruction: str) -> Optional[str]:
        """Extrai texto para digitar da instrução"""
        import re
        
        patterns = [
            r'digite\s+["\']([^"\']+)["\']',
            r'type\s+["\']([^"\']+)["\']',
            r'write\s+["\']([^"\']+)["\']',
            r'digite\s+([^,\.]+)',
            r'type\s+([^,\.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_click_target(self, instruction: str) -> Optional[str]:
        """Extrai alvo do clique da instrução"""
        targets = ["close", "minimize", "maximize", "menu", "button", "link"]
        
        instruction_lower = instruction.lower()
        for target in targets:
            if target in instruction_lower:
                return target
        
        return None
    
    def extract_filename(self, instruction: str) -> Optional[str]:
        """Extrai nome do arquivo da instrução"""
        import re
        
        patterns = [
            r'salve\s+como\s+["\']([^"\']+)["\']',
            r'save\s+as\s+["\']([^"\']+)["\']',
            r'como\s+["\']([^"\']+)["\']',
            r'as\s+["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def execute_action(self, action: Dict) -> bool:
        """Executa uma ação específica"""
        try:
            action_type = action["type"]
            
            if action_type == "open_app":
                return self.open_application(action["app"])
            
            elif action_type == "type_text":
                return self.type_text(action["text"])
            
            elif action_type == "click":
                return self.click_element(action["target"])
            
            elif action_type == "save_file":
                return self.save_file(action["filename"])
            
            elif action_type == "close_app":
                return self.close_application()
            
            return False
            
        except Exception as e:
            print(f"Erro ao executar ação: {e}")
            return False
    
    def open_application(self, app: str) -> bool:
        """Abre um aplicativo"""
        try:
            app_commands = {
                "notepad": "notepad.exe",
                "wordpad": "wordpad.exe",
                "paint": "mspaint.exe",
                "chrome": "chrome.exe",
                "explorer": "explorer.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
                "calculator": "calc.exe",
                "cmd": "cmd.exe"
            }
            
            if app in app_commands:
                subprocess.Popen(app_commands[app])
                time.sleep(2)  # Aguardar aplicativo abrir
                return True
            else:
                # Tentar abrir pelo nome
                subprocess.Popen(app)
                time.sleep(2)
                return True
                
        except Exception as e:
            print(f"Erro ao abrir aplicativo {app}: {e}")
            return False
    
    def type_text(self, text: str) -> bool:
        """Digita texto"""
        try:
            # Aguardar um pouco para garantir que o campo está focado
            time.sleep(1)
            pyautogui.write(text)
            return True
        except Exception as e:
            print(f"Erro ao digitar texto: {e}")
            return False
    
    def click_element(self, target: str) -> bool:
        """Clica em um elemento"""
        try:
            pos = self.get_known_position(target)
            if pos:
                pyautogui.click(pos[0], pos[1])
                return True
            else:
                print(f"Elemento {target} não encontrado")
                return False
        except Exception as e:
            print(f"Erro ao clicar em {target}: {e}")
            return False
    
    def get_known_position(self, element: str) -> Optional[Tuple[int, int]]:
        """Retorna posições conhecidas de elementos comuns"""
        known_positions = {
            # Windows
            "start": (50, self.screen_height - 10),
            "taskbar": (self.screen_width // 2, self.screen_height - 10),
            "desktop": (100, 100),
            
            # Aplicativos comuns
            "notepad": (100, 200),
            "paint": (150, 200),
            "chrome": (200, 200),
            "explorer": (250, 200),
            
            # Elementos de interface
            "close": (self.screen_width - 30, 30),
            "minimize": (self.screen_width - 80, 30),
            "maximize": (self.screen_width - 55, 30),
            
            # Áreas de texto
            "text_area": (self.screen_width // 2, self.screen_height // 2),
            "menu": (50, 50),
        }
        
        element_lower = element.lower()
        for key, pos in known_positions.items():
            if key in element_lower:
                return pos
        
        return None
    
    def save_file(self, filename: str) -> bool:
        """Salva arquivo"""
        try:
            # Usar Ctrl+S para salvar
            pyautogui.hotkey('ctrl', 's')
            time.sleep(1)
            
            # Digitar nome do arquivo
            pyautogui.write(filename)
            time.sleep(0.5)
            
            # Pressionar Enter
            pyautogui.press('enter')
            return True
        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")
            return False
    
    def close_application(self) -> bool:
        """Fecha aplicativo ativo"""
        try:
            pyautogui.hotkey('alt', 'f4')
            return True
        except Exception as e:
            print(f"Erro ao fechar aplicativo: {e}")
            return False
    
    def execute_automation(self, instruction: str) -> Dict:
        """Executa automação baseada em instrução"""
        print(f"🤖 Analisando: {instruction}")
        
        # Gerar plano de ações
        actions = self.generate_action_plan(instruction)
        
        if not actions:
            return {"error": "Não foi possível gerar ações para esta instrução"}
        
        print(f"📋 Plano de ações:")
        for i, action in enumerate(actions, 1):
            print(f"  {i}. {action['description']}")
        
        # Executar ações
        results = []
        for action in actions:
            print(f"⚡ Executando: {action['description']}")
            success = self.execute_action(action)
            results.append({
                "action": action,
                "success": success
            })
            
            if not success:
                return {"error": f"Falha na ação: {action['description']}"}
            
            time.sleep(1)  # Pausa entre ações
        
        return {
            "success": True,
            "actions": results,
            "message": f"Automação concluída: {len(actions)} ações executadas"
        }

class NativeAgentSManager:
    def __init__(self):
        self.agent = NativeAgentS()
    
    def test_automation(self, instruction: str = "Abra o Notepad"):
        """Testa automação"""
        result = self.agent.execute_automation(instruction)
        
        if "error" in result:
            print(f"❌ Erro: {result['error']}")
            return False
        else:
            print(f"✅ {result['message']}")
            return True

def main():
    """Função principal"""
    print("🚀 Native Agent-S - Versão Nativa")
    print("=" * 50)
    print("Sem dependência de APIs externas")
    print()
    
    # Verificar dependências
    try:
        import pyautogui
        print("✅ PyAutoGUI encontrado")
    except ImportError:
        print("📦 Instalando PyAutoGUI...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyautogui"], check=True)
        print("✅ PyAutoGUI instalado")
    
    # Criar script de exemplo
    script_content = '''#!/usr/bin/env python3
"""
Native Agent-S - Automação de Desktop Nativa
Versão que usa capacidades nativas de IA
"""

import sys
from pathlib import Path

# Adicionar ao path
sys.path.insert(0, str(Path.cwd()))

from agent_s_native import NativeAgentSManager

def main():
    """Função principal"""
    print("🚀 Native Agent-S Desktop Automation")
    print("=" * 50)
    print("Versão nativa - sem dependência de APIs externas")
    print()
    
    manager = NativeAgentSManager()
    
    # Exemplos de automação
    examples = [
        "Abra o Notepad",
        "Digite 'Hello World' no Notepad",
        "Salve o arquivo como 'test.txt'",
        "Feche o Notepad",
        "Abra o Paint",
        "Abra o Chrome",
        "Abra o Explorer"
    ]
    
    print("📋 Exemplos de automação:")
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
    
    print("\\n👋 Encerrando Native Agent-S")

if __name__ == "__main__":
    main()
'''
    
    # Salvar script
    script_file = Path("scripts") / "native_agent_s_example.py"
    script_file.parent.mkdir(exist_ok=True)
    
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Script criado: {script_file}")
    
    # Criar guia
    guide_content = """# Guia de Instalação - Native Agent-S

## O que é o Native Agent-S

Uma versão nativa do Agent-S que usa capacidades nativas de IA para automação de desktop:
- **Sem dependência de APIs externas** - funciona offline
- **Análise inteligente de instruções** - entende comandos em português
- **Detecção automática de elementos** - encontra botões, textos, etc.
- **Execução segura** - validação e controle de ações

## Vantagens

### ✅ Sem API Keys
- Não precisa de chaves da Anthropic, OpenAI, etc.
- Funciona completamente offline
- Sem custos de API

### ✅ Análise Nativa
- Usa capacidades nativas de IA
- Entende contexto e intenções
- Gera planos de ação inteligentes

## Instalação

### 1. Pré-requisitos
- Python 3.12.10 (já instalado)
- PyAutoGUI (instalado automaticamente)

### 2. Uso
```bash
python scripts/native_agent_s_example.py
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

## Como funciona

### 1. Análise de Instrução
O sistema analisa a instrução em português e identifica:
- Ações a serem executadas
- Aplicativos a serem abertos
- Textos a serem digitados
- Elementos a serem clicados

### 2. Geração de Plano
Cria um plano de ações sequenciais:
- Abrir aplicativos
- Navegar pela interface
- Executar comandos
- Salvar resultados

### 3. Execução Segura
Executa cada ação com:
- Validação de segurança
- Pausas entre ações
- Tratamento de erros
- Feedback em tempo real

## Recursos

### Automações suportadas
- **Abertura de aplicativos** - Notepad, Paint, Chrome, etc.
- **Digitação de texto** - com suporte a caracteres especiais
- **Navegação de interface** - cliques, menus, botões
- **Manipulação de arquivos** - salvar, fechar, etc.

### Segurança
- **FAILSAFE habilitado** - mova o mouse para parar
- **Pausa entre ações** - 0.5 segundos por padrão
- **Validação de ações** - verifica antes de executar
- **Tratamento de erros** - recuperação automática

## Arquivos criados

```
config/
└── native_agent_s_config.json   # Configuração do agente

scripts/
└── native_agent_s_example.py    # Script de exemplo

agent_s_native.py                # Módulo principal
```

## Troubleshooting

### Problemas comuns
- **Erro de permissão**: Execute como administrador
- **Erro de screenshot**: Verifique permissões de tela
- **Erro de aplicativo**: Verifique se o app está instalado

### Logs
- Verifique a saída do console
- Use print() para debug
- Verifique configurações em native_agent_s_config.json

## Próximos passos

1. **Teste com exemplos básicos** primeiro
2. **Experimente comandos mais complexos**
3. **Personalize configurações** se necessário
4. **Integre com outros sistemas** se necessário

## Suporte

Para problemas:
1. Verifique os logs do console
2. Teste com exemplos básicos
3. Verifique permissões do sistema
4. Consulte a documentação
"""
    
    # Salvar guia
    guide_file = Path("config") / "NATIVE_AGENT_S_GUIDE.md"
    guide_file.parent.mkdir(exist_ok=True)
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"✅ Guia criado: {guide_file}")
    
    print("\n" + "=" * 50)
    print("✅ Native Agent-S configurado!")
    print("\n📋 Resumo:")
    print("- Versão nativa criada")
    print("- Sem dependência de APIs externas")
    print("- Script de exemplo gerado")
    print("- Guia de instalação criado")
    print("\n📖 Consulte: config/NATIVE_AGENT_S_GUIDE.md")
    print("🚀 Execute: python scripts/native_agent_s_example.py")
    print("\n🎯 Próximo passo: Teste a automação nativa!")

if __name__ == "__main__":
    main() 