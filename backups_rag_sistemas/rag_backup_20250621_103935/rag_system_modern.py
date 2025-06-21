#!/usr/bin/env python3
"""
Sistema RAG Moderno - Versão 2024
Integração com ChromaDB, Qdrant, LangChain e múltiplos LLMs
Baseado nas melhores práticas de 2024
"""

import os
import json
import logging
import requests
import asyncio
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import hashlib
import uuid
from dataclasses import dataclass
from enum import Enum

# Core imports
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    import qdrant_client
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

# LangChain imports
try:
    from langchain_community.document_loaders import (
        PyPDFLoader, TextLoader, WebBaseLoader, CSVLoader
    )
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Sentence transformers fallback
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDBType(Enum):
    """Tipos de banco de dados vetoriais suportados"""
    CHROMADB = "chromadb"
    QDRANT = "qdrant"
    FAISS = "faiss"

class EmbeddingModel(Enum):
    """Modelos de embedding suportados"""
    MINILM = "sentence-transformers/all-MiniLM-L6-v2"
    MPNET = "sentence-transformers/all-mpnet-base-v2"
    BGE_SMALL = "BAAI/bge-small-en-v1.5"
    BGE_BASE = "BAAI/bge-base-en-v1.5"
    E5_SMALL = "intfloat/e5-small-v2"

@dataclass
class RAGConfig:
    """Configuração do sistema RAG"""
    data_dir: str = "rag_data_modern"
    vector_db_type: VectorDBType = VectorDBType.CHROMADB
    embedding_model: EmbeddingModel = EmbeddingModel.BGE_SMALL
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_retrieval: int = 5
    similarity_threshold: float = 0.7
    
    # Configurações específicas do ChromaDB
    chromadb_host: str = "localhost"
    chromadb_port: int = 8000
    chromadb_persist_directory: Optional[str] = None
    
    # Configurações específicas do Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "rag_collection"
    
    # APIs
    openrouter_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
