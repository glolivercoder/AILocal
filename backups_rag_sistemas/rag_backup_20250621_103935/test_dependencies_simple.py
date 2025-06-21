#!/usr/bin/env python3
"""
Teste Simples de Dependências do Sistema RAG
"""

import sys
import importlib

def test_dependency(module_name, package_name=None):
    """Testa se uma dependência está disponível"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def main():
    print("🔍 Testando Dependências do Sistema RAG Moderno")
    print("=" * 50)
    
    # Lista de dependências críticas
    dependencies = {
        "numpy": "NumPy",
        "requests": "Requests",
        "sentence_transformers": "SentenceTransformers",
        "chromadb": "ChromaDB",
        "qdrant_client": "Qdrant Client",
        "langchain": "LangChain",
        "langchain_community": "LangChain Community",
        "langchain_huggingface": "LangChain HuggingFace",
        "faiss": "FAISS (CPU)",
        "pypdf": "PyPDF",
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "google.generativeai": "Google Gemini"
    }
    
    results = {}
    
    for module, name in dependencies.items():
        available = test_dependency(module)
        results[name] = available
        status = "✅" if available else "❌"
        print(f"  {status} {name}")
    
    print("\n" + "=" * 50)
    
    # Contagem
    available_count = sum(results.values())
    total_count = len(results)
    
    print(f"📊 Resultado: {available_count}/{total_count} dependências disponíveis")
    
    if available_count >= total_count * 0.7:  # 70% das dependências
        print("\n🎉 Sistema pronto para uso básico!")
        print("\n📚 Próximos passos:")
        print("  1. Teste o sistema RAG com: python rag_system_modern.py")
        print("  2. Configure suas APIs no config_manager.py")
        print("  3. Adicione documentos ao sistema")
    else:
        print("\n⚠️  Algumas dependências estão faltando")
        print("\n💡 Para instalar dependências faltantes:")
        print("  pip install -r requirements_rag_modern.txt")
        
        missing = [name for name, available in results.items() if not available]
        print(f"\n❌ Dependências faltantes: {', '.join(missing)}")
    
    # Teste básico do sistema se possível
    if results.get("NumPy", False) and results.get("Requests", False):
        print("\n🧪 Testando importação do sistema RAG...")
        try:
            sys.path.append('.')
            from rag_system_modern import RAGConfig, VectorDBType, EmbeddingModel
            print("✅ Sistema RAG importado com sucesso")
            
            # Teste de configuração básica
            config = RAGConfig(
                data_dir="test_basic",
                vector_db_type=VectorDBType.CHROMADB,
                embedding_model=EmbeddingModel.MINILM
            )
            print("✅ Configuração básica criada")
            
        except Exception as e:
            print(f"❌ Erro ao importar sistema RAG: {e}")
    
    print("\n" + "=" * 50)
    print("✨ Teste de dependências concluído!")

if __name__ == "__main__":
    main()