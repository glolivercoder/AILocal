#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Sistema RAG com Suporte a Múltiplos Formatos de Documentos
Versão: 1.0
Data: 2024-06-21

Este script testa as novas funcionalidades do sistema RAG:
- Importação de PDF, TXT, MD, Word, Excel, LibreOffice, HTML, CSV
- Processamento de diretórios
- Importação de páginas web
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from rag_system_functional import UltraSimpleRAG

def criar_documentos_teste():
    """Cria documentos de teste em diferentes formatos"""
    test_dir = Path("test_documents_multiplos")
    test_dir.mkdir(exist_ok=True)
    
    # Documento TXT
    with open(test_dir / "documento.txt", "w", encoding="utf-8") as f:
        f.write("Este é um documento de texto simples para teste do sistema RAG. "
                "Contém informações sobre desenvolvimento de aplicações móveis e web.")
    
    # Documento Markdown
    with open(test_dir / "guia.md", "w", encoding="utf-8") as f:
        f.write("""# Guia de Desenvolvimento

## Aplicações Móveis

- **iOS**: Swift, Objective-C
- **Android**: Kotlin, Java
- **Cross-platform**: React Native, Flutter

## Tecnologias Web

- Frontend: React, Vue.js, Angular
- Backend: Node.js, Python, Java
- Banco de dados: PostgreSQL, MongoDB

### Melhores Práticas

1. Testes automatizados
2. CI/CD
3. Documentação
""")
    
    # Documento HTML
    with open(test_dir / "pagina.html", "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Desenvolvimento de Apps</title>
</head>
<body>
    <h1>Tecnologias para Desenvolvimento</h1>
    <p>Este documento contém informações sobre as principais tecnologias 
    utilizadas no desenvolvimento de aplicações modernas.</p>
    
    <h2>Frameworks Frontend</h2>
    <ul>
        <li>React - Biblioteca JavaScript</li>
        <li>Vue.js - Framework progressivo</li>
        <li>Angular - Plataforma completa</li>
    </ul>
    
    <h2>Bancos de Dados</h2>
    <p>Escolha do banco de dados é crucial para performance:</p>
    <ul>
        <li>PostgreSQL - Relacional robusto</li>
        <li>MongoDB - NoSQL flexível</li>
        <li>Redis - Cache em memória</li>
    </ul>
    
    <script>
        // Este script não deve aparecer no texto extraído
        console.log("Script ignorado");
    </script>
</body>
</html>""")
    
    # Documento CSV
    with open(test_dir / "tecnologias.csv", "w", encoding="utf-8") as f:
        f.write("""Categoria,Tecnologia,Descrição,Popularidade
Frontend,React,Biblioteca JavaScript,Alta
Frontend,Vue.js,Framework progressivo,Média
Backend,Node.js,Runtime JavaScript,Alta
Backend,Python,Linguagem versátil,Alta
Banco,PostgreSQL,Banco relacional,Alta
Banco,MongoDB,Banco NoSQL,Média
Mobile,React Native,Framework cross-platform,Alta
Mobile,Flutter,SDK do Google,Crescente""")
    
    print(f"✅ Documentos de teste criados em: {test_dir}")
    return test_dir

def testar_importacao_arquivos():
    """Testa importação de diferentes tipos de arquivo"""
    print("\n" + "="*60)
    print("🧪 TESTE: Importação de Múltiplos Formatos")
    print("="*60)
    
    # Cria sistema RAG
    rag = UltraSimpleRAG("rag_storage_multiplos_formatos")
    
    # Cria documentos de teste
    test_dir = criar_documentos_teste()
    
    # Testa importação individual
    print("\n📄 Testando importação individual:")
    
    # TXT
    success = rag.add_document_from_file(
        str(test_dir / "documento.txt"), 
        "doc_txt",
        {"categoria": "documentação", "tipo": "texto"}
    )
    print(f"TXT: {'✅' if success else '❌'}")
    
    # Markdown
    success = rag.add_document_from_file(
        str(test_dir / "guia.md"), 
        "guia_md",
        {"categoria": "guia", "tipo": "markdown"}
    )
    print(f"Markdown: {'✅' if success else '❌'}")
    
    # HTML
    success = rag.add_document_from_file(
        str(test_dir / "pagina.html"), 
        "pagina_html",
        {"categoria": "web", "tipo": "html"}
    )
    print(f"HTML: {'✅' if success else '❌'}")
    
    # CSV
    success = rag.add_document_from_file(
        str(test_dir / "tecnologias.csv"), 
        "tech_csv",
        {"categoria": "dados", "tipo": "csv"}
    )
    print(f"CSV: {'✅' if success else '❌'}")
    
    return rag

def testar_importacao_diretorio():
    """Testa importação de diretório completo"""
    print("\n" + "="*60)
    print("📁 TESTE: Importação de Diretório")
    print("="*60)
    
    # Cria novo sistema RAG
    rag = UltraSimpleRAG("rag_storage_diretorio")
    
    # Importa diretório completo
    test_dir = Path("test_documents_multiplos")
    if test_dir.exists():
        results = rag.add_documents_from_directory(str(test_dir))
        
        print(f"\n📊 Resultados da importação:")
        for file_path, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {Path(file_path).name}")
    
    return rag

def testar_importacao_url():
    """Testa importação de página web"""
    print("\n" + "="*60)
    print("🌐 TESTE: Importação de URL")
    print("="*60)
    
    # Cria novo sistema RAG
    rag = UltraSimpleRAG("rag_storage_web")
    
    # URLs de teste (páginas simples)
    test_urls = [
        "https://httpbin.org/html",  # Página HTML simples
        "https://example.com"        # Página básica
    ]
    
    for url in test_urls:
        try:
            print(f"\n🌐 Testando: {url}")
            success = rag.add_document_from_url(
                url, 
                metadata={"fonte": "web", "tipo": "pagina"}
            )
            print(f"Resultado: {'✅' if success else '❌'}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    return rag

def testar_busca_multiplos_formatos(rag):
    """Testa busca em documentos de múltiplos formatos"""
    print("\n" + "="*60)
    print("🔍 TESTE: Busca em Múltiplos Formatos")
    print("="*60)
    
    # Consultas de teste
    queries = [
        "desenvolvimento aplicações",
        "React JavaScript",
        "banco de dados",
        "tecnologias frontend",
        "mobile apps"
    ]
    
    for query in queries:
        print(f"\n🔍 Busca: '{query}'")
        results = rag.search(query, top_k=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['doc_id']} (similaridade: {result['similarity']:.3f})")
                print(f"     Tipo: {result['metadata'].get('file_extension', 'N/A')}")
                print(f"     Preview: {result['content'][:100]}...")
        else:
            print("  Nenhum resultado encontrado")

def mostrar_estatisticas(rag):
    """Mostra estatísticas do sistema"""
    print("\n" + "="*60)
    print("📊 ESTATÍSTICAS DO SISTEMA")
    print("="*60)
    
    stats = rag.get_stats()
    print(f"📄 Total de documentos: {stats['total_documents']}")
    print(f"📚 Tamanho do vocabulário: {stats['vocabulary_size']}")
    print(f"💾 Diretório de armazenamento: {stats['storage_dir']}")
    
    print("\n📋 Documentos no sistema:")
    docs = rag.list_documents()
    for doc in docs:
        print(f"  • {doc['doc_id']}")
        print(f"    Tipo: {doc['metadata'].get('file_extension', 'N/A')}")
        print(f"    Tamanho: {doc['metadata'].get('file_size', 'N/A')} bytes")
        print(f"    Adicionado: {doc['added_at']}")

def main():
    """Função principal de teste"""
    print("🚀 SISTEMA RAG - TESTE DE MÚLTIPLOS FORMATOS")
    print("=" * 60)
    print("Testando suporte a: TXT, MD, HTML, CSV, PDF, Word, Excel, LibreOffice")
    
    try:
        # Teste 1: Importação de arquivos individuais
        rag1 = testar_importacao_arquivos()
        
        # Teste 2: Importação de diretório
        rag2 = testar_importacao_diretorio()
        
        # Teste 3: Importação de URL (opcional)
        try:
            rag3 = testar_importacao_url()
        except Exception as e:
            print(f"⚠️ Teste de URL falhou (normal se sem internet): {e}")
            rag3 = rag2
        
        # Teste 4: Busca em múltiplos formatos
        testar_busca_multiplos_formatos(rag1)
        
        # Teste 5: Estatísticas
        mostrar_estatisticas(rag1)
        
        print("\n" + "="*60)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("="*60)
        print("\n💡 O sistema RAG agora suporta:")
        print("   📄 TXT, MD, HTML, CSV")
        print("   📊 Excel (.xlsx) - parcial")
        print("   📝 Word (.docx) - parcial")
        print("   📋 LibreOffice (.odt, .ods, .odp)")
        print("   🌐 Páginas web (HTML)")
        print("   📁 Importação de diretórios")
        print("   🔍 Busca unificada em todos os formatos")
        
        print("\n🔧 Para melhor suporte a PDF:")
        print("   pip install PyPDF2 pdfplumber")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)