#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Importação Corrigida - ai_agent_gui.py
Verifica se as correções nas importações resolveram os problemas
"""

import sys
import traceback
from pathlib import Path

def test_import_ai_agent():
    """Testa a importação do ai_agent_gui"""
    print("============================================================")
    print("  TESTE DE IMPORTAÇÃO CORRIGIDA")
    print("============================================================")
    
    try:
        print("Tentando importar ai_agent_gui...")
        import ai_agent_gui
        print("✅ ai_agent_gui importado com sucesso!")
        
        # Verificar se a classe principal existe
        if hasattr(ai_agent_gui, 'AiAgentGUI'):
            print("✅ Classe AiAgentGUI encontrada")
        else:
            print("⚠️  Classe AiAgentGUI não encontrada")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {type(e).__name__}")
        print(f"Detalhes: {str(e)}")
        print("\nTraceback completo:")
        traceback.print_exc()
        return False

def test_rag_systems():
    """Testa as importações dos sistemas RAG"""
    print("\n============================================================")
    print("  TESTE DOS SISTEMAS RAG")
    print("============================================================")
    
    # Teste rag_system_functional
    try:
        print("Testando rag_system_functional...")
        import rag_system_functional
        print("✅ rag_system_functional importado")
        
        if hasattr(rag_system_functional, 'ADVANCED_RAG_AVAILABLE'):
            status = rag_system_functional.ADVANCED_RAG_AVAILABLE
            print(f"Status RAG Avançado: {status}")
            
    except Exception as e:
        print(f"❌ Erro em rag_system_functional: {e}")
    
    # Teste rag_system_advanced
    try:
        print("\nTestando rag_system_advanced...")
        import rag_system_advanced
        print("✅ rag_system_advanced importado")
        
        if hasattr(rag_system_advanced, 'FAISS_AVAILABLE'):
            status = rag_system_advanced.FAISS_AVAILABLE
            print(f"Status FAISS: {status}")
            
    except Exception as e:
        print(f"❌ Erro em rag_system_advanced: {e}")

def main():
    """Função principal"""
    print(f"Python: {sys.version}")
    print(f"Diretório: {Path.cwd()}")
    
    # Teste principal
    success = test_import_ai_agent()
    
    # Teste dos sistemas RAG
    test_rag_systems()
    
    print("\n============================================================")
    if success:
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("O ai_agent_gui.py agora pode ser importado sem erros.")
    else:
        print("❌ TESTE FALHOU")
        print("Ainda há problemas na importação do ai_agent_gui.py")
    print("============================================================")
    
    return success

if __name__ == "__main__":
    main()