#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se o erro do ai_agent_gui.py foi corrigido
"""

import sys
import os

def test_import():
    """Testa a importação do ai_agent_gui"""
    try:
        print("🔍 Testando importação do ai_agent_gui...")
        
        # Tentar importar o módulo
        import ai_agent_gui
        
        print("✅ Importação bem-sucedida!")
        
        # Verificar se a classe principal existe
        if hasattr(ai_agent_gui, 'AiAgentGUI'):
            print("✅ Classe AiAgentGUI encontrada!")
            
            # Verificar se os métodos necessários existem
            gui_class = ai_agent_gui.AiAgentGUI
            
            required_methods = [
                'load_cursor_mcps',
                'save_cursor_mcps',
                'install_filesystem_mcp'
            ]
            
            missing_methods = []
            for method in required_methods:
                if not hasattr(gui_class, method):
                    missing_methods.append(method)
            
            if missing_methods:
                print(f"❌ Métodos faltando: {missing_methods}")
                return False
            else:
                print("✅ Todos os métodos necessários estão presentes!")
                return True
        else:
            print("❌ Classe AiAgentGUI não encontrada!")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_instantiation():
    """Testa a criação de uma instância (sem interface gráfica)"""
    try:
        print("\n🔍 Testando criação de instância...")
        
        # Simular ambiente sem display para evitar erro de GUI
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        from PyQt5.QtWidgets import QApplication
        import ai_agent_gui
        
        # Criar aplicação Qt
        app = QApplication([])
        
        # Tentar criar instância
        gui = ai_agent_gui.AiAgentGUI()
        
        print("✅ Instância criada com sucesso!")
        
        # Verificar se os métodos podem ser chamados (sem executar)
        if hasattr(gui, 'load_cursor_mcps') and callable(gui.load_cursor_mcps):
            print("✅ Método load_cursor_mcps é chamável!")
        
        if hasattr(gui, 'save_cursor_mcps') and callable(gui.save_cursor_mcps):
            print("✅ Método save_cursor_mcps é chamável!")
            
        if hasattr(gui, 'install_filesystem_mcp') and callable(gui.install_filesystem_mcp):
            print("✅ Método install_filesystem_mcp é chamável!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar instância: {e}")
        return False

def main():
    """Função principal"""
    print("="*60)
    print("    TESTE DE CORREÇÃO DO AI_AGENT_GUI")
    print("="*60)
    
    # Teste 1: Importação
    import_ok = test_import()
    
    # Teste 2: Instanciação (apenas se importação funcionou)
    instantiation_ok = False
    if import_ok:
        instantiation_ok = test_instantiation()
    
    # Resumo
    print("\n" + "="*60)
    print("    RESUMO DOS TESTES")
    print("="*60)
    print(f"Importação: {'✅ OK' if import_ok else '❌ FALHOU'}")
    print(f"Instanciação: {'✅ OK' if instantiation_ok else '❌ FALHOU'}")
    
    if import_ok and instantiation_ok:
        print("\n🎉 SUCESSO! O erro foi corrigido!")
        print("\n💡 Agora você pode executar:")
        print("   python ai_agent_gui.py")
    else:
        print("\n⚠️  Ainda há problemas que precisam ser corrigidos.")
    
    print("\n📁 Arquivos importantes:")
    print("   - ai_agent_gui.py (interface principal)")
    print("   - cursor_mcp_manager.py (gerenciador MCP)")
    
if __name__ == "__main__":
    main()