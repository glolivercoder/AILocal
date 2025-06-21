#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar diagnóstico do sistema e gerar arquivo de diagnóstico
"""

import sys
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

def executar_diagnostico():
    """Executa o diagnóstico do sistema"""
    print("🔍 Iniciando diagnóstico do sistema...")
    
    try:
        # Importar e executar o diagnóstico
        sys.path.append(os.getcwd())
        from diagnostico_sistema import main as diagnostico_main
        
        print("📊 Executando diagnóstico completo...")
        resultado = diagnostico_main()
        
        print("✅ Diagnóstico concluído!")
        return resultado
        
    except Exception as e:
        print(f"❌ Erro ao executar diagnóstico: {e}")
        
        # Criar diagnóstico básico de erro
        diagnostico_erro = {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e),
            "message": "Falha ao executar diagnóstico completo",
            "basic_checks": {
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "files_exist": {
                    "ai_agent_gui.py": os.path.exists("ai_agent_gui.py"),
                    "diagnostico_sistema.py": os.path.exists("diagnostico_sistema.py"),
                    "start_main_interface.py": os.path.exists("start_main_interface.py")
                }
            }
        }
        
        # Salvar diagnóstico de erro
        with open("Diagnostico.json", 'w', encoding='utf-8') as f:
            json.dump(diagnostico_erro, f, indent=2, ensure_ascii=False)
        
        return diagnostico_erro

def tentar_executar_interface():
    """Tenta executar a interface principal"""
    interfaces = [
        "ai_agent_gui.py",
        "integrated_knowledge_interface.py", 
        "start_main_interface.py"
    ]
    
    for interface in interfaces:
        if os.path.exists(interface):
            print(f"🚀 Tentando executar {interface}...")
            try:
                # Tentar importar primeiro para verificar dependências
                if interface == "ai_agent_gui.py":
                    import ai_agent_gui
                    print(f"✅ {interface} importado com sucesso!")
                    print(f"💡 Execute manualmente: python {interface}")
                    return True
                elif interface == "integrated_knowledge_interface.py":
                    import integrated_knowledge_interface
                    print(f"✅ {interface} importado com sucesso!")
                    print(f"💡 Execute manualmente: python {interface}")
                    return True
                elif interface == "start_main_interface.py":
                    import start_main_interface
                    print(f"✅ {interface} importado com sucesso!")
                    print(f"💡 Execute manualmente: python {interface}")
                    return True
            except Exception as e:
                print(f"❌ Erro ao importar {interface}: {e}")
                continue
    
    print("❌ Nenhuma interface pôde ser importada com sucesso")
    return False

def main():
    """Função principal"""
    print("="*60)
    print("    DIAGNÓSTICO E EXECUÇÃO DO SISTEMA AILOCAL")
    print("="*60)
    print()
    
    # Executar diagnóstico
    resultado_diagnostico = executar_diagnostico()
    
    print()
    print("📋 Arquivo de diagnóstico gerado: Diagnostico.json")
    print()
    
    # Tentar executar interface
    print("🔄 Verificando interfaces disponíveis...")
    interface_ok = tentar_executar_interface()
    
    print()
    print("📊 RESUMO:")
    print(f"   - Diagnóstico: {'✅ Concluído' if resultado_diagnostico else '❌ Erro'}")
    print(f"   - Interface: {'✅ Disponível' if interface_ok else '❌ Problemas'}")
    print()
    
    if interface_ok:
        print("🎉 Sistema pronto! Execute uma das interfaces manualmente.")
    else:
        print("⚠️  Verifique o arquivo Diagnostico.json para detalhes dos problemas.")
    
    print()
    print("📁 Arquivos importantes:")
    print("   - Diagnostico.json (diagnóstico completo)")
    print("   - ai_agent_gui.py (interface principal)")
    print("   - requirements.txt (dependências)")
    
if __name__ == "__main__":
    main()