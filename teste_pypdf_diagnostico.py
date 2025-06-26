#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico específico para pypdf
"""

import sys
import traceback

def test_pypdf_import():
    """Testa a importação da biblioteca pypdf"""
    print("🔍 Testando importação da biblioteca pypdf...")
    print("=" * 50)
    
    try:
        print("1. Tentando importar pypdf...")
        from pypdf import PdfReader
        print("✅ pypdf importado com sucesso!")
        
        print("\n2. Testando criação de PdfReader...")
        # Não vamos tentar abrir um arquivo, apenas verificar se a classe existe
        print(f"✅ Classe PdfReader disponível: {PdfReader}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação pypdf: {e}")
        print("\n💡 Soluções possíveis:")
        print("   - pip install pypdf")
        print("   - pip install --upgrade pypdf")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        print("\nTraceback completo:")
        traceback.print_exc()
        return False

def test_alternative_pdf_libs():
    """Testa bibliotecas alternativas para PDF"""
    print("\n🔍 Testando bibliotecas alternativas para PDF...")
    print("=" * 50)
    
    alternatives = [
        ("PyPDF2", "PyPDF2"),
        ("pdfplumber", "pdfplumber"),
        ("pymupdf", "fitz")
    ]
    
    available = []
    
    for lib_name, import_name in alternatives:
        try:
            __import__(import_name)
            print(f"✅ {lib_name} disponível")
            available.append(lib_name)
        except ImportError:
            print(f"❌ {lib_name} não disponível")
        except Exception as e:
            print(f"⚠️ {lib_name} erro: {e}")
    
    return available

def main():
    """Função principal"""
    print("🧪 DIAGNÓSTICO PYPDF")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Plataforma: {sys.platform}")
    print("\n")
    
    # Teste pypdf
    pypdf_ok = test_pypdf_import()
    
    # Teste alternativas
    alternatives = test_alternative_pdf_libs()
    
    # Resumo
    print("\n📊 RESUMO")
    print("=" * 30)
    print(f"pypdf: {'✅ OK' if pypdf_ok else '❌ ERRO'}")
    print(f"Alternativas disponíveis: {', '.join(alternatives) if alternatives else 'Nenhuma'}")
    
    if not pypdf_ok and not alternatives:
        print("\n⚠️ NENHUMA BIBLIOTECA PDF DISPONÍVEL!")
        print("\n💡 Para corrigir, execute:")
        print("   pip install pypdf PyPDF2 pdfplumber")
    elif not pypdf_ok:
        print(f"\n💡 pypdf não disponível, mas você pode usar: {alternatives[0]}")
    
    print("\n✅ Diagnóstico concluído!")

if __name__ == "__main__":
    main()