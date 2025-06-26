#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para identificar o erro atual do sistema RAG
"""

import sys
import traceback
from pathlib import Path

def test_rag_import():
    """Testa a importação do sistema RAG"""
    print("🔍 Testando importação do sistema RAG...")
    print("=" * 50)
    
    try:
        print("1. Importando rag_system_functional...")
        from rag_system_functional import UltraSimpleRAG, create_rag_system
        print("✅ rag_system_functional importado com sucesso!")
        
        print("\n2. Criando sistema RAG...")
        rag = create_rag_system("teste_erro")
        print("✅ Sistema RAG criado com sucesso!")
        
        print("\n3. Testando adição de documento simples...")
        doc_content = "Este é um documento de teste simples."
        resultado = rag.add_document("teste_doc", doc_content, {"tipo": "teste"})
        print(f"✅ Documento adicionado: {resultado}")
        
        print("\n4. Testando busca...")
        resultados = rag.search("documento teste", top_k=1)
        print(f"✅ Busca realizada: {len(resultados)} resultados")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        print("\nTraceback completo:")
        traceback.print_exc()
        return False

def test_pdf_processing():
    """Testa especificamente o processamento de PDF"""
    print("\n🔍 Testando processamento de PDF...")
    print("=" * 50)
    
    try:
        # Criar um arquivo PDF de teste simples (texto)
        test_dir = Path("teste_pdf_temp")
        test_dir.mkdir(exist_ok=True)
        
        # Criar arquivo de texto que simula conteúdo
        test_file = test_dir / "teste.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Este é um arquivo de teste para o sistema RAG.\n")
            f.write("Contém informações sobre inteligência artificial.\n")
        
        print(f"✅ Arquivo de teste criado: {test_file}")
        
        # Testar com sistema RAG
        from rag_system_functional import create_rag_system
        rag = create_rag_system("teste_pdf")
        
        print("\n2. Testando adição de arquivo...")
        resultado = rag.add_document_from_file(str(test_file))
        print(f"✅ Arquivo adicionado: {resultado}")
        
        # Limpar
        test_file.unlink()
        test_dir.rmdir()
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO no processamento de arquivo: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        print("\nTraceback completo:")
        traceback.print_exc()
        
        # Tentar limpar mesmo com erro
        try:
            if 'test_file' in locals() and test_file.exists():
                test_file.unlink()
            if 'test_dir' in locals() and test_dir.exists():
                test_dir.rmdir()
        except:
            pass
        
        return False

def main():
    """Função principal"""
    print("🧪 TESTE DE ERRO ATUAL DO SISTEMA RAG")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Diretório: {Path.cwd()}")
    print("\n")
    
    # Teste básico
    basic_ok = test_rag_import()
    
    # Teste PDF se básico funcionou
    pdf_ok = False
    if basic_ok:
        pdf_ok = test_pdf_processing()
    
    # Resumo
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 30)
    print(f"Importação RAG: {'✅ OK' if basic_ok else '❌ ERRO'}")
    print(f"Processamento arquivo: {'✅ OK' if pdf_ok else '❌ ERRO'}")
    
    if not basic_ok:
        print("\n⚠️ PROBLEMA NA IMPORTAÇÃO DO SISTEMA RAG!")
        print("\n💡 Verifique:")
        print("   - Se rag_system_functional.py existe")
        print("   - Se as dependências estão instaladas")
        print("   - Se há conflitos de importação")
    elif not pdf_ok:
        print("\n⚠️ PROBLEMA NO PROCESSAMENTO DE ARQUIVOS!")
        print("\n💡 Verifique:")
        print("   - Se pypdf está instalado")
        print("   - Se há problemas de permissão de arquivo")
    else:
        print("\n✅ TODOS OS TESTES PASSARAM!")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    main()