class ModernRAGSystem:
    """Sistema RAG Moderno com múltiplos backends"""
    
    def __init__(self, config: RAGConfig):
        self.config = config
        self.data_dir = Path(config.data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Estado do sistema
        self.vector_db = None
        self.embeddings = None
        self.text_splitter = None
        self.documents_metadata = {}
        self.collection_name = "rag_documents"
        
        # Inicializar sistema
        self._init_system()
        
    def _init_system(self):
        """Inicializa o sistema RAG moderno"""
        logger.info("🚀 Inicializando Sistema RAG Moderno 2024")
        
        # Inicializar embeddings
        self._init_embeddings()
        
        # Inicializar text splitter
        self._init_text_splitter()
        
        # Inicializar banco de dados vetorial
        self._init_vector_db()
        
        # Carregar metadados existentes
        self._load_metadata()
        
        logger.info("✅ Sistema RAG Moderno inicializado com sucesso")
        
    def _init_embeddings(self):
        """Inicializa modelo de embeddings"""
        try:
            if LANGCHAIN_AVAILABLE:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=self.config.embedding_model.value,
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True}
                )
                logger.info(f"✅ Embeddings LangChain carregado: {self.config.embedding_model.value}")
            elif SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embeddings = SentenceTransformer(self.config.embedding_model.value)
                logger.info(f"✅ Embeddings SentenceTransformers carregado: {self.config.embedding_model.value}")
            else:
                raise RuntimeError("Nenhum modelo de embedding disponível")
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar embeddings: {e}")
            # Fallback para modelo menor
            try:
                if LANGCHAIN_AVAILABLE:
                    self.embeddings = HuggingFaceEmbeddings(
                        model_name=EmbeddingModel.MINILM.value,
                        model_kwargs={"device": "cpu"}
                    )
                    logger.info("✅ Fallback para MiniLM embeddings")
                else:
                    raise RuntimeError("Falha no fallback de embeddings")
            except Exception as fallback_error:
                logger.error(f"❌ Falha no fallback: {fallback_error}")
                raise
                
    def _init_text_splitter(self):
        """Inicializa divisor de texto"""
        if LANGCHAIN_AVAILABLE:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
        else:
            # Implementação simples sem LangChain
            self.text_splitter = SimpleTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )
        logger.info("✅ Text splitter inicializado")
        
    def _init_vector_db(self):
        """Inicializa banco de dados vetorial"""
        if self.config.vector_db_type == VectorDBType.CHROMADB:
            self._init_chromadb()
        elif self.config.vector_db_type == VectorDBType.QDRANT:
            self._init_qdrant()
        else:
            raise ValueError(f"Tipo de DB não suportado: {self.config.vector_db_type}")
            
    def _init_chromadb(self):
        """Inicializa ChromaDB"""
        if not CHROMADB_AVAILABLE:
            raise RuntimeError("ChromaDB não disponível. Instale com: pip install chromadb")
            
        try:
            # Configurar ChromaDB
            if self.config.chromadb_persist_directory:
                # Modo persistente local
                self.chroma_client = chromadb.PersistentClient(
                    path=self.config.chromadb_persist_directory
                )
            else:
                # Modo em memória
                self.chroma_client = chromadb.Client()
                
            # Criar ou obter coleção
            try:
                self.vector_db = self.chroma_client.get_collection(
                    name=self.collection_name
                )
                logger.info(f"📂 Coleção ChromaDB carregada: {self.collection_name}")
            except:
                self.vector_db = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info(f"🆕 Nova coleção ChromaDB criada: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar ChromaDB: {e}")
            raise
            
    def _init_qdrant(self):
        """Inicializa Qdrant"""
        if not QDRANT_AVAILABLE:
            raise RuntimeError("Qdrant não disponível. Instale com: pip install qdrant-client")
            
        try:
            self.qdrant_client = qdrant_client.QdrantClient(
                host=self.config.qdrant_host,
                port=self.config.qdrant_port
            )
            
            # Verificar se coleção existe
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.config.qdrant_collection_name not in collection_names:
                # Criar coleção
                self.qdrant_client.create_collection(
                    collection_name=self.config.qdrant_collection_name,
                    vectors_config=VectorParams(
                        size=384,  # Tamanho padrão para most embeddings
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"🆕 Nova coleção Qdrant criada: {self.config.qdrant_collection_name}")
            else:
                logger.info(f"📂 Coleção Qdrant carregada: {self.config.qdrant_collection_name}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Qdrant: {e}")
            raise
            
    def add_document(self, file_path: Union[str, Path], 
                    document_type: str = "auto",
                    metadata: Optional[Dict] = None) -> bool:
        """Adiciona documento ao sistema RAG"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"❌ Arquivo não encontrado: {file_path}")
                return False
                
            logger.info(f"📄 Processando documento: {file_path.name}")
            
            # Detectar tipo de documento
            if document_type == "auto":
                document_type = self._detect_document_type(file_path)
            
            # Carregar documento
            documents = self._load_document(file_path, document_type)
            if not documents:
                return False
                
            # Dividir em chunks
            if LANGCHAIN_AVAILABLE:
                texts = self.text_splitter.split_documents(documents)
            else:
                # Implementação simples
                texts = []
                for doc in documents:
                    chunks = self.text_splitter.split_text(doc.page_content)
                    for chunk in chunks:
                        texts.append(Document(
                            page_content=chunk,
                            metadata=doc.metadata
                        ))
            
            # Adicionar metadados
            doc_id = str(uuid.uuid4())
            base_metadata = {
                "document_id": doc_id,
                "source_file": file_path.name,
                "full_path": str(file_path),
                "document_type": document_type,
                "added_at": datetime.now().isoformat(),
                "file_hash": self._get_file_hash(file_path),
                "total_chunks": len(texts)
            }
            
            if metadata:
                base_metadata.update(metadata)
            
            for i, doc in enumerate(texts):
                doc.metadata.update(base_metadata)
                doc.metadata["chunk_id"] = f"{doc_id}_{i}"
                doc.metadata["chunk_index"] = i
            
            # Adicionar ao banco vetorial
            success = self._add_to_vector_db(texts)
            
            if success:
                # Atualizar metadados
                self.documents_metadata[doc_id] = {
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "document_type": document_type,
                    "added_at": datetime.now().isoformat(),
                    "chunks_count": len(texts),
                    "file_hash": self._get_file_hash(file_path)
                }
                self._save_metadata()
                
                logger.info(f"✅ Documento adicionado: {file_path.name} ({len(texts)} chunks)")
                return True
            else:
                logger.error(f"❌ Falha ao adicionar documento ao banco vetorial")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar documento: {e}")
            return False
            
    def _detect_document_type(self, file_path: Path) -> str:
        """Detecta tipo do documento"""
        suffix = file_path.suffix.lower()
        type_mapping = {
            ".pdf": "pdf",
            ".txt": "text",
            ".md": "markdown",
            ".csv": "csv",
            ".json": "json",
            ".html": "html",
            ".htm": "html"
        }
        return type_mapping.get(suffix, "text")
        
    def _load_document(self, file_path: Path, document_type: str) -> List[Document]:
        """Carrega documento baseado no tipo"""
        try:
            if not LANGCHAIN_AVAILABLE:
                # Implementação simples sem LangChain
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return [Document(
                    page_content=content,
                    metadata={"source": str(file_path)}
                )]
                
            # Usar LangChain loaders
            if document_type == "pdf":
                loader = PyPDFLoader(str(file_path))
            elif document_type == "csv":
                loader = CSVLoader(str(file_path))
            else:
                loader = TextLoader(str(file_path), encoding="utf-8")
            
            return loader.load()
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar documento: {e}")
            return []
            
    def _get_file_hash(self, file_path: Path) -> str:
        """Gera hash MD5 do arquivo"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"❌ Erro ao gerar hash: {e}")
            return ""
            
    def _add_to_vector_db(self, documents: List[Document]) -> bool:
        """Adiciona documentos ao banco vetorial"""
        try:
            if self.config.vector_db_type == VectorDBType.CHROMADB:
                return self._add_to_chromadb(documents)
            elif self.config.vector_db_type == VectorDBType.QDRANT:
                return self._add_to_qdrant(documents)
            else:
                logger.error(f"❌ Tipo de DB não suportado: {self.config.vector_db_type}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar ao banco vetorial: {e}")
            return False
            
    def _add_to_chromadb(self, documents: List[Document]) -> bool:
        """Adiciona documentos ao ChromaDB"""
        try:
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            ids = [doc.metadata.get("chunk_id", str(uuid.uuid4())) for doc in documents]
            
            # Gerar embeddings
            if LANGCHAIN_AVAILABLE:
                embeddings = self.embeddings.embed_documents(texts)
            else:
                embeddings = self.embeddings.encode(texts).tolist()
            
            # Adicionar ao ChromaDB
            self.vector_db.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar ao ChromaDB: {e}")
            return False
            
    def _add_to_qdrant(self, documents: List[Document]) -> bool:
        """Adiciona documentos ao Qdrant"""
        try:
            points = []
            
            for doc in documents:
                # Gerar embedding
                if LANGCHAIN_AVAILABLE:
                    embedding = self.embeddings.embed_query(doc.page_content)
                else:
                    embedding = self.embeddings.encode([doc.page_content])[0].tolist()
                
                # Criar ponto
                point = PointStruct(
                    id=doc.metadata.get("chunk_id", str(uuid.uuid4())),
                    vector=embedding,
                    payload={
                        "text": doc.page_content,
                        **doc.metadata
                    }
                )
                points.append(point)
            
            # Adicionar pontos
            self.qdrant_client.upsert(
                collection_name=self.config.qdrant_collection_name,
                points=points
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar ao Qdrant: {e}")
            return False
            
    def search(self, query: str, top_k: Optional[int] = None, 
              filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Busca documentos relevantes"""
        try:
            if top_k is None:
                top_k = self.config.top_k_retrieval
                
            if self.config.vector_db_type == VectorDBType.CHROMADB:
                return self._search_chromadb(query, top_k, filters)
            elif self.config.vector_db_type == VectorDBType.QDRANT:
                return self._search_qdrant(query, top_k, filters)
            else:
                logger.error(f"❌ Tipo de DB não suportado: {self.config.vector_db_type}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
            return []
            
    def _search_chromadb(self, query: str, top_k: int, 
                        filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Busca no ChromaDB"""
        try:
            # Gerar embedding da query
            if LANGCHAIN_AVAILABLE:
                query_embedding = self.embeddings.embed_query(query)
            else:
                query_embedding = self.embeddings.encode([query])[0].tolist()
            
            # Buscar
            results = self.vector_db.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters
            )
            
            # Formatar resultados
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity_score": 1 - results['distances'][0][i],  # Converter distância para similaridade
                    "rank": i + 1,
                    "source": results['metadatas'][0][i].get('source_file', 'Desconhecido')
                })
            
            logger.info(f"🔍 Busca ChromaDB: {len(formatted_results)} resultados para \"{query}\"")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Erro na busca ChromaDB: {e}")
            return []
            
    def _search_qdrant(self, query: str, top_k: int, 
                      filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Busca no Qdrant"""
        try:
            # Gerar embedding da query
            if LANGCHAIN_AVAILABLE:
                query_embedding = self.embeddings.embed_query(query)
            else:
                query_embedding = self.embeddings.encode([query])[0].tolist()
            
            # Buscar
            results = self.qdrant_client.search(
                collection_name=self.config.qdrant_collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=filters
            )
            
            # Formatar resultados
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append({
                    "text": result.payload.get('text', ''),
                    "metadata": {k: v for k, v in result.payload.items() if k != 'text'},
                    "similarity_score": result.score,
                    "rank": i + 1,
                    "source": result.payload.get('source_file', 'Desconhecido')
                })
            
            logger.info(f"🔍 Busca Qdrant: {len(formatted_results)} resultados para \"{query}\"")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Erro na busca Qdrant: {e}")
            return []
            
    def get_context_for_query(self, query: str, top_k: Optional[int] = None) -> str:
        """Obtém contexto formatado para uma query"""
        if top_k is None:
            top_k = self.config.top_k_retrieval
            
        results = self.search(query, top_k)
        
        if not results:
            return "Nenhum contexto relevante encontrado na base de conhecimento."
        
        # Filtrar por threshold de similaridade
        filtered_results = [
            r for r in results 
            if r['similarity_score'] >= self.config.similarity_threshold
        ]
        
        if not filtered_results:
            return f"Nenhum contexto com similaridade suficiente encontrado (threshold: {self.config.similarity_threshold})."
        
        context_parts = []
        for result in filtered_results:
            metadata = result["metadata"]
            source = metadata.get("source_file", "Desconhecido")
            score = result["similarity_score"]
            
            context_parts.append(
                f"[Fonte: {source} | Relevância: {score:.3f}]\n{result['text']}\n"
            )
        
        context = "\n" + "="*60 + "\n".join(context_parts)
        logger.info(f"📋 Contexto gerado com {len(filtered_results)} fragmentos relevantes")
        return context
        
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status detalhado do sistema"""
        status = {
            "system_version": "RAG Modern 2024",
            "vector_db_type": self.config.vector_db_type.value,
            "embedding_model": self.config.embedding_model.value,
            "documents_count": len(self.documents_metadata),
            "chunk_size": self.config.chunk_size,
            "chunk_overlap": self.config.chunk_overlap,
            "similarity_threshold": self.config.similarity_threshold,
            "langchain_available": LANGCHAIN_AVAILABLE,
            "chromadb_available": CHROMADB_AVAILABLE,
            "qdrant_available": QDRANT_AVAILABLE,
            "sentence_transformers_available": SENTENCE_TRANSFORMERS_AVAILABLE
        }
        
        # Status específico do banco vetorial
        if self.config.vector_db_type == VectorDBType.CHROMADB and self.vector_db:
            try:
                collection_info = self.vector_db.get()
                status["vector_db_status"] = {
                    "connected": True,
                    "total_vectors": len(collection_info['ids']),
                    "collection_name": self.collection_name
                }
            except Exception as e:
                status["vector_db_status"] = {"connected": False, "error": str(e)}
                
        elif self.config.vector_db_type == VectorDBType.QDRANT:
            try:
                collection_info = self.qdrant_client.get_collection(
                    self.config.qdrant_collection_name
                )
                status["vector_db_status"] = {
                    "connected": True,
                    "total_vectors": collection_info.points_count,
                    "collection_name": self.config.qdrant_collection_name
                }
            except Exception as e:
                status["vector_db_status"] = {"connected": False, "error": str(e)}
        
        return status
        
    def get_documents_list(self) -> List[Dict[str, Any]]:
        """Lista todos os documentos carregados"""
        return list(self.documents_metadata.values())
        
    def remove_document(self, document_id: str) -> bool:
        """Remove documento do sistema"""
        try:
            if document_id not in self.documents_metadata:
                logger.error(f"❌ Documento não encontrado: {document_id}")
                return False
                
            # Remover do banco vetorial
            if self.config.vector_db_type == VectorDBType.CHROMADB:
                # ChromaDB - remover por filtro de metadata
                try:
                    self.vector_db.delete(
                        where={"document_id": document_id}
                    )
                except Exception as e:
                    logger.error(f"❌ Erro ao remover do ChromaDB: {e}")
                    return False
                    
            elif self.config.vector_db_type == VectorDBType.QDRANT:
                # Qdrant - remover por filtro
                try:
                    self.qdrant_client.delete(
                        collection_name=self.config.qdrant_collection_name,
                        points_selector={
                            "filter": {
                                "must": [
                                    {"key": "document_id", "match": {"value": document_id}}
                                ]
                            }
                        }
                    )
                except Exception as e:
                    logger.error(f"❌ Erro ao remover do Qdrant: {e}")
                    return False
            
            # Remover dos metadados
            del self.documents_metadata[document_id]
            self._save_metadata()
            
            logger.info(f"🗑️ Documento removido: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao remover documento: {e}")
            return False
            
    def clear_all_documents(self) -> bool:
        """Remove todos os documentos"""
        try:
            if self.config.vector_db_type == VectorDBType.CHROMADB:
                # Recriar coleção
                self.chroma_client.delete_collection(self.collection_name)
                self.vector_db = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                
            elif self.config.vector_db_type == VectorDBType.QDRANT:
                # Limpar coleção
                self.qdrant_client.delete(
                    collection_name=self.config.qdrant_collection_name,
                    points_selector={"filter": {"must": []}}
                )
            
            # Limpar metadados
            self.documents_metadata = {}
            self._save_metadata()
            
            logger.info("🗑️ Todos os documentos foram removidos")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar documentos: {e}")
            return False
            
    def _save_metadata(self):
        """Salva metadados dos documentos"""
        try:
            metadata_path = self.data_dir / "documents_metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.documents_metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar metadados: {e}")
            
    def _load_metadata(self):
        """Carrega metadados dos documentos"""
        try:
            metadata_path = self.data_dir / "documents_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, "r", encoding="utf-8") as f:
                    self.documents_metadata = json.load(f)
                logger.info(f"📂 Metadados carregados: {len(self.documents_metadata)} documentos")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar metadados: {e}")
            self.documents_metadata = {}

