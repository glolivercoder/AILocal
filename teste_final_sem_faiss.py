#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Final - ai_agent_gui sem FAISS
Desabilita o FAISS e testa a importação do ai_agent_gui.py
"""

import os
import sys
import traceback

def setup_environment():
    """Configura o ambiente para desabilitar FAISS"""
    print("Configurando ambiente...")
    
    # Desabilitar FAISS para evitar problemas
    os.environ['DISABLE_FAISS'] = 'true'
    print("✅ FAISS desabilitado via variável de ambiente")
    
    # Outras configurações de segurança
    os.environ['PYTHONUNBUFFERED'] = '1'
    print("✅ Output Python não bufferizado")

def test_rag_imports():
    """Testa as importações dos sistemas RAG"""
    print("\n============================================================")
    print("  TESTE DOS SISTEMAS RAG (SEM FAISS)")
    print("============================================================")
    
    try:
        print("Importando rag_system_advanced...")
        import rag_system_advanced
        print(f"✅ rag_system_advanced importado")
        print(f"FAISS_AVAILABLE: {rag_system_advanced.FAISS_AVAILABLE}")
        
        if hasattr(rag_system_advanced, 'SENTENCE_TRANSFORMERS_AVAILABLE'):
            print(f"SENTENCE_TRANSFORMERS_AVAILABLE: {rag_system_advanced.SENTENCE_TRANSFORMERS_AVAILABLE}")
        
        if hasattr(rag_system_advanced, 'PYMUPDF_AVAILABLE'):
            print(f"PYMUPDF_AVAILABLE: {rag_system_advanced.PYMUPDF_AVAILABLE}")
            
    except Exception as e:
        print(f"❌ Erro em rag_system_advanced: {type(e).__name__} - {e}")
        traceback.print_exc()
        return False
    
    try:
        print("\nImportando rag_system_functional...")
        import rag_system_functional
        print(f"✅ rag_system_functional importado")
        print(f"ADVANCED_RAG_AVAILABLE: {rag_system_functional.ADVANCED_RAG_AVAILABLE}")
        
    except Exception as e:
        print(f"❌ Erro em rag_system_functional: {type(e).__name__} - {e}")
        traceback.print_exc()
        return False
    
    return True

def test_ai_agent_gui():
    """Testa a importação do ai_agent_gui"""
    print("\n============================================================")
    print("  TESTE DO AI_AGENT_GUI (SEM FAISS)")
    print("============================================================")
    
    try:
        print("Importando ai_agent_gui...")
        import ai_agent_gui
        print("✅ ai_agent_gui importado com sucesso!")
        
        # Verificar classe principal
        if hasattr(ai_agent_gui, 'AiAgentGUI'):
            print("✅ Classe AiAgentGUI encontrada")
            
            # Tentar instanciar (sem executar)
            try:
                # Apenas verificar se a classe pode ser referenciada
                gui_class = ai_agent_gui.AiAgentGUI
                print("✅ Classe AiAgentGUI pode ser referenciada")
            except Exception as e:
                print(f"⚠️  Problema ao referenciar classe: {e}")
        else:
            print("❌ Classe AiAgentGUI não encontrada")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação do ai_agent_gui: {type(e).__name__}")
        print(f"Detalhes: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        return False

def create_launch_script():
    """Cria um script de lançamento que desabilita FAISS"""
    print("\nCriando script de lançamento...")
    
    script_content = '''@echo off
echo Iniciando AI Agent GUI sem FAISS...
set DISABLE_FAISS=true
set PYTHONUNBUFFERED=1
python ai_agent_gui.py
pause
'''
    
    try:
        with open('executar_ai_agent_sem_faiss.bat', 'w', encoding='utf-8') as f:
            f.write(script_content)
        print("✅ Script executar_ai_agent_sem_faiss.bat criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar script: {e}")
        return False

def main():
    """Função principal"""
    print("============================================================")
    print("  TESTE FINAL - AI AGENT GUI SEM FAISS")
    print("============================================================")
    print(f"Python: {sys.version}")
    print(f"Diretório: {os.getcwd()}")
    
    # Configurar ambiente
    setup_environment()
    
    # Teste 1: Sistemas RAG
    rag_ok = test_rag_imports()
    
    # Teste 2: AI Agent GUI
    gui_ok = test_ai_agent_gui()
    
    # Criar script de lançamento
    script_ok = create_launch_script()
    
    print("\n============================================================")
    print("  RESUMO FINAL")
    print("============================================================")
    print(f"Sistemas RAG: {'✅' if rag_ok else '❌'}")
    print(f"AI Agent GUI: {'✅' if gui_ok else '❌'}")
    print(f"Script criado: {'✅' if script_ok else '❌'}")
    
    if gui_ok:
        print("\n🎉 SUCESSO!")
        print("O ai_agent_gui.py agora pode ser importado sem problemas.")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Use 'executar_ai_agent_sem_faiss.bat' para iniciar a GUI")
        print("2. Ou defina DISABLE_FAISS=true antes de executar python ai_agent_gui.py")
        print("3. O sistema usará RAG básico (TF-IDF) em vez do avançado (FAISS)")
    else:
        print("\n❌ AINDA HÁ PROBLEMAS")
        print("Verifique os erros acima para mais detalhes.")
    
    print("============================================================")
    
    return gui_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)