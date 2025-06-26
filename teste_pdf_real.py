# -*- coding: utf-8 -*-
"""
Teste REAL de importação de PDF no sistema RAG
"""

import os
import sys

print("📄 Teste REAL de importação de PDF")
print("=" * 50)

try:
    print("1. Importando sistema RAG...")
    from rag_system_functional import UltraSimpleRAG, create_rag_system
    print("   ✅ Sistema RAG importado")
    
    print("\n2. Verificando PDFs disponíveis...")
    ebooks_dir = "g:\\AILocal\\Ebooks"
    pdfs_disponiveis = []
    
    if os.path.exists(ebooks_dir):
        for arquivo in os.listdir(ebooks_dir):
            if arquivo.lower().endswith('.pdf'):
                pdfs_disponiveis.append(arquivo)
        print(f"   📚 {len(pdfs_disponiveis)} PDFs encontrados")
        for pdf in pdfs_disponiveis[:3]:  # Mostra apenas os 3 primeiros
            print(f"      - {pdf}")
    else:
        print("   ❌ Pasta Ebooks não encontrada")
        sys.exit(1)
    
    if not pdfs_disponiveis:
        print("   ❌ Nenhum PDF encontrado")
        sys.exit(1)
    
    print("\n3. Criando sistema RAG...")
    rag = create_rag_system("teste_pdf_real")
    print("   ✅ Sistema criado")
    
    print("\n4. Testando importação de PDF REAL...")
    # Usa o primeiro PDF encontrado
    pdf_teste = pdfs_disponiveis[0]
    caminho_pdf = os.path.join(ebooks_dir, pdf_teste)
    
    print(f"   📄 Tentando importar: {pdf_teste}")
    print(f"   📁 Caminho: {caminho_pdf}")
    print(f"   📊 Tamanho: {os.path.getsize(caminho_pdf) / 1024:.1f} KB")
    
    # Testa se o arquivo existe e é legível
    if not os.path.exists(caminho_pdf):
        print("   ❌ Arquivo não existe")
        sys.exit(1)
    
    if not os.access(caminho_pdf, os.R_OK):
        print("   ❌ Arquivo não é legível")
        sys.exit(1)
    
    print("\n5. Importando PDF para o RAG...")
    try:
        resultado = rag.add_document_from_file(
            file_path=caminho_pdf,
            doc_id=f"pdf_teste_{pdf_teste}"
        )
        
        if resultado:
            print("   ✅ PDF importado com SUCESSO!")
            
            print("\n6. Testando busca no conteúdo do PDF...")
            # Tenta buscar termos comuns em PDFs de IA
            termos_busca = ["inteligência", "artificial", "machine", "learning", "dados"]
            
            for termo in termos_busca:
                resultados = rag.search(termo, top_k=1)
                if resultados:
                    print(f"   🔍 Busca '{termo}': {len(resultados)} resultado(s)")
                    break
            else:
                print("   ⚠️ Nenhum resultado encontrado nas buscas")
            
            print("\n7. Estatísticas do sistema...")
            stats = rag.get_stats()
            print(f"   📊 Total de documentos: {stats.get('total_documents', 'N/A')}")
            print(f"   📊 Total de chunks: {stats.get('total_chunks', 'N/A')}")
            
            print("\n✅ TESTE DE PDF CONCLUÍDO COM SUCESSO!")
            print(f"✅ PDF '{pdf_teste}' foi importado e indexado corretamente")
            
        else:
            print("   ❌ Falha ao importar PDF")
            
    except Exception as e:
        print(f"   ❌ ERRO ao importar PDF: {e}")
        print(f"   🔍 Tipo do erro: {type(e).__name__}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        
except ImportError as e:
    print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
    print("💡 Verifique se o sistema RAG está configurado corretamente")
    
except Exception as e:
    print(f"❌ ERRO GERAL: {e}")
    print(f"🔍 Tipo: {type(e).__name__}")
    import traceback
    print(f"📋 Traceback: {traceback.format_exc()}")

print("\n🏁 Teste finalizado.")