class SimpleTextSplitter:
    """Divisor de texto simples para quando LangChain não está disponível"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def split_text(self, text: str) -> List[str]:
        """Divide texto em chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap
            
        return chunks

# Funções de conveniência
def create_modern_rag_system(
    vector_db_type: VectorDBType = VectorDBType.CHROMADB,
    embedding_model: EmbeddingModel = EmbeddingModel.BGE_SMALL,
    data_dir: str = "rag_data_modern",
    **kwargs
) -> ModernRAGSystem:
    """Cria sistema RAG moderno com configurações padrão"""
    config = RAGConfig(
        data_dir=data_dir,
        vector_db_type=vector_db_type,
        embedding_model=embedding_model,
        **kwargs
    )
    return ModernRAGSystem(config)

def create_chromadb_rag_system(
    data_dir: str = "rag_data_chromadb",
    persist_directory: Optional[str] = None,
    embedding_model: EmbeddingModel = EmbeddingModel.BGE_SMALL
) -> ModernRAGSystem:
    """Cria sistema RAG com ChromaDB"""
    config = RAGConfig(
        data_dir=data_dir,
        vector_db_type=VectorDBType.CHROMADB,
        embedding_model=embedding_model,
        chromadb_persist_directory=persist_directory or f"{data_dir}/chromadb"
    )
    return ModernRAGSystem(config)

