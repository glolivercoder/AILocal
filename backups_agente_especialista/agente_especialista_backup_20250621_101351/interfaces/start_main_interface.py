#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Inicialização da Tela Principal do Agente Especialista em Desenvolvimento de Apps
Criado para contornar problemas de timeout e inicializar a interface principal
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Função principal para inicializar a interface"""
    print("🚀 Iniciando Agente Especialista em Desenvolvimento de Apps...")
    
    # Verificar se estamos no diretório correto
    current_dir = Path.cwd()
    print(f"📁 Diretório atual: {current_dir}")
    
    # Lista de possíveis interfaces principais em ordem de prioridade
    interfaces = [
        "ai_agent_gui.py",
        "integrated_knowledge_interface.py", 
        "prompt_manager_gui.py",
        "app.py"
    ]
    
    # Tentar executar cada interface
    for interface in interfaces:
        interface_path = current_dir / interface
        if interface_path.exists():
            print(f"✅ Encontrado: {interface}")
            print(f"🔄 Tentando executar {interface}...")
            
            try:
                # Executar usando subprocess com configurações específicas
                result = subprocess.run(
                    [sys.executable, str(interface_path)],
                    cwd=str(current_dir),
                    capture_output=False,
                    text=True,
                    timeout=None
                )
                
                if result.returncode == 0:
                    print(f"✅ {interface} executado com sucesso!")
                    return
                else:
                    print(f"⚠️ {interface} retornou código {result.returncode}")
                    
            except FileNotFoundError:
                print(f"❌ Python não encontrado ou {interface} não pode ser executado")
            except Exception as e:
                print(f"❌ Erro ao executar {interface}: {e}")
                
        else:
            print(f"❌ Não encontrado: {interface}")
    
    # Se nenhuma interface foi encontrada, mostrar informações do projeto
    print("\n📋 Informações do Projeto:")
    print("Este é um projeto de Agente Especialista em Desenvolvimento de Apps")
    print("Componentes disponíveis:")
    
    # Listar arquivos Python principais
    python_files = list(current_dir.glob("*.py"))
    for py_file in sorted(python_files):
        if py_file.name.startswith(("ai_", "app", "integrated_", "prompt_", "run_")):
            print(f"  📄 {py_file.name}")
    
    print("\n💡 Para executar manualmente, tente:")
    print("   python ai_agent_gui.py")
    print("   python integrated_knowledge_interface.py")
    print("   python app.py")

if __name__ == "__main__":
    main()