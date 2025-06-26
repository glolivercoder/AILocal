#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Isolado - Problema FAISS
Testa especificamente a importação do FAISS que está causando KeyboardInterrupt
"""

import sys
import os

def test_faiss_import():
    """Testa a importação do FAISS de forma isolada"""
    print("Testando importação do FAISS...")
    
    try:
        # Tentar importar com timeout simulado
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Importação do FAISS demorou muito")
        
        # Configurar timeout de 5 segundos
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)
        
        try:
            import faiss
            signal.alarm(0)  # Cancelar timeout
            print("✅ FAISS importado com sucesso")
            return True
        except TimeoutError:
            print("⚠️  FAISS timeout - importação muito lenta")
            return False
        
    except ImportError:
        print("⚠️  FAISS não está instalado")
        return False
    except Exception as e:
        print(f"❌ Erro na importação do FAISS: {type(e).__name__} - {e}")
        return False

def test_alternative_approach():
    """Testa uma abordagem alternativa sem FAISS"""
    print("\nTestando abordagem alternativa...")
    
    try:
        # Simular o que o rag_system_advanced faria sem FAISS
        print("Configurando FAISS_AVAILABLE = False")
        
        # Testar outras dependências
        try:
            import numpy as np
            print("✅ NumPy disponível")
        except ImportError:
            print("❌ NumPy não disponível")
            
        try:
            from sentence_transformers import SentenceTransformer
            print("✅ SentenceTransformers disponível")
        except ImportError:
            print("⚠️  SentenceTransformers não disponível")
            
        try:
            import fitz  # PyMuPDF
            print("✅ PyMuPDF disponível")
        except ImportError:
            print("⚠️  PyMuPDF não disponível")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro na abordagem alternativa: {e}")
        return False

def create_faiss_mock():
    """Cria um mock do FAISS para evitar problemas de importação"""
    print("\nCriando mock do FAISS...")
    
    mock_content = '''# Mock do FAISS para evitar problemas de importação
class MockFAISS:
    """Mock simples do FAISS"""
    
    @staticmethod
    def IndexFlatL2(dimension):
        return MockIndex()
    
    @staticmethod
    def IndexFlatIP(dimension):
        return MockIndex()

class MockIndex:
    """Mock do índice FAISS"""
    
    def __init__(self):
        self.ntotal = 0
        self.d = 0
    
    def add(self, vectors):
        self.ntotal += len(vectors)
    
    def search(self, query, k):
        # Retorna resultados vazios
        import numpy as np
        distances = np.array([[]])
        indices = np.array([[]])
        return distances, indices

# Exportar como se fosse o FAISS real
IndexFlatL2 = MockFAISS.IndexFlatL2
IndexFlatIP = MockFAISS.IndexFlatIP
'''
    
    try:
        with open('faiss_mock.py', 'w', encoding='utf-8') as f:
            f.write(mock_content)
        print("✅ Mock do FAISS criado em faiss_mock.py")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar mock: {e}")
        return False

def main():
    """Função principal"""
    print("============================================================")
    print("  DIAGNÓSTICO ISOLADO - PROBLEMA FAISS")
    print("============================================================")
    
    # Teste 1: Importação direta do FAISS
    faiss_ok = test_faiss_import()
    
    # Teste 2: Abordagem alternativa
    alt_ok = test_alternative_approach()
    
    # Teste 3: Criar mock se necessário
    if not faiss_ok:
        mock_ok = create_faiss_mock()
    
    print("\n============================================================")
    print("  RESUMO DO DIAGNÓSTICO")
    print("============================================================")
    print(f"FAISS direto: {'✅' if faiss_ok else '❌'}")
    print(f"Alternativas: {'✅' if alt_ok else '❌'}")
    
    if not faiss_ok:
        print("\n🔧 RECOMENDAÇÕES:")
        print("1. O FAISS está causando problemas (timeout/KeyboardInterrupt)")
        print("2. Use o sistema RAG básico (TF-IDF) em vez do avançado")
        print("3. Considere instalar uma versão mais leve do FAISS")
        print("4. Ou use o mock criado para desenvolvimento")
    
    print("============================================================")

if __name__ == "__main__":
    main()