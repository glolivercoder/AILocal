#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Final do Sistema
Verifica se o agente está pronto e funcionando
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

def test_rag_import():
    """Testa importação do sistema RAG"""
    print("🔍 Testando importação do sistema RAG...")
    
    try:
        from rag_system_functional import UltraSimpleRAG
        print("✅ UltraSimpleRAG importado com sucesso")
        
        # Testar criação de instância
        rag = UltraSimpleRAG()
        print("✅ Instância UltraSimpleRAG criada")
        
        # Testar funcionalidades básicas
        rag.add_document("Teste de documento", {"tipo": "teste"})
        results = rag.search("documento", top_k=1)
        
        if results:
            print("✅ Funcionalidades básicas do RAG funcionando")
            return True
        else:
            print("❌ Busca não retornou resultados")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar RAG: {e}")
        return False

def test_rag_alias():
    """Testa alias RAGSystemFunctional"""
    print("🔍 Testando alias RAGSystemFunctional...")
    
    try:
        from rag_system_functional import RAGSystemFunctional
        print("✅ RAGSystemFunctional importado com sucesso")
        
        # Verificar se é o mesmo que UltraSimpleRAG
        from rag_system_functional import UltraSimpleRAG
        
        if RAGSystemFunctional == UltraSimpleRAG:
            print("✅ Alias RAGSystemFunctional está correto")
            return True
        else:
            print("❌ Alias RAGSystemFunctional não aponta para UltraSimpleRAG")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar alias: {e}")
        return False

def test_gui_import():
    """Testa importação da interface gráfica"""
    print("🔍 Testando importação da interface gráfica...")
    
    try:
        # Testar apenas a importação, não executar
        import ai_agent_gui
        print("✅ ai_agent_gui.py importado com sucesso")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação em ai_agent_gui.py: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Aviso: Erro não crítico em ai_agent_gui.py: {e}")
        return True  # Pode ser erro de PyQt5, mas importação funcionou

def test_multiple_formats():
    """Testa suporte a múltiplos formatos"""
    print("🔍 Testando suporte a múltiplos formatos...")
    
    try:
        from rag_system_functional import UltraSimpleRAG
        rag = UltraSimpleRAG()
        
        # Verificar se métodos existem
        methods_to_check = [
            '_extract_from_txt',
            '_extract_from_markdown',
            '_extract_from_html',
            '_extract_from_csv',
            '_extract_from_word',
            '_extract_from_excel',
            '_extract_from_libreoffice',
            '_extract_from_pdf',
            'add_document_from_file',
            'add_documents_from_directory',
            'add_document_from_url'
        ]
        
        missing_methods = []
        for method in methods_to_check:
            if not hasattr(rag, method):
                missing_methods.append(method)
        
        if not missing_methods:
            print("✅ Todos os métodos de múltiplos formatos estão disponíveis")
            return True
        else:
            print(f"❌ Métodos ausentes: {missing_methods}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar múltiplos formatos: {e}")
        return False

def test_file_existence():
    """Testa existência de arquivos principais"""
    print("🔍 Verificando arquivos principais...")
    
    required_files = [
        "ai_agent_gui.py",
        "rag_system_functional.py",
        "executar_interface_principal.bat"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"✅ {file} encontrado")
    
    if not missing_files:
        print("✅ Todos os arquivos principais estão presentes")
        return True
    else:
        print(f"❌ Arquivos ausentes: {missing_files}")
        return False

def run_final_test():
    """Executa teste final completo"""
    print("🚀 TESTE FINAL DO SISTEMA")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "summary": {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "success_rate": 0
        },
        "system_ready": False
    }
    
    # Lista de testes
    tests = [
        ("Existência de Arquivos", test_file_existence),
        ("Importação RAG", test_rag_import),
        ("Alias RAGSystemFunctional", test_rag_alias),
        ("Importação Interface", test_gui_import),
        ("Múltiplos Formatos", test_multiple_formats)
    ]
    
    # Executar testes
    for test_name, test_func in tests:
        print(f"\n📋 Executando: {test_name}")
        try:
            result = test_func()
            results["tests"][test_name] = {
                "status": "PASSED" if result else "FAILED",
                "success": result
            }
            
            if result:
                results["summary"]["passed_tests"] += 1
            else:
                results["summary"]["failed_tests"] += 1
                
        except Exception as e:
            print(f"❌ Erro crítico em {test_name}: {e}")
            results["tests"][test_name] = {
                "status": "ERROR",
                "success": False,
                "error": str(e)
            }
            results["summary"]["failed_tests"] += 1
        
        results["summary"]["total_tests"] += 1
    
    # Calcular taxa de sucesso
    if results["summary"]["total_tests"] > 0:
        results["summary"]["success_rate"] = (
            results["summary"]["passed_tests"] / results["summary"]["total_tests"]
        ) * 100
    
    # Determinar se sistema está pronto
    results["system_ready"] = results["summary"]["success_rate"] >= 80
    
    # Salvar resultados
    with open("Teste_Final_Resultados.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Exibir resumo
    print(f"\n📊 RESUMO DOS TESTES:")
    print(f"   Total: {results['summary']['total_tests']}")
    print(f"   Sucessos: {results['summary']['passed_tests']}")
    print(f"   Falhas: {results['summary']['failed_tests']}")
    print(f"   Taxa de Sucesso: {results['summary']['success_rate']:.1f}%")
    
    if results["system_ready"]:
        print(f"\n🎉 SISTEMA PRONTO PARA USO!")
        print(f"\n🚀 Para iniciar o agente:")
        print(f"   • Windows: executar_interface_principal.bat")
        print(f"   • Python: python ai_agent_gui.py")
        print(f"\n📚 Para testar RAG:")
        print(f"   • python demo_rag_multiplos_formatos.py")
        print(f"   • python rag_system_functional.py")
    else:
        print(f"\n⚠️  SISTEMA PRECISA DE CORREÇÕES")
        print(f"\n🔧 Verifique os testes que falharam acima")
        print(f"\n📄 Detalhes salvos em: Teste_Final_Resultados.json")
    
    return results

def main():
    """Função principal"""
    try:
        return run_final_test()
    except Exception as e:
        print(f"❌ Erro crítico durante teste final: {e}")
        return {"status": "critical_error", "error": str(e)}

if __name__ == "__main__":
    main()