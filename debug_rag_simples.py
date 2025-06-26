#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug simples do sistema RAG
"""

print("🔍 Iniciando debug do sistema RAG...")
print("=" * 40)

try:
    print("1. Importando módulos...")
    import sys
    import os
    print(f"   Python: {sys.version_info.major}.{sys.version_info.minor}")
    print(f"   Diretório: {os.getcwd()}")
    
    print("\n2. Testando importação rag_system_functional...")
    from rag_system_functional import UltraSimpleRAG, create_rag_system
    print("   ✅ Importação bem-sucedida")
    
    print("\n3. Criando sistema RAG...")
    rag = create_rag_system("debug_test")
    print("   ✅ Sistema criado")
    
    print("\n4. Adicionando documento de teste...")
    resultado = rag.add_document(
        doc_id="test_doc",
        content="Este é um documento de teste para debug.",
        metadata={"tipo": "debug"}
    )
    print(f"   ✅ Documento adicionado: {resultado}")
    
    print("\n5. Fazendo busca...")
    resultados = rag.search("documento teste", top_k=1)
    print(f"   ✅ Busca realizada: {len(resultados)} resultados")
    
    if resultados:
        print(f"   📄 Primeiro resultado: {resultados[0].get('doc_id', 'N/A')}")
    
    print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
    
except ImportError as e:
    print(f"\n❌ ERRO DE IMPORTAÇÃO: {e}")
    print("\n💡 Possíveis soluções:")
    print("   - Verificar se rag_system_functional.py existe")
    print("   - Instalar dependências: pip install numpy")
    
except Exception as e:
    print(f"\n❌ ERRO GERAL: {e}")
    print(f"   Tipo: {type(e).__name__}")
    
    # Mostrar traceback detalhado
    import traceback
    print("\n📋 Traceback completo:")
    traceback.print_exc()
    
print("\n🏁 Debug finalizado.")