#!/usr/bin/env python3
"""
Sistema RAG Ultra-Simplificado
Apenas bibliotecas built-in do Python - sem dependências externas
"""

import os
import json
import pickle
import re
import math
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
import hashlib
from datetime import datetime

class UltraSimpleRAG:
    """
    Sistema RAG ultra-simplificado usando apenas bibliotecas built-in
    """
    
    def __init__(self, storage_dir: str = "rag_storage_simple"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Arquivos de armazenamento
        self.documents_file = self.storage_dir / "documents.json"
        self.vocabulary_file = self.storage_dir / "vocabulary.json"
        self.vectors_file = self.storage_dir / "vectors.pkl"
        self.metadata_file = self.storage_dir / "metadata.json"
        
        # Dados em memória
        self.documents = {}
        self.vocabulary = {}
        self.vectors = {}
        self.metadata = {}
        
        # Carrega dados existentes
        self._load_data()
        
        print(f"✅ Sistema RAG inicializado em: {self.storage_dir}")
    
    def _load_data(self):
        """Carrega dados salvos"""
        try:
            # Carrega documentos
            if self.documents_file.exists():
                with open(self.documents_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
            
            # Carrega vocabulário
            if self.vocabulary_file.exists():
                with open(self.vocabulary_file, 'r', encoding='utf-8') as f:
                    self.vocabulary = json.load(f)
            
            # Carrega vetores
            if self.vectors_file.exists():
                with open(self.vectors_file, 'rb') as f:
                    self.vectors = pickle.load(f)
            
            # Carrega metadata
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            
            print(f"📚 Carregados {len(self.documents)} documentos")
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar dados: {e}")
            # Inicializa estruturas vazias
            self.documents = {}
            self.vocabulary = {}
            self.vectors = {}
            self.metadata = {}
    
    def _save_data(self):
        """Salva dados"""
        try:
            # Salva documentos
            with open(self.documents_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
            
            # Salva vocabulário
            with open(self.vocabulary_file, 'w', encoding='utf-8') as f:
                json.dump(self.vocabulary, f, ensure_ascii=False, indent=2)
            
            # Salva vetores
            with open(self.vectors_file, 'wb') as f:
                pickle.dump(self.vectors, f)
            
            # Salva metadata
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            
            print("💾 Dados salvos com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenização simples"""
        # Remove pontuação e converte para minúsculas
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Divide em palavras e filtra palavras muito curtas
        tokens = [word for word in text.split() if len(word) > 2]
        return tokens
    
    def _build_vocabulary(self, texts: List[str]):
        """Constrói vocabulário a partir dos textos"""
        all_tokens = set()
        for text in texts:
            tokens = self._tokenize(text)
            all_tokens.update(tokens)
        
        # Cria mapeamento token -> índice
        self.vocabulary = {token: idx for idx, token in enumerate(sorted(all_tokens))}
        print(f"📖 Vocabulário construído: {len(self.vocabulary)} termos")
    
    def _text_to_vector(self, text: str) -> List[float]:
        """Converte texto em vetor TF-IDF simplificado"""
        tokens = self._tokenize(text)
        token_counts = Counter(tokens)
        
        # Cria vetor baseado no vocabulário
        vector = [0.0] * len(self.vocabulary)
        
        for token, count in token_counts.items():
            if token in self.vocabulary:
                idx = self.vocabulary[token]
                # TF simples (frequência normalizada)
                tf = count / len(tokens) if tokens else 0
                vector[idx] = tf
        
        return vector
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similaridade cosseno entre dois vetores"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        # Produto escalar
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Normas
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def add_document(self, content: str, doc_id: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
        """Adiciona documento ao sistema"""
        if doc_id is None:
            # Gera ID baseado no hash do conteúdo
            doc_id = hashlib.md5(content.encode()).hexdigest()[:12]
        
        # Armazena documento
        self.documents[doc_id] = content
        
        # Armazena metadata
        doc_metadata = metadata or {}
        doc_metadata.update({
            'added_at': datetime.now().isoformat(),
            'length': len(content),
            'tokens': len(self._tokenize(content))
        })
        self.metadata[doc_id] = doc_metadata
        
        # Reconstrói vocabulário com todos os documentos
        all_texts = list(self.documents.values())
        self._build_vocabulary(all_texts)
        
        # Reconstrói todos os vetores
        self.vectors = {}
        for did, text in self.documents.items():
            self.vectors[did] = self._text_to_vector(text)
        
        # Salva dados
        self._save_data()
        
        print(f"📄 Documento adicionado: {doc_id} ({len(content)} chars)")
        return doc_id
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, str]]:
        """Busca documentos similares à query"""
        if not self.documents or not self.vocabulary:
            print("⚠️ Nenhum documento disponível")
            return []
        
        # Converte query em vetor
        query_vector = self._text_to_vector(query)
        
        # Calcula similaridades
        similarities = []
        for doc_id, doc_vector in self.vectors.items():
            similarity = self._cosine_similarity(query_vector, doc_vector)
            similarities.append((doc_id, similarity))
        
        # Ordena por similaridade
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Retorna top_k resultados
        results = []
        for doc_id, similarity in similarities[:top_k]:
            content = self.documents[doc_id]
            # Trunca conteúdo para preview
            preview = content[:200] + "..." if len(content) > 200 else content
            results.append((doc_id, similarity, preview))
        
        return results
    
    def get_document(self, doc_id: str) -> Optional[str]:
        """Recupera documento completo por ID"""
        return self.documents.get(doc_id)
    
    def get_metadata(self, doc_id: str) -> Optional[Dict]:
        """Recupera metadata do documento"""
        return self.metadata.get(doc_id)
    
    def list_documents(self) -> List[Dict]:
        """Lista todos os documentos com metadata"""
        docs = []
        for doc_id in self.documents:
            metadata = self.metadata.get(doc_id, {})
            docs.append({
                'id': doc_id,
                'preview': self.documents[doc_id][:100] + "...",
                'metadata': metadata
            })
        return docs
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove documento"""
        if doc_id not in self.documents:
            return False
        
        del self.documents[doc_id]
        del self.metadata[doc_id]
        if doc_id in self.vectors:
            del self.vectors[doc_id]
        
        # Reconstrói vocabulário e vetores
        if self.documents:
            all_texts = list(self.documents.values())
            self._build_vocabulary(all_texts)
            
            self.vectors = {}
            for did, text in self.documents.items():
                self.vectors[did] = self._text_to_vector(text)
        else:
            self.vocabulary = {}
            self.vectors = {}
        
        self._save_data()
        print(f"🗑️ Documento removido: {doc_id}")
        return True
    
    def clear_all(self):
        """Remove todos os documentos"""
        self.documents = {}
        self.vocabulary = {}
        self.vectors = {}
        self.metadata = {}
        self._save_data()
        print("🧹 Todos os documentos removidos")
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do sistema"""
        return {
            'total_documents': len(self.documents),
            'vocabulary_size': len(self.vocabulary),
            'storage_dir': str(self.storage_dir),
            'total_chars': sum(len(doc) for doc in self.documents.values()),
            'avg_doc_length': sum(len(doc) for doc in self.documents.values()) / len(self.documents) if self.documents else 0
        }

def demo_rag_system():
    """Demonstração do sistema RAG"""
    print("🚀 Demonstração do Sistema RAG Ultra-Simples")
    print("=" * 60)
    
    # Inicializa sistema
    rag = UltraSimpleRAG()
    
    # Documentos de exemplo sobre desenvolvimento
    sample_docs = [
        {
            'content': "React Native é um framework de desenvolvimento móvel criado pelo Facebook. Permite criar aplicações nativas para iOS e Android usando JavaScript e React. É uma excelente opção para desenvolvimento cross-platform.",
            'metadata': {'topic': 'mobile', 'framework': 'react-native'}
        },
        {
            'content': "Flutter é o framework de desenvolvimento móvel do Google que usa a linguagem Dart. Oferece performance nativa e um único codebase para múltiplas plataformas. Tem widgets personalizáveis e hot reload.",
            'metadata': {'topic': 'mobile', 'framework': 'flutter'}
        },
        {
            'content': "Docker é uma plataforma de containerização que permite empacotar aplicações com suas dependências. Facilita o deployment e garante consistência entre ambientes de desenvolvimento e produção.",
            'metadata': {'topic': 'devops', 'tool': 'docker'}
        },
        {
            'content': "APIs REST são interfaces de programação que seguem os princípios REST. Usam métodos HTTP como GET, POST, PUT, DELETE para operações CRUD. São stateless e amplamente utilizadas em aplicações web.",
            'metadata': {'topic': 'backend', 'type': 'api'}
        },
        {
            'content': "Bancos de dados NoSQL como MongoDB e Firebase oferecem flexibilidade para dados não estruturados. São escaláveis horizontalmente e ideais para aplicações modernas com grandes volumes de dados.",
            'metadata': {'topic': 'database', 'type': 'nosql'}
        }
    ]
    
    # Adiciona documentos
    print("\n📚 Adicionando documentos de exemplo...")
    for i, doc in enumerate(sample_docs):
        doc_id = rag.add_document(doc['content'], metadata=doc['metadata'])
        print(f"  {i+1}. {doc_id}: {doc['content'][:50]}...")
    
    # Mostra estatísticas
    print("\n📊 Estatísticas do sistema:")
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Testa buscas
    queries = [
        "desenvolvimento móvel",
        "containerização docker",
        "banco de dados",
        "API REST",
        "framework JavaScript"
    ]
    
    print("\n🔍 Testando buscas:")
    for query in queries:
        print(f"\n  Query: '{query}'")
        results = rag.search(query, top_k=3)
        
        if results:
            for i, (doc_id, similarity, preview) in enumerate(results, 1):
                print(f"    {i}. [{similarity:.3f}] {doc_id}: {preview[:80]}...")
        else:
            print("    Nenhum resultado encontrado")
    
    print("\n✅ Demonstração concluída!")
    return rag

def main():
    """Função principal"""
    try:
        print("Sistema RAG Ultra-Simplificado")
        print("Usando apenas bibliotecas built-in do Python")
        print("=" * 60)
        
        # Executa demonstração
        rag = demo_rag_system()
        
        print("\n" + "=" * 60)
        print("🎯 Sistema funcionando perfeitamente!")
        print("\n💡 Como usar:")
        print("  1. rag = UltraSimpleRAG()")
        print("  2. rag.add_document('seu texto aqui')")
        print("  3. results = rag.search('sua busca')")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)