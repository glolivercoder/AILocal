#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher Simples e Robusto
Tenta executar a interface principal com máxima compatibilidade
"""

import sys
import os
from pathlib import Path

def try_import_and_run(module_name, class_name=None):
    """Tenta importar e executar um módulo"""
    try:
        print(f"🔄 Tentando carregar {module_name}...")
        
        # Importar módulo
        module = __import__(module_name)
        
        if class_name:
            # Executar classe específica
            cls = getattr(module, class_name)
            app = cls()
            app.run()
        else:
            # Executar função main se existir
            if hasattr(module, 'main'):
                module.main()
            else:
                print(f"⚠️  {module_name} carregado mas sem função main")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação em {module_name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar {module_name}: {e}")
        return False

def main():
    """Função principal do launcher"""
    print("🚀 LAUNCHER SIMPLES - Agente Especialista")
    print("=" * 50)
    
    # Verificar diretório
    current_dir = Path.cwd()
    print(f"📁 Diretório: {current_dir}")
    
    # Lista de módulos para tentar
    modules_to_try = [
        ("ai_agent_gui", None),
        ("integrated_knowledge_interface", None),
        ("start_main_interface", None),
        ("app", None)
    ]
    
    # Tentar cada módulo
    for module_name, class_name in modules_to_try:
        module_file = current_dir / f"{module_name}.py"
        if module_file.exists():
            print(f"
📄 Encontrado: {module_file.name}")
            if try_import_and_run(module_name, class_name):
                print(f"✅ {module_name} executado com sucesso!")
                return
        else:
            print(f"❌ Não encontrado: {module_name}.py")
    
    # Se chegou aqui, nada funcionou
    print("
❌ Nenhuma interface pôde ser executada")
    print("
💡 Diagnósticos disponíveis:")
    print("   python diagnostico_sistema.py")
    print("   python verificar_dependencias.py")

if __name__ == "__main__":
    main()
