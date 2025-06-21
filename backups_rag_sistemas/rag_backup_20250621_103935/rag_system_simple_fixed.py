#!/usr/bin/env python3
"""
Sistema RAG Simplificado - Versão Funcional
Evita dependências problemáticas e foca na funcionalidade básica
"""

import os
import sys
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import re

# Dependências básicas (sempre disponíveis)
try:
    import numpy as np
except ImportError:
    print("⚠️ NumPy não encontrado. Instalando...")
    os.system("pip install numpy")
    import numpy as np

try:
    import requests
except ImportError:
    print("⚠️ Requests não encontrado. Instalando...")
    os.system("pip install requests")
    import requests

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDBType(Enum):
    """Tipos de banco de dados vetorial"""
    SIMPLE = "simple"  # Implementação simples com NumPy
    FAISS = "faiss"    # FAISS se disponível

class EmbeddingModel(Enum):
    """Modelos de embedding disponíveis"""
    SIMPLE = "simple"      # Embedding simples baseado em TF-IDF
    OPENAI = "openai"      # OpenAI embeddings
    HUGGINGFACE = "huggingface"  # HuggingFace se disponível

@dataclass
class RAGConfig:
    """Configuração do sistema RAG"""
    data_dir: str = "rag_data_simple"
    vector_db_type: VectorDBType = VectorDBType.SIMPLE
    embedding_model: EmbeddingModel = EmbeddingModel.SIMPLE
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_results: int = 5
    similarity_threshold: float = 0.1
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "data_dir": self.data_dir,
            "vector_db_type": self.vector_db_type.value,
            "embedding_model": self.embedding_model.value,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "max_results": self.max_results,
            "similarity_threshold": self.similarity_threshold
        }

