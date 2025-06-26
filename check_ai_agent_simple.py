import os
import sys

print("=== DIAGNÓSTICO SIMPLES ai_agent_gui.py ===")
print(f"Diretório: {os.getcwd()}")
print(f"Python: {sys.version}")

# Verificar se arquivo existe
if os.path.exists('ai_agent_gui.py'):
    print("✅ Arquivo ai_agent_gui.py encontrado")
    
    # Verificar tamanho
    size = os.path.getsize('ai_agent_gui.py')
    print(f"Tamanho: {size} bytes")
    
    # Tentar compilar (verificar sintaxe)
    try:
        with open('ai_agent_gui.py', 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, 'ai_agent_gui.py', 'exec')
        print("✅ Sintaxe OK")
    except SyntaxError as e:
        print(f"❌ Erro de sintaxe linha {e.lineno}: {e.msg}")
    except Exception as e:
        print(f"❌ Erro ao verificar sintaxe: {e}")
    
    # Verificar dependências básicas
    deps = ['PyQt5', 'requests', 'json']
    for dep in deps:
        try:
            if dep == 'json':
                import json
                print(f"✅ {dep}")
            elif dep == 'PyQt5':
                import PyQt5
                print(f"✅ {dep}")
            elif dep == 'requests':
                import requests
                print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} não encontrado")
    
    # Tentar importar
    try:
        import ai_agent_gui
        print("✅ Importação bem-sucedida")
        if hasattr(ai_agent_gui, 'AiAgentGUI'):
            print("✅ Classe AiAgentGUI encontrada")
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        
else:
    print("❌ Arquivo ai_agent_gui.py NÃO encontrado")

print("\n=== FIM DO DIAGNÓSTICO ===")