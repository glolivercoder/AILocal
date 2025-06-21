#!/usr/bin/env python3
"""
Backup do Sistema RAG Funcional Original
Criado automaticamente antes da substituição pelo sistema ultra-simplificado
Data: 2024-06-21

Para restaurar este sistema:
1. Renomeie este arquivo para rag_system_functional.py
2. Remova o sistema atual
3. Instale as dependências: pip install -r requirements_rag_modern.txt
"""

"""
Sistema RAG Funcional - Integração Real com Ollama, OpenRouter e Docker
"""

import os
import json
import logging
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import hashlib

# LangChain imports
try:
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain.schema import Document
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
    except ImportError:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGSystemFunctional:
    """Sistema RAG Funcional com múltiplos backends"""
    
    def __init__(self, 
                 data_dir: str = "rag_data",
                 ollama_url: str = "http://localhost:11434",
                 openrouter_api_key: Optional[str] = None):
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Configurações dos backends
        self.ollama_url = ollama_url
        self.openrouter_api_key = openrouter_api_key
        
        # Estado do sistema
        self.vectorstore = None
        self.embeddings = None
        self.text_splitter = None
        self.documents_cache = {}
        
        # Inicializar sistema
        self._init_system()
        
    def _init_system(self):
        """Inicializa o sistema RAG"""
        logger.info("🚀 Inicializando Sistema RAG Funcional")
        
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain não disponível")
        
        # Inicializar embeddings
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"}
            )
            logger.info("✅ HuggingFace Embeddings carregado")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar embeddings: {e}")
            raise
            
        # Inicializar text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Carregar vectorstore existente
        self.load_vectorstore()
        
        # Testar conexões
        self._test_connections()
        
    def _test_connections(self):
        """Testa conexões com os backends"""
        # Testar Ollama
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                logger.info(f"✅ Ollama conectado - {len(models)} modelos disponíveis")
                self.ollama_available = True
            else:
                logger.warning("⚠️ Ollama não disponível")
                self.ollama_available = False
        except Exception as e:
            logger.warning(f"⚠️ Ollama não conectado: {e}")
            self.ollama_available = False
            
        # Testar OpenRouter
        if self.openrouter_api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json"
                }
                response = requests.get("https://openrouter.ai/api/v1/models", 
                                      headers=headers, timeout=5)
                if response.status_code == 200:
                    logger.info("✅ OpenRouter conectado")
                    self.openrouter_available = True
                else:
                    logger.warning("⚠️ OpenRouter não disponível")
                    self.openrouter_available = False
            except Exception as e:
                logger.warning(f"⚠️ OpenRouter não conectado: {e}")
                self.openrouter_available = False
        else:
            self.openrouter_available = False
    
    def add_document(self, file_path: str, document_type: str = "auto") -> bool:
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
            texts = self.text_splitter.split_documents(documents)
            
            # Adicionar metadados
            for doc in texts:
                doc.metadata.update({
                    "source_file": file_path.name,
                    "full_path": str(file_path),
                    "document_type": document_type,
                    "added_at": datetime.now().isoformat(),
                    "file_hash": self._get_file_hash(file_path)
                })
            
            # Adicionar ao vectorstore
            if self.vectorstore is None:
                self.vectorstore = FAISS.from_documents(texts, self.embeddings)
            else:
                self.vectorstore.add_documents(texts)
                
            # Salvar
            self.save_vectorstore()
            
            # Atualizar cache
            self.documents_cache[file_path.name] = {
                "path": str(file_path),
                "type": document_type,
                "added_at": datetime.now().isoformat(),
                "chunks": len(texts)
            }
            self._save_documents_cache()
            
            logger.info(f"✅ Documento adicionado: {file_path.name} ({len(texts)} chunks)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar documento: {e}")
            return False
    
    def _detect_document_type(self, file_path: Path) -> str:
        """Detecta tipo do documento"""
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return "pdf"
        elif suffix in [".txt", ".md"]:
            return "text"
        else:
            return "text"
    
    def _load_document(self, file_path: Path, document_type: str) -> List[Document]:
        """Carrega documento baseado no tipo"""
        try:
            if document_type == "pdf":
                loader = PyPDFLoader(str(file_path))
            else:
                loader = TextLoader(str(file_path), encoding="utf-8")
            
            return loader.load()
        except Exception as e:
            logger.error(f"❌ Erro ao carregar documento: {e}")
            return []
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Gera hash do arquivo"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos relevantes"""
        try:
            if self.vectorstore is None:
                logger.warning("⚠️ Vectorstore não inicializado")
                return []
                
            # Buscar documentos similares
            docs = self.vectorstore.similarity_search_with_score(query, k=top_k)
            
            results = []
            for i, (doc, score) in enumerate(docs):
                results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(1 / (1 + score)),
                    "rank": i + 1,
                    "source": doc.metadata.get("source_file", "Desconhecido")
                })
            
            logger.info(f"🔍 Busca realizada: {len(results)} resultados para \"{query}\"")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
            return []
    
    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """Obtém contexto formatado para uma query"""
        results = self.search(query, top_k)
        
        if not results:
            return "Nenhum contexto relevante encontrado."
        
        context_parts = []
        for result in results:
            metadata = result["metadata"]
            source = metadata.get("source_file", "Desconhecido")
            score = result["similarity_score"]
            
            context_parts.append(
                f"[Fonte: {source} | Relevância: {score:.2f}]\n{result['text']}\n"
            )
        
        return "\n" + "="*50 + "\n".join(context_parts)
    
    def get_document_list(self) -> List[Dict[str, Any]]:
        """Lista documentos carregados"""
        return list(self.documents_cache.values())
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status do sistema"""
        return {
            "vectorstore_loaded": self.vectorstore is not None,
            "documents_count": len(self.documents_cache),
            "ollama_available": getattr(self, "ollama_available", False),
            "openrouter_available": getattr(self, "openrouter_available", False),
            "embeddings_type": "HuggingFace"
        }
    
    def save_vectorstore(self):
        """Salva vectorstore"""
        if self.vectorstore is not None:
            try:
                vectorstore_path = self.data_dir / "vectorstore"
                self.vectorstore.save_local(str(vectorstore_path))
                logger.info("💾 Vectorstore salvo")
            except Exception as e:
                logger.error(f"❌ Erro ao salvar vectorstore: {e}")
    
    def load_vectorstore(self):
        """Carrega vectorstore"""
        try:
            vectorstore_path = self.data_dir / "vectorstore"
            if vectorstore_path.exists():
                self.vectorstore = FAISS.load_local(str(vectorstore_path), self.embeddings)
                logger.info("📂 Vectorstore carregado")
            
            # Carregar cache de documentos
            self._load_documents_cache()
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar vectorstore: {e}")
            self.vectorstore = None
    
    def _save_documents_cache(self):
        """Salva cache de documentos"""
        cache_path = self.data_dir / "documents_cache.json"
        with open(cache_path, "w") as f:
            json.dump(self.documents_cache, f, indent=2)
    
    def _load_documents_cache(self):
        """Carrega cache de documentos"""
        cache_path = self.data_dir / "documents_cache.json"
        if cache_path.exists():
            with open(cache_path, "r") as f:
                self.documents_cache = json.load(f)
        else:
            self.documents_cache = {}
    
    def clear_all(self):
        """Limpa todos os dados"""
        try:
            import shutil
            shutil.rmtree(self.data_dir)
            self.data_dir.mkdir(exist_ok=True)
            self.vectorstore = None
            self.documents_cache = {}
            logger.info("🗑️ Todos os dados foram limpos")
        except Exception as e:
            logger.error(f"❌ Erro ao limpar dados: {e}")

# Função de conveniência
def create_rag_system(data_dir: str = "rag_data", 
                     ollama_url: str = "http://localhost:11434",
                     openrouter_api_key: Optional[str] = None) -> RAGSystemFunctional:
    """Cria sistema RAG funcional"""
    return RAGSystemFunctional(
        data_dir=data_dir,
        ollama_url=ollama_url,
        openrouter_api_key=openrouter_api_key
    )