class SimpleEmbedding:
    """Embedding simples baseado em TF-IDF"""
    
    def __init__(self):
        self.vocabulary = {}
        self.idf_scores = {}
        self.documents = []
        
    def _tokenize(self, text: str) -> List[str]:
        """Tokenização simples"""
        # Remove pontuação e converte para minúsculas
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return [word for word in text.split() if len(word) > 2]
    
    def _calculate_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Calcula Term Frequency"""
        tf = {}
        total_tokens = len(tokens)
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        
        # Normaliza por frequência
        for token in tf:
            tf[token] = tf[token] / total_tokens
        
        return tf
    
    def _calculate_idf(self, documents: List[List[str]]) -> Dict[str, float]:
        """Calcula Inverse Document Frequency"""
        idf = {}
        total_docs = len(documents)
        
        # Conta em quantos documentos cada termo aparece
        for doc_tokens in documents:
            unique_tokens = set(doc_tokens)
            for token in unique_tokens:
                idf[token] = idf.get(token, 0) + 1
        
        # Calcula IDF
        for token in idf:
            idf[token] = np.log(total_docs / idf[token])
        
        return idf
    
    def fit(self, texts: List[str]):
        """Treina o modelo com os textos"""
        self.documents = [self._tokenize(text) for text in texts]
        
        # Constrói vocabulário
        all_tokens = set()
        for doc_tokens in self.documents:
            all_tokens.update(doc_tokens)
        
        self.vocabulary = {token: idx for idx, token in enumerate(sorted(all_tokens))}
        self.idf_scores = self._calculate_idf(self.documents)
        
        logger.info(f"Modelo treinado com {len(texts)} documentos e {len(self.vocabulary)} termos únicos")
    
    def transform(self, text: str) -> np.ndarray:
        """Converte texto em vetor de embedding"""
        tokens = self._tokenize(text)
        tf = self._calculate_tf(tokens)
        
        # Cria vetor TF-IDF
        vector = np.zeros(len(self.vocabulary))
        for token, tf_score in tf.items():
            if token in self.vocabulary:
                idx = self.vocabulary[token]
                idf_score = self.idf_scores.get(token, 0)
                vector[idx] = tf_score * idf_score
        
        # Normaliza o vetor
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """Treina e transforma os textos"""
        self.fit(texts)
        return np.array([self.transform(text) for text in texts])

class SimpleVectorDB:
    """Banco de dados vetorial simples usando NumPy"""
    
    def __init__(self, embedding_dim: int = None):
        self.vectors = []
        self.metadata = []
        self.embedding_dim = embedding_dim
    
    def add(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]):
        """Adiciona vetores e metadados"""
        if len(vectors) != len(metadata):
            raise ValueError("Número de vetores deve ser igual ao número de metadados")
        
        if self.embedding_dim is None:
            self.embedding_dim = vectors.shape[1]
        elif vectors.shape[1] != self.embedding_dim:
            raise ValueError(f"Dimensão dos vetores ({vectors.shape[1]}) não corresponde à esperada ({self.embedding_dim})")
        
        self.vectors.extend(vectors)
        self.metadata.extend(metadata)
        
        logger.info(f"Adicionados {len(vectors)} vetores ao banco")
    
    def search(self, query_vector: np.ndarray, top_k: int = 5, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Busca por similaridade"""
        if not self.vectors:
            return []
        
        vectors_array = np.array(self.vectors)
        
        # Calcula similaridade cosseno
        similarities = np.dot(vectors_array, query_vector)
        
        # Filtra por threshold
        valid_indices = np.where(similarities >= threshold)[0]
        
        if len(valid_indices) == 0:
            return []
        
        # Ordena por similaridade
        sorted_indices = valid_indices[np.argsort(similarities[valid_indices])[::-1]]
        
        # Retorna top_k resultados
        results = []
        for idx in sorted_indices[:top_k]:
            result = self.metadata[idx].copy()
            result['similarity_score'] = float(similarities[idx])
            results.append(result)
        
        return results
    
    def save(self, filepath: str):
        """Salva o banco de dados"""
        data = {
            'vectors': self.vectors,
            'metadata': self.metadata,
            'embedding_dim': self.embedding_dim
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        logger.info(f"Banco salvo em {filepath}")
    
    def load(self, filepath: str):
        """Carrega o banco de dados"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            self.vectors = data['vectors']
            self.metadata = data['metadata']
            self.embedding_dim = data['embedding_dim']
            logger.info(f"Banco carregado de {filepath} com {len(self.vectors)} vetores")
            return True
        return False

class SimpleRAGSystem:
    """Sistema RAG simplificado e funcional"""
    
    def __init__(self, config: RAGConfig):
        self.config = config
        self.data_dir = Path(config.data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Inicializa componentes
        self.embedding_model = SimpleEmbedding()
        self.vector_db = SimpleVectorDB()
        self.documents_cache = {}
        
        # Arquivos de persistência
        self.vector_db_file = self.data_dir / "vector_db.pkl"
        self.embedding_model_file = self.data_dir / "embedding_model.pkl"
        self.cache_file = self.data_dir / "documents_cache.json"
        self.config_file = self.data_dir / "config.json"
        
        # Carrega dados existentes
        self._load_system()
        
        logger.info(f"Sistema RAG inicializado em {self.data_dir}")
    
    def _load_system(self):
        """Carrega sistema salvo"""
        try:
            # Carrega configuração
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                logger.info("Configuração carregada")
            
            # Carrega cache de documentos
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.documents_cache = json.load(f)
                logger.info(f"Cache carregado com {len(self.documents_cache)} documentos")
            
            # Carrega modelo de embedding
            if self.embedding_model_file.exists():
                with open(self.embedding_model_file, 'rb') as f:
                    self.embedding_model = pickle.load(f)
                logger.info("Modelo de embedding carregado")
            
            # Carrega banco vetorial
            self.vector_db.load(str(self.vector_db_file))
            
        except Exception as e:
            logger.warning(f"Erro ao carregar sistema: {e}")
    
    def _save_system(self):
        """Salva sistema"""
        try:
            # Salva configuração
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Salva cache
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents_cache, f, indent=2, ensure_ascii=False)
            
            # Salva modelo de embedding
            with open(self.embedding_model_file, 'wb') as f:
                pickle.dump(self.embedding_model, f)
            
            # Salva banco vetorial
            self.vector_db.save(str(self.vector_db_file))
            
            logger.info("Sistema salvo com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao salvar sistema: {e}")
    
    def _split_text(self, text: str) -> List[str]:
        """Divide texto em chunks"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.config.chunk_size - self.config.chunk_overlap):
            chunk_words = words[i:i + self.config.chunk_size]
            chunk = ' '.join(chunk_words)
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def _load_document(self, file_path: Union[str, Path]) -> str:
        """Carrega documento de arquivo"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        try:
            if file_path.suffix.lower() == '.pdf':
                # Tenta carregar PDF (requer PyPDF2)
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                    return text
                except ImportError:
                    logger.warning("PyPDF2 não disponível. Instale com: pip install PyPDF2")
                    return f"Documento PDF: {file_path.name} (conteúdo não extraído)"
            
            else:
                # Arquivo de texto
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
        except Exception as e:
            logger.error(f"Erro ao carregar {file_path}: {e}")
            return f"Erro ao carregar documento: {file_path.name}"
    
    def add_document(self, file_path: Union[str, Path], metadata: Dict[str, Any] = None) -> bool:
        """Adiciona documento ao sistema"""
        try:
            file_path = Path(file_path)
            
            # Verifica se já foi processado
            file_hash = hashlib.md5(str(file_path).encode()).hexdigest()
            if file_hash in self.documents_cache:
                logger.info(f"Documento já processado: {file_path.name}")
                return True
            
            # Carrega e processa documento
            text = self._load_document(file_path)
            chunks = self._split_text(text)
            
            if not chunks:
                logger.warning(f"Nenhum chunk gerado para {file_path.name}")
                return False
            
            # Prepara metadados
            base_metadata = {
                'source': str(file_path),
                'filename': file_path.name,
                'file_hash': file_hash,
                'chunks_count': len(chunks)
            }
            
            if metadata:
                base_metadata.update(metadata)
            
            # Gera embeddings
            if not hasattr(self.embedding_model, 'vocabulary') or not self.embedding_model.vocabulary:
                # Primeiro documento - treina o modelo
                self.embedding_model.fit(chunks)
            
            vectors = np.array([self.embedding_model.transform(chunk) for chunk in chunks])
            
            # Prepara metadados para cada chunk
            chunk_metadata = []
            for i, chunk in enumerate(chunks):
                chunk_meta = base_metadata.copy()
                chunk_meta.update({
                    'chunk_id': i,
                    'text': chunk,
                    'chunk_length': len(chunk)
                })
                chunk_metadata.append(chunk_meta)
            
            # Adiciona ao banco vetorial
            self.vector_db.add(vectors, chunk_metadata)
            
            # Atualiza cache
            self.documents_cache[file_hash] = {
                'file_path': str(file_path),
                'filename': file_path.name,
                'chunks_count': len(chunks),
                'processed_at': str(Path().cwd())
            }
            
            # Salva sistema
            self._save_system()
            
            logger.info(f"Documento adicionado: {file_path.name} ({len(chunks)} chunks)")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar documento {file_path}: {e}")
            return False
    
    def search(self, query: str, top_k: int = None, threshold: float = None) -> List[Dict[str, Any]]:
        """Busca documentos relevantes"""
        if top_k is None:
            top_k = self.config.max_results
        if threshold is None:
            threshold = self.config.similarity_threshold
        
        try:
            # Gera embedding da query
            query_vector = self.embedding_model.transform(query)
            
            # Busca no banco vetorial
            results = self.vector_db.search(query_vector, top_k, threshold)
            
            logger.info(f"Busca por '{query[:50]}...' retornou {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
    
    def get_context_for_query(self, query: str, max_length: int = 2000) -> str:
        """Gera contexto para uma query"""
        results = self.search(query)
        
        if not results:
            return "Nenhum contexto relevante encontrado."
        
        context_parts = []
        current_length = 0
        
        for result in results:
            text = result.get('text', '')
            source = result.get('filename', 'Desconhecido')
            
            part = f"[{source}] {text}"
            
            if current_length + len(part) > max_length:
                break
            
            context_parts.append(part)
            current_length += len(part)
        
        return "\n\n".join(context_parts)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status do sistema"""
        return {
            'system_version': '1.0.0-simple',
            'data_dir': str(self.data_dir),
            'documents_count': len(self.documents_cache),
            'vectors_count': len(self.vector_db.vectors),
            'embedding_model': self.config.embedding_model.value,
            'vector_db_type': self.config.vector_db_type.value,
            'vocabulary_size': len(getattr(self.embedding_model, 'vocabulary', {})),
            'config': self.config.to_dict()
        }
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """Lista documentos carregados"""
        return list(self.documents_cache.values())
    
    def clear_all(self):
        """Limpa todos os dados"""
        self.vector_db = SimpleVectorDB()
        self.embedding_model = SimpleEmbedding()
        self.documents_cache = {}
        
        # Remove arquivos salvos
        for file_path in [self.vector_db_file, self.embedding_model_file, self.cache_file]:
            if file_path.exists():
                file_path.unlink()
        
        logger.info("Sistema limpo")

# Funções de conveniência
def create_simple_rag_system(data_dir: str = "rag_data_simple") -> SimpleRAGSystem:
    """Cria sistema RAG simples"""
    config = RAGConfig(
        data_dir=data_dir,
        vector_db_type=VectorDBType.SIMPLE,
        embedding_model=EmbeddingModel.SIMPLE
    )
    return SimpleRAGSystem(config)

if __name__ == "__main__":
    # Teste básico
    print("🚀 Testando Sistema RAG Simplificado")
    
    try:
        # Cria sistema
        rag = create_simple_rag_system("test_rag_simple")
        print("✅ Sistema criado com sucesso")
        
        # Status
        status = rag.get_system_status()
        print(f"📊 Status: {status['documents_count']} documentos, {status['vectors_count']} vetores")
        
        # Teste com texto simples
        test_text = """
        Este é um documento de teste sobre desenvolvimento de aplicações.
        Ele contém informações sobre React Native, Flutter e desenvolvimento nativo.
        React Native permite criar apps para iOS e Android usando JavaScript.
        Flutter usa a linguagem Dart e oferece performance excelente.
        O desenvolvimento nativo oferece acesso completo às APIs do sistema.
        """
        
        # Salva texto de teste
        test_file = Path("test_document.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_text)
        
        # Adiciona documento
        success = rag.add_document(test_file)
        if success:
            print("✅ Documento de teste adicionado")
        
        # Teste de busca
        query = "Como desenvolver apps com React Native?"
        results = rag.search(query, top_k=3)
        
        print(f"\n🔍 Busca: {query}")
        for i, result in enumerate(results, 1):
            print(f"  {i}. Score: {result['similarity_score']:.3f}")
            print(f"     {result['text'][:100]}...")
        
        # Contexto
        context = rag.get_context_for_query(query)
        print(f"\n📋 Contexto gerado ({len(context)} caracteres)")
        
        # Limpa arquivo de teste
        if test_file.exists():
            test_file.unlink()
        
        print("\n🎉 Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()