#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstração do Sistema RAG com Múltiplos Formatos
Versão: 1.0

Este script demonstra como usar o sistema RAG com diferentes tipos de documentos.
"""

from rag_system_functional import UltraSimpleRAG
from pathlib import Path

def demo_basica():
    """Demonstração básica das novas funcionalidades"""
    print("🚀 DEMO: Sistema RAG com Múltiplos Formatos")
    print("=" * 50)
    
    # Cria sistema RAG
    rag = UltraSimpleRAG("demo_rag_multiplos")
    
    # Cria diretório de teste
    test_dir = Path("demo_docs")
    test_dir.mkdir(exist_ok=True)
    
    # Cria documento TXT
    txt_file = test_dir / "exemplo.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("Este é um exemplo de documento TXT sobre desenvolvimento de aplicações móveis. "
                "Tecnologias como React Native e Flutter são populares para desenvolvimento cross-platform.")
    
    # Cria documento Markdown
    md_file = test_dir / "guia.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("""# Guia de Desenvolvimento

## Tecnologias Frontend
- React
- Vue.js
- Angular

## Bancos de Dados
- PostgreSQL
- MongoDB
- Redis
""")
    
    # Cria documento HTML
    html_file = test_dir / "info.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write("""<html>
<head><title>Desenvolvimento Web</title></head>
<body>
<h1>Tecnologias Web Modernas</h1>
<p>APIs RESTful são fundamentais para aplicações modernas.</p>
<p>Segurança de dados é crucial em qualquer aplicação.</p>
</body>
</html>""")
    
    # Cria documento CSV
    csv_file = test_dir / "tecnologias.csv"
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write("Categoria,Nome,Descrição\n")
        f.write("Frontend,React,Biblioteca JavaScript\n")
        f.write("Backend,Node.js,Runtime JavaScript\n")
        f.write("Database,PostgreSQL,Banco relacional\n")
    
    print("\n📄 Adicionando documentos...")
    
    # Adiciona documentos
    results = {
        "TXT": rag.add_document_from_file(str(txt_file), "exemplo_txt"),
        "Markdown": rag.add_document_from_file(str(md_file), "guia_md"),
        "HTML": rag.add_document_from_file(str(html_file), "info_html"),
        "CSV": rag.add_document_from_file(str(csv_file), "tech_csv")
    }
    
    # Mostra resultados
    for formato, sucesso in results.items():
        status = "✅" if sucesso else "❌"
        print(f"  {status} {formato}")
    
    # Testa busca
    print("\n🔍 Testando busca...")
    queries = ["desenvolvimento aplicações", "React JavaScript", "banco dados"]
    
    for query in queries:
        print(f"\nBusca: '{query}'")
        resultados = rag.search(query, top_k=2)
        for i, resultado in enumerate(resultados, 1):
            print(f"  {i}. {resultado['doc_id']} (sim: {resultado['similarity']:.3f})")
    
    # Estatísticas
    stats = rag.get_stats()
    print(f"\n📊 Estatísticas:")
    print(f"  Documentos: {stats['total_documents']}")
    print(f"  Vocabulário: {stats['vocabulary_size']} palavras")
    
    print("\n✅ Demonstração concluída!")
    return rag

if __name__ == "__main__":
    demo_basica()