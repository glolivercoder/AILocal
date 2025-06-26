#!/usr/bin/env python3
"""
Teste Básico do Sistema RAG - Verificação de Dependências
"""

import sys
import os
from pathlib import Path

def test_basic_imports():
    """Testa importações básicas"""
    print("🔍 Testando importações básicas...")
    
    results = {}
    
    # Testa NumPy
    try:
        import numpy as np
        results['numpy'] = True
        print("✅ NumPy disponível")
    except ImportError as e:
        results['numpy'] = False
        print(f"❌ NumPy não disponível: {e}")
    
    # Testa Requests
    try:
        import requests
        results['requests'] = True
        print("✅ Requests disponível")
    except ImportError as e:
        results['requests'] = False
        print(f"❌ Requests não disponível: {e}")
    
    # Testa JSON (built-in)
    try:
        import json
        results['json'] = True
        print("✅ JSON disponível")
    except ImportError as e:
        results['json'] = False
        print(f"❌ JSON não disponível: {e}")
    
    # Testa Pickle (built-in)
    try:
        import pickle
        results['pickle'] = True
        print("✅ Pickle disponível")
    except ImportError as e:
        results['pickle'] = False
        print(f"❌ Pickle não disponível: {e}")
    
    # Testa Pathlib (built-in)
    try:
        from pathlib import Path
        results['pathlib'] = True
        print("✅ Pathlib disponível")
    except ImportError as e:
        results['pathlib'] = False
        print(f"❌ Pathlib não disponível: {e}")
    
    return results

def test_file_operations():
    """Testa operações básicas de arquivo"""
    print("\n📁 Testando operações de arquivo...")
    
    try:
        # Cria diretório de teste
        test_dir = Path("test_rag_basic")
        test_dir.mkdir(exist_ok=True)
        print(f"✅ Diretório criado: {test_dir}")
        
        # Cria arquivo de teste
        test_file = test_dir / "test.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Este é um teste básico do sistema RAG.")
        print(f"✅ Arquivo criado: {test_file}")
        
        # Lê arquivo
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"✅ Arquivo lido: {len(content)} caracteres")
        
        # Remove arquivo de teste
        test_file.unlink()
        test_dir.rmdir()
        print("✅ Limpeza concluída")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas operações de arquivo: {e}")
        return False

def test_simple_embedding():
    """Testa embedding simples sem dependências externas"""
    print("\n🧮 Testando embedding simples...")
    
    try:
        # Texto de teste
        texts = [
            "React Native é um framework para desenvolvimento móvel",
            "Flutter usa a linguagem Dart para criar aplicações",
            "Desenvolvimento nativo oferece melhor performance"
        ]
        
        # Tokenização simples
        def simple_tokenize(text):
            import re
            text = re.sub(r'[^\w\s]', ' ', text.lower())
            return [word for word in text.split() if len(word) > 2]
        
        # Testa tokenização
        for text in texts:
            tokens = simple_tokenize(text)
            print(f"✅ Tokenizado: '{text[:30]}...' -> {len(tokens)} tokens")
        
        # Vocabulário simples
        all_tokens = set()
        for text in texts:
            all_tokens.update(simple_tokenize(text))
        
        vocabulary = {token: idx for idx, token in enumerate(sorted(all_tokens))}
        print(f"✅ Vocabulário criado: {len(vocabulary)} termos únicos")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no embedding simples: {e}")
        return False

def test_vector_operations():
    """Testa operações vetoriais básicas"""
    print("\n🔢 Testando operações vetoriais...")
    
    try:
        import numpy as np
        
        # Cria vetores de teste
        vector1 = np.array([1, 2, 3, 4, 5])
        vector2 = np.array([2, 3, 4, 5, 6])
        
        # Testa similaridade cosseno
        dot_product = np.dot(vector1, vector2)
        norm1 = np.linalg.norm(vector1)
        norm2 = np.linalg.norm(vector2)
        similarity = dot_product / (norm1 * norm2)
        
        print(f"✅ Similaridade cosseno calculada: {similarity:.3f}")
        
        # Testa normalização
        normalized = vector1 / np.linalg.norm(vector1)
        print(f"✅ Vetor normalizado: norma = {np.linalg.norm(normalized):.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas operações vetoriais: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Teste Básico do Sistema RAG")
    print("=" * 50)
    
    # Testa importações
    import_results = test_basic_imports()
    
    # Testa operações de arquivo
    file_ops_ok = test_file_operations()
    
    # Testa embedding simples
    embedding_ok = test_simple_embedding()
    
    # Testa operações vetoriais (se NumPy disponível)
    vector_ops_ok = False
    if import_results.get('numpy', False):
        vector_ops_ok = test_vector_operations()
    else:
        print("\n⚠️ Pulando testes vetoriais - NumPy não disponível")
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    tests = {
        "Importações básicas": all(import_results.values()),
        "Operações de arquivo": file_ops_ok,
        "Embedding simples": embedding_ok,
        "Operações vetoriais": vector_ops_ok or not import_results.get('numpy', False)
    }
    
    for test_name, success in tests.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"  {test_name}: {status}")
    
    overall_success = all(tests.values())
    print(f"\n🎯 Resultado Geral: {'✅ SUCESSO' if overall_success else '❌ FALHA'}")
    
    if overall_success:
        print("\n🎉 Sistema básico está funcionando!")
        print("\n📚 Próximos passos:")
        print("  1. Teste o sistema RAG simplificado")
        print("  2. Adicione documentos para teste")
        print("  3. Configure APIs se necessário")
    else:
        print("\n🔧 Algumas funcionalidades precisam de ajustes")
        print("\n💡 Sugestões:")
        print("  1. Instale dependências faltantes")
        print("  2. Verifique permissões de arquivo")
        print("  3. Use o sistema RAG simplificado")
    
    # Informações do sistema
    print("\n" + "=" * 50)
    print("ℹ️ INFORMAÇÕES DO SISTEMA")
    print("=" * 50)
    print(f"Python: {sys.version}")
    print(f"Diretório atual: {os.getcwd()}")
    print(f"Arquivos RAG disponíveis:")
    
    rag_files = [
        "rag_system_simple_fixed.py",
        "rag_system_modern.py",
        "rag_system_functional.py",
        "test_dependencies_simple.py"
    ]
    
    for file in rag_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
    
    return overall_success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)