#!/usr/bin/env python3
"""
Sistema RAG (Retrieval-Augmented Generation) para processamento de PDFs
Usando PyPDF2 para extração e FAISS para indexação vetorial
"""

import os
import json
import pickle
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import PyPDF2
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import re

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGSystem:
    """Sistema RAG para processamento e busca em documentos PDF"""
    
    def __init__(self, data_dir: str = "rag_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Modelo de embeddings (usando um modelo pequeno e rápido)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Índice FAISS
        self.index = None
        self.documents = []
        self.document_metadata = []
        
        # Carregar dados existentes se disponível
        self.load_index()
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extrai texto de um PDF e divide em chunks"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                chunks = []
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    
                    # Dividir texto em chunks menores (aproximadamente 500 caracteres)
                    text_chunks = self.split_text_into_chunks(text, chunk_size=500)
                    
                    for chunk_idx, chunk in enumerate(text_chunks):
                        if chunk.strip():  # Ignorar chunks vazios
                            chunks.append({
                                'text': chunk.strip(),
                                'page': page_num + 1,
                                'chunk_id': chunk_idx,
                                'source_file': os.path.basename(pdf_path),
                                'full_path': pdf_path
                            })
                
                logger.info(f"Extraídos {len(chunks)} chunks do PDF: {pdf_path}")
                return chunks
                
        except Exception as e:
            logger.error(f"Erro ao processar PDF {pdf_path}: {e}")
            return []
    
    def split_text_into_chunks(self, text: str, chunk_size: int = 500) -> List[str]:
        """Divide texto em chunks menores"""
        # Remover quebras de linha extras
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Dividir por sentenças primeiro
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        # Adicionar último chunk se não estiver vazio
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def add_document(self, pdf_path: str) -> bool:
        """Adiciona um documento PDF ao sistema RAG"""
        try:
            # Extrair chunks do PDF
            chunks = self.extract_text_from_pdf(pdf_path)
            
            if not chunks:
                return False
            
            # Gerar embeddings para os chunks
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
            
            # Adicionar ao índice FAISS
            if self.index is None:
                # Criar novo índice
                dimension = embeddings.shape[1]
                self.index = faiss.IndexFlatIP(dimension)  # Inner Product para similaridade de cosseno
            
            # Normalizar embeddings para similaridade de cosseno
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype('float32'))
            
            # Adicionar metadados
            self.documents.extend(texts)
            self.document_metadata.extend(chunks)
            
            # Salvar índice atualizado
            self.save_index()
            
            logger.info(f"Documento adicionado com sucesso: {pdf_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar documento {pdf_path}: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos similares à query"""
        try:
            if self.index is None or len(self.documents) == 0:
                return []
            
            # Gerar embedding da query
            query_embedding = self.embedding_model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Buscar no índice
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.documents):
                    results.append({
                        'text': self.documents[idx],
                        'metadata': self.document_metadata[idx],
                        'score': float(score),
                        'rank': i + 1
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
    
    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """Obtém contexto relevante para uma query"""
        results = self.search(query, top_k)
        
        if not results:
            return ""
        
        context_parts = []
        for result in results:
            metadata = result['metadata']
            context_parts.append(
                f"[Fonte: {metadata['source_file']}, Página: {metadata['page']}]\n"
                f"{result['text']}\n"
            )
        
        return "\n".join(context_parts)
    
    def save_index(self):
        """Salva o índice FAISS e metadados"""
        try:
            if self.index is not None:
                # Salvar índice FAISS
                faiss.write_index(self.index, str(self.data_dir / "faiss_index.idx"))
                
                # Salvar documentos e metadados
                with open(self.data_dir / "documents.pkl", 'wb') as f:
                    pickle.dump(self.documents, f)
                
                with open(self.data_dir / "metadata.pkl", 'wb') as f:
                    pickle.dump(self.document_metadata, f)
                
                logger.info("Índice salvo com sucesso")
                
        except Exception as e:
            logger.error(f"Erro ao salvar índice: {e}")
    
    def load_index(self):
        """Carrega o índice FAISS e metadados"""
        try:
            index_path = self.data_dir / "faiss_index.idx"
            documents_path = self.data_dir / "documents.pkl"
            metadata_path = self.data_dir / "metadata.pkl"
            
            if index_path.exists() and documents_path.exists() and metadata_path.exists():
                # Carregar índice FAISS
                self.index = faiss.read_index(str(index_path))
                
                # Carregar documentos e metadados
                with open(documents_path, 'rb') as f:
                    self.documents = pickle.load(f)
                
                with open(metadata_path, 'rb') as f:
                    self.document_metadata = pickle.load(f)
                
                logger.info(f"Índice carregado com {len(self.documents)} documentos")
                
        except Exception as e:
            logger.error(f"Erro ao carregar índice: {e}")
            self.index = None
            self.documents = []
            self.document_metadata = []
    
    def get_document_list(self) -> List[Dict[str, Any]]:
        """Retorna lista de documentos processados"""
        if not self.document_metadata:
            return []
        
        # Agrupar por arquivo
        files = {}
        for metadata in self.document_metadata:
            source_file = metadata['source_file']
            if source_file not in files:
                files[source_file] = {
                    'filename': source_file,
                    'full_path': metadata['full_path'],
                    'pages': set(),
                    'chunks': 0
                }
            files[source_file]['pages'].add(metadata['page'])
            files[source_file]['chunks'] += 1
        
        # Converter para lista
        result = []
        for file_info in files.values():
            result.append({
                'filename': file_info['filename'],
                'full_path': file_info['full_path'],
                'pages': sorted(list(file_info['pages'])),
                'chunks': file_info['chunks']
            })
        
        return result
    
    def remove_document(self, filename: str) -> bool:
        """Remove um documento do sistema"""
        try:
            # Encontrar chunks do documento
            indices_to_remove = []
            for i, metadata in enumerate(self.document_metadata):
                if metadata['source_file'] == filename:
                    indices_to_remove.append(i)
            
            if not indices_to_remove:
                return False
            
            # Remover do índice FAISS
            if self.index is not None:
                # FAISS não suporta remoção direta, então recriamos o índice
                remaining_embeddings = []
                remaining_docs = []
                remaining_metadata = []
                
                for i in range(len(self.documents)):
                    if i not in indices_to_remove:
                        remaining_docs.append(self.documents[i])
                        remaining_metadata.append(self.document_metadata[i])
                
                if remaining_docs:
                    # Recriar embeddings
                    embeddings = self.embedding_model.encode(remaining_docs)
                    faiss.normalize_L2(embeddings)
                    
                    # Recriar índice
                    dimension = embeddings.shape[1]
                    self.index = faiss.IndexFlatIP(dimension)
                    self.index.add(embeddings.astype('float32'))
                    
                    self.documents = remaining_docs
                    self.document_metadata = remaining_metadata
                else:
                    # Sem documentos restantes
                    self.index = None
                    self.documents = []
                    self.document_metadata = []
                
                # Salvar índice atualizado
                self.save_index()
                
                logger.info(f"Documento removido: {filename}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao remover documento {filename}: {e}")
            return False
    
    def clear_all(self):
        """Limpa todos os documentos do sistema"""
        try:
            self.index = None
            self.documents = []
            self.document_metadata = []
            
            # Remover arquivos salvos
            for file_path in self.data_dir.glob("*"):
                file_path.unlink()
            
            logger.info("Todos os documentos removidos")
            
        except Exception as e:
            logger.error(f"Erro ao limpar documentos: {e}")

# Função de teste
def test_rag_system():
    """Testa o sistema RAG"""
    print("=== Teste do Sistema RAG ===\n")
    
    rag = RAGSystem()
    
    # Mostrar documentos existentes
    documents = rag.get_document_list()
    print(f"Documentos no sistema: {len(documents)}")
    for doc in documents:
        print(f"- {doc['filename']} ({doc['chunks']} chunks, páginas {doc['pages']})")
    
    print("\n=== Teste concluído ===")

if __name__ == "__main__":
    test_rag_system() 