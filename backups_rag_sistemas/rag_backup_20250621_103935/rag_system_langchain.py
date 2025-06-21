#!/usr/bin/env python3
"""
Sistema RAG usando LangChain - Substituição do TensorFlow
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# LangChain imports
try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain.chains import RetrievalQA
    from langchain_community.llms import OpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Fallback
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
    FALLBACK_AVAILABLE = True
except ImportError:
    FALLBACK_AVAILABLE = False

import PyPDF2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGSystemLangChain:
    """Sistema RAG usando LangChain"""
    
    def __init__(self, data_dir: str = "rag_data", api_key: Optional[str] = None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.api_key = api_key
        
        if LANGCHAIN_AVAILABLE:
            self._init_langchain()
        elif FALLBACK_AVAILABLE:
            self._init_fallback()
        else:
            raise ImportError("Nem LangChain nem sentence-transformers disponíveis")
    
    def _init_langchain(self):
        """Inicializa com LangChain"""
        logger.info("Inicializando com LangChain")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        self.vectorstore = None
        self.load_vectorstore()
        self.mode = "langchain"
    
    def _init_fallback(self):
        """Inicializa com fallback"""
        logger.info("Inicializando com fallback")
        
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.documents = []
        self.document_metadata = []
        self.load_fallback_index()
        self.mode = "fallback"
    
    def add_document(self, pdf_path: str) -> bool:
        """Adiciona documento"""
        try:
            if self.mode == "langchain":
                return self._add_document_langchain(pdf_path)
            else:
                return self._add_document_fallback(pdf_path)
        except Exception as e:
            logger.error(f"Erro ao adicionar: {e}")
            return False
    
    def _add_document_langchain(self, pdf_path: str) -> bool:
        """Adiciona com LangChain"""
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        texts = self.text_splitter.split_documents(documents)
        
        for doc in texts:
            doc.metadata.update({
                'source_file': os.path.basename(pdf_path),
                'full_path': pdf_path
            })
        
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(texts, self.embeddings)
        else:
            self.vectorstore.add_documents(texts)
        
        self.save_vectorstore()
        logger.info(f"Documento adicionado: {pdf_path}")
        return True
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos"""
        try:
            if self.mode == "langchain":
                return self._search_langchain(query, top_k)
            else:
                return self._search_fallback(query, top_k)
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
    
    def _search_langchain(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca com LangChain"""
        if self.vectorstore is None:
            return []
        
        docs = self.vectorstore.similarity_search_with_score(query, k=top_k)
        
        results = []
        for i, (doc, score) in enumerate(docs):
            results.append({
                'text': doc.page_content,
                'metadata': doc.metadata,
                'score': float(score),
                'rank': i + 1
            })
        
        return results
    
    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """Obtém contexto"""
        results = self.search(query, top_k)
        
        if not results:
            return ""
        
        context_parts = []
        for result in results:
            metadata = result['metadata']
            source = metadata.get('source_file', 'Desconhecido')
            page = metadata.get('page', 'N/A')
            
            context_parts.append(
                f"[Fonte: {source}, Página: {page}]\n{result['text']}\n"
            )
        
        return "\n".join(context_parts)
    
    def save_vectorstore(self):
        """Salva vectorstore"""
        if self.vectorstore is not None:
            try:
                self.vectorstore.save_local(str(self.data_dir / "langchain_vectorstore"))
                logger.info("Vectorstore salvo")
            except Exception as e:
                logger.error(f"Erro ao salvar: {e}")
    
    def load_vectorstore(self):
        """Carrega vectorstore"""
        vectorstore_path = self.data_dir / "langchain_vectorstore"
        if vectorstore_path.exists():
            try:
                self.vectorstore = FAISS.load_local(str(vectorstore_path), self.embeddings)
                logger.info("Vectorstore carregado")
            except Exception as e:
                logger.error(f"Erro ao carregar: {e}")
                self.vectorstore = None
    
    # Métodos de fallback simplificados...
    def _add_document_fallback(self, pdf_path: str) -> bool:
        return False  # Implementação simplificada
    
    def _search_fallback(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return []  # Implementação simplificada
    
    def load_fallback_index(self):
        pass  # Implementação simplificada
    
    def get_document_list(self) -> List[Dict[str, Any]]:
        """Lista documentos"""
        return []
    
    def remove_document(self, filename: str) -> bool:
        """Remove um documento (funcionalidade limitada)"""
        # Nota: FAISS não suporta remoção eficiente de documentos
        # Para uma remoção real, seria necessário recriar todo o índice
        logger.warning("Remoção de documentos não implementada - requer recriação do índice")
        return False
    
    def clear_all(self):
        """Limpa tudo"""
        if self.mode == "langchain":
            self.vectorstore = None
        else:
            self.index = None
            self.documents = []
            self.document_metadata = []

# Função para compatibilidade com o código existente
def create_rag_system(data_dir: str = "rag_data", api_key: Optional[str] = None):
    """Cria uma instância do sistema RAG"""
    return RAGSystemLangChain(data_dir, api_key)

# Teste do sistema
if __name__ == "__main__":
    print("Testando Sistema RAG com LangChain...")
    
    rag = RAGSystemLangChain()
    print(f"Sistema inicializado em modo: {rag.mode}")
    
    # Teste básico
    if rag.mode == "langchain":
        print("✅ LangChain disponível - sistema completo")
    else:
        print("⚠️ Usando fallback - funcionalidade limitada")