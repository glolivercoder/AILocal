#!/usr/bin/env python3
"""
Teste do Sistema RAG Funcional Ultra-Simplificado
"""

from rag_system_functional import UltraSimpleRAG, create_rag_system

def teste_basico():
    """Teste básico do sistema RAG"""
    print("🧪 Iniciando teste do Sistema RAG Ultra-Simplificado")
    print("=" * 60)
    
    try:
        # Criar sistema
        rag = create_rag_system("teste_rag")
        print("✅ Sistema criado com sucesso")
        
        # Adicionar documento de teste
        doc_content = "Este é um documento de teste sobre inteligência artificial e machine learning."
        resultado = rag.add_document("teste_doc", doc_content, {"tipo": "teste"})
        
        if resultado:
            print("✅ Documento adicionado com sucesso")
        else:
            print("❌ Falha ao adicionar documento")
            return False
        
        # Listar documentos
        docs = rag.list_documents()
        print(f"📋 Documentos no sistema: {len(docs)}")
        
        # Fazer busca
        resultados = rag.search("inteligência artificial", top_k=1)
        print(f"🔍 Resultados da busca: {len(resultados)}")
        
        if resultados:
            print(f"📄 Primeiro resultado: {resultados[0]['doc_id']}")
            print(f"📊 Similaridade: {resultados[0]['similarity']:.3f}")
        
        # Estatísticas
        stats = rag.get_stats()
        print(f"📊 Total de documentos: {stats['total_documents']}")
        print(f"📚 Tamanho do vocabulário: {stats['vocabulary_size']}")
        
        print("\n✅ Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    teste_basico()