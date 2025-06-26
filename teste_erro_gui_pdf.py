#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para reproduzir o erro de PDF na interface gráfica
"""

import sys
import os
import traceback
from pathlib import Path

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gui_pdf_error():
    """Testa o erro de PDF que ocorre na GUI"""
    print("🔍 Testando erro de PDF na interface gráfica...")
    
    try:
        # Importa o sistema RAG funcional (mesmo usado na GUI)
        from rag_system_functional import UltraSimpleRAG
        
        print("✅ Sistema RAG importado com sucesso")
        
        # Inicializa o sistema RAG
        rag_system = UltraSimpleRAG()
        print("✅ Sistema RAG inicializado")
        
        # Testa com um PDF existente
        pdf_files = [
            "test_documents/a-practical-guide-to-building-agents.pdf",
            "test_documents/identifying-and-scaling-ai-use-cases.pdf",
            "test_documents/ai-in-the-enterprise.pdf"
        ]
        
        for pdf_file in pdf_files:
            if os.path.exists(pdf_file):
                print(f"\n📄 Testando upload de: {pdf_file}")
                
                try:
                    # Simula o que a GUI faz
                    doc_id = os.path.basename(pdf_file)
                    print(f"⚙️ Processando: {doc_id}...")
                    
                    # Chama o mesmo método que a GUI usa
                    success = rag_system.add_document_from_file(pdf_file, doc_id=doc_id)
                    
                    if success:
                        print(f"✅ Documento '{doc_id}' adicionado com sucesso!")
                        
                        # Testa busca
                        results = rag_system.search("AI agents", top_k=3)
                        print(f"🔍 Busca retornou {len(results)} resultados")
                        
                    else:
                        print(f"⚠️ Falha ao adicionar '{doc_id}'. Verifique os logs.")
                        
                except Exception as e:
                    print(f"❌ Erro ao processar o arquivo: {e}")
                    print("\n📋 Traceback completo:")
                    traceback.print_exc()
                    
                break  # Testa apenas o primeiro PDF encontrado
        else:
            print("❌ Nenhum arquivo PDF encontrado para teste")
            
        # Testa estatísticas
        try:
            stats = rag_system.get_stats()
            print(f"\n📊 Estatísticas: {stats}")
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            traceback.print_exc()
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        traceback.print_exc()

def check_dependencies():
    """Verifica dependências necessárias"""
    print("🔍 Verificando dependências...")
    
    dependencies = {
        'pypdf': 'pypdf',
        'PyQt5': 'PyQt5',
        'sentence_transformers': 'sentence-transformers',
        'faiss': 'faiss-cpu'
    }
    
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module} disponível")
        except ImportError:
            print(f"❌ {module} não disponível (instale com: pip install {package})")

if __name__ == "__main__":
    print("🚀 Iniciando teste de erro de PDF na GUI...\n")
    
    check_dependencies()
    print()
    test_gui_pdf_error()
    
    print("\n✅ Teste concluído!")