def create_qdrant_rag_system(
    data_dir: str = "rag_data_qdrant",
    qdrant_host: str = "localhost",
    qdrant_port: int = 6333,
    collection_name: str = "rag_collection",
    embedding_model: EmbeddingModel = EmbeddingModel.BGE_SMALL
) -> ModernRAGSystem:
    """Cria sistema RAG com Qdrant"""
    config = RAGConfig(
        data_dir=data_dir,
        vector_db_type=VectorDBType.QDRANT,
        embedding_model=embedding_model,
        qdrant_host=qdrant_host,
        qdrant_port=qdrant_port,
        qdrant_collection_name=collection_name
    )
    return ModernRAGSystem(config)

if __name__ == "__main__":
    # Exemplo de uso
    print("🚀 Sistema RAG Moderno 2024")
    print("Dependências disponíveis:")
    print(f"  - LangChain: {LANGCHAIN_AVAILABLE}")
    print(f"  - ChromaDB: {CHROMADB_AVAILABLE}")
    print(f"  - Qdrant: {QDRANT_AVAILABLE}")
    print(f"  - SentenceTransformers: {SENTENCE_TRANSFORMERS_AVAILABLE}")
    
    # Criar sistema RAG
    try:
        rag = create_modern_rag_system()
        print("\n✅ Sistema RAG criado com sucesso!")
        print(f"Status: {rag.get_system_status()}")
    except Exception as e:
        print(f"\n❌ Erro ao criar sistema RAG: {e}")