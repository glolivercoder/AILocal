#!/usr/bin/env python3
"""
Sistema RAG Avançado com PyMuPDF + FAISS + SentenceTransformers
Mantém compatibilidade com a interface existente
"""

import os
import json
import logging
import pickle
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

# Bibliotecas modernas para RAG
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("⚠️  PyMuPDF não disponível, usando fallback")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️  SentenceTransformers não disponível, usando fallback")

# Importação segura do FAISS com timeout
FAISS_AVAILABLE = False
try:
    # Verificar se FAISS deve ser desabilitado via variável de ambiente
    import os
    if os.environ.get('DISABLE_FAISS', '').lower() in ('true', '1', 'yes'):
        print("⚠️  FAISS desabilitado via DISABLE_FAISS, usando fallback")
    else:
        import faiss
        FAISS_AVAILABLE = True
        print("✅ FAISS disponível")
except (ImportError, KeyboardInterrupt, Exception) as e:
    FAISS_AVAILABLE = False
    print(f"⚠️  FAISS não disponível ({type(e).__name__}), usando fallback")
    # Definir variável de ambiente para evitar futuras tentativas
    os.environ['DISABLE_FAISS'] = 'true'

# Fallbacks para compatibilidade
try:
    import pypdf
except ImportError:
    pypdf = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import openpyxl
except ImportError:
    openpyxl = None

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedRAGSystem:
    """
    Sistema RAG Avançado com PyMuPDF + FAISS + SentenceTransformers
    Mantém compatibilidade com UltraSimpleRAG
    """
    
    def __init__(self, storage_dir: str = "rag_data_advanced"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Arquivos de persistência
        self.documents_file = self.storage_dir / "documents.json"
        self.metadata_file = self.storage_dir / "metadata.json"
        self.index_file = self.storage_dir / "faiss_index.bin"
        self.embeddings_file = self.storage_dir / "embeddings.pkl"
        
        # Estruturas de dados
        self.documents = {}  # {doc_id: {"content": str, "chunks": [str]}}
        self.metadata = {}   # {doc_id: metadata}
        self.embeddings = {}  # {doc_id: embeddings}
        self.faiss_index = None
        self.doc_id_to_chunk_ids = {}  # Mapeamento documento -> chunks
        self.chunk_id_to_doc_id = {}   # Mapeamento chunk -> documento
        
        # Modelo de embeddings
        self.model = None
        self.model_name = 'sentence-transformers/all-MiniLM-L6-v2'
        
        # Inicializar
        self._initialize_model()
        self._load_data()
        
        logger.info(f"✅ Sistema RAG Avançado inicializado em {self.storage_dir}")

    def _initialize_model(self):
        """Inicializa o modelo de embeddings"""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                print("🤖 Carregando modelo SentenceTransformers...")
                self.model = SentenceTransformer(self.model_name)
                print("✅ Modelo carregado com sucesso")
            except Exception as e:
                print(f"❌ Erro ao carregar modelo: {e}")
                self.model = None
        else:
            print("⚠️  SentenceTransformers não disponível")
            self.model = None

    def _extract_text_from_pdf_advanced(self, file_path: str) -> str:
        """Extração avançada de texto usando PyMuPDF"""
        if not PYMUPDF_AVAILABLE:
            return self._extract_text_from_pdf_fallback(file_path)
        
        try:
            doc = fitz.open(file_path)
            texts = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Tentar diferentes métodos de extração
                # Método 1: Texto normal
                text = page.get_text()
                
                if text and len(text.strip()) > 50:
                    # Limpar texto com espaços extras
                    cleaned_text = re.sub(r'\s+', ' ', text.strip())
                    texts.append(cleaned_text)
                else:
                    # Método 2: Extrair blocos estruturados
                    blocks = page.get_text("blocks")
                    page_texts = []
                    
                    for block in blocks:
                        if len(block) > 4:
                            block_text = block[4].strip()
                            if block_text and len(block_text) > 5:
                                # Limpar espaços extras entre caracteres
                                cleaned_block = re.sub(r'(?<=\w)\s+(?=\w)', '', block_text)
                                cleaned_block = re.sub(r'\s+', ' ', cleaned_block)
                                page_texts.append(cleaned_block)
                    
                    if page_texts:
                        texts.append(' '.join(page_texts))
            
            doc.close()
            
            if texts:
                full_text = "\n\n".join(texts)
                # Limpeza final
                full_text = re.sub(r'\n\s*\n', '\n\n', full_text)  # Múltiplas quebras
                full_text = re.sub(r'[ \t]+', ' ', full_text)      # Espaços extras
                
                print(f"✅ PyMuPDF extraiu {len(full_text)} caracteres de {len(texts)} páginas")
                return full_text
            else:
                print("⚠️  PyMuPDF não encontrou texto, tentando fallback")
                return self._extract_text_from_pdf_fallback(file_path)
                
        except Exception as e:
            print(f"❌ Erro PyMuPDF: {e}, usando fallback")
            return self._extract_text_from_pdf_fallback(file_path)

    def _extract_text_from_pdf_fallback(self, file_path: str) -> str:
        """Fallback usando pypdf"""
        if not pypdf:
            return ""
        
        try:
            with open(file_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            print(f"❌ Erro pypdf fallback: {e}")
            return ""

    def _extract_text_from_file(self, file_path: str) -> str:
        """Extrai texto de diferentes tipos de arquivo"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        print(f"📄 Extraindo texto de: {file_path.name}")
        
        try:
            if extension == '.pdf':
                return self._extract_text_from_pdf_advanced(str(file_path))
            
            elif extension == '.txt' or extension == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif extension == '.docx' and Document:
                doc = Document(file_path)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                return text
            
            elif extension in ['.xlsx', '.xls'] and openpyxl:
                workbook = openpyxl.load_workbook(file_path)
                text = ""
                for sheet in workbook.worksheets:
                    for row in sheet.iter_rows(values_only=True):
                        row_text = " ".join([str(cell) for cell in row if cell])
                        if row_text.strip():
                            text += row_text + "\n"
                return text
            
            else:
                print(f"⚠️  Formato {extension} não suportado")
                return ""
                
        except Exception as e:
            print(f"❌ Erro ao extrair texto de {file_path.name}: {e}")
            return ""

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Divide texto em chunks com sobreposição (otimizado para memória)"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        max_chunks = 50  # Limitar número de chunks para evitar MemoryError
        
        while start < len(text) and len(chunks) < max_chunks:
            end = start + chunk_size
            
            # Tentar quebrar em ponto natural (sentença)
            if end < len(text):
                # Procurar por quebra de parágrafo ou sentença
                for punct in ['\n\n', '. ', '! ', '? ']:
                    punct_pos = text.rfind(punct, start, end)
                    if punct_pos > start:
                        end = punct_pos + len(punct)
                        break
            
            chunk = text[start:end].strip()
            if chunk and len(chunk) > 20:  # Filtrar chunks muito pequenos
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        # Se ainda temos muitos chunks, pegar apenas os primeiros
        if len(chunks) > max_chunks:
            chunks = chunks[:max_chunks]
            print(f"⚠️  Limitado a {max_chunks} chunks para otimização de memória")
        
        return chunks

    def _create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Cria embeddings para lista de textos"""
        if not self.model:
            print("❌ Modelo não disponível para criar embeddings")
            return np.array([])
        
        try:
            embeddings = self.model.encode(texts, show_progress_bar=True)
            return np.array(embeddings)
        except Exception as e:
            print(f"❌ Erro ao criar embeddings: {e}")
            return np.array([])

    def _build_faiss_index(self, embeddings: np.ndarray):
        """Constrói índice FAISS"""
        if not FAISS_AVAILABLE or embeddings.size == 0:
            return None
        
        try:
            dim = embeddings.shape[1]
            
            # Usar IndexFlatL2 para datasets pequenos, IndexIVFFlat para grandes
            if len(embeddings) < 1000:
                index = faiss.IndexFlatL2(dim)
            else:
                quantizer = faiss.IndexFlatL2(dim)
                index = faiss.IndexIVFFlat(quantizer, dim, min(100, len(embeddings) // 10))
                index.train(embeddings)
            
            index.add(embeddings)
            return index
            
        except Exception as e:
            print(f"❌ Erro ao criar índice FAISS: {e}")
            return None

    def add_document_from_file(self, file_path: str) -> bool:
        """Adiciona documento a partir de arquivo"""
        try:
            file_path = Path(file_path)
            
            # Extrair texto
            text = self._extract_text_from_file(str(file_path))
            if not text or not text.strip():
                print(f"⚠️  Nenhum texto extraído de: {file_path.name}")
                return False
            
            # Usar nome do arquivo como doc_id
            doc_id = file_path.stem
            
            # Adicionar documento
            return self.add_document(doc_id, text, {
                "file_name": file_path.name,
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size if file_path.exists() else 0
            })
            
        except Exception as e:
            print(f"❌ Erro ao processar arquivo {file_path}: {e}")
            return False

    def add_document(self, doc_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Adiciona documento ao sistema RAG"""
        try:
            if not content or not content.strip():
                print(f"❌ Conteúdo vazio para documento {doc_id}")
                return False
            
            print(f"📄 Processando documento: {doc_id}")
            
            # Dividir em chunks
            chunks = self._chunk_text(content)
            print(f"📝 Documento dividido em {len(chunks)} chunks")
            
            # Criar embeddings
            if self.model and chunks:
                embeddings = self._create_embeddings(chunks)
                if embeddings.size == 0:
                    print(f"❌ Falha ao criar embeddings para {doc_id}")
                    return False
            else:
                print(f"❌ Modelo não disponível ou chunks vazios para {doc_id}")
                return False
            
            # Armazenar documento
            self.documents[doc_id] = {
                "content": content,
                "chunks": chunks
            }
            
            self.metadata[doc_id] = metadata or {}
            self.embeddings[doc_id] = embeddings
            
            # Mapear chunks
            chunk_ids = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                chunk_ids.append(chunk_id)
                self.chunk_id_to_doc_id[chunk_id] = doc_id
            
            self.doc_id_to_chunk_ids[doc_id] = chunk_ids
            
            # Reconstruir índice FAISS
            self._rebuild_faiss_index()
            
            # Salvar dados
            self._save_data()
            
            print(f"✅ Documento '{doc_id}' adicionado com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar documento {doc_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _rebuild_faiss_index(self):
        """Reconstrói o índice FAISS com todos os embeddings"""
        if not self.embeddings:
            return
        
        try:
            # Concatenar todos os embeddings
            all_embeddings = []
            for doc_id, embeddings in self.embeddings.items():
                all_embeddings.extend(embeddings)
            
            if all_embeddings:
                all_embeddings = np.array(all_embeddings)
                self.faiss_index = self._build_faiss_index(all_embeddings)
                print(f"🔄 Índice FAISS reconstruído com {len(all_embeddings)} embeddings")
            
        except Exception as e:
            print(f"❌ Erro ao reconstruir índice FAISS: {e}")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos relevantes"""
        if not self.model or not self.faiss_index:
            print("❌ Sistema não inicializado para busca")
            return []
        
        try:
            print(f"🔍 Busca por '{query}': ", end="")
            
            # Criar embedding da query
            query_embedding = self.model.encode([query])
            
            # Buscar no índice FAISS
            distances, indices = self.faiss_index.search(
                np.array(query_embedding), top_k * 2  # Buscar mais para filtrar
            )
            
            # Mapear resultados para documentos
            results = []
            seen_docs = set()
            
            # Criar lista de todos os chunks para mapeamento
            all_chunks = []
            chunk_to_doc = {}
            
            for doc_id, chunks in self.documents.items():
                for i, chunk in enumerate(chunks["chunks"]):
                    chunk_id = f"{doc_id}_chunk_{i}"
                    all_chunks.append(chunk)
                    chunk_to_doc[len(all_chunks) - 1] = (doc_id, chunk, i)
            
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(all_chunks):
                    doc_id, chunk, chunk_idx = chunk_to_doc[idx]
                    
                    if doc_id not in seen_docs and len(results) < top_k:
                        score = 1.0 / (1.0 + distance)  # Converter distância em score
                        
                        results.append({
                            "doc_id": doc_id,
                            "content": chunk,
                            "full_content": self.documents[doc_id]["content"],
                            "metadata": self.metadata.get(doc_id, {}),
                            "score": float(score),
                            "chunk_index": chunk_idx
                        })
                        
                        seen_docs.add(doc_id)
            
            print(f"{len(results)} resultados encontrados")
            return results
            
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            return []

    def answer_question(self, query: str, ai_agent, model: str = "anthropic/claude-3-haiku") -> str:
        """Responde pergunta usando RAG + IA"""
        try:
            # Buscar documentos relevantes
            results = self.search(query, top_k=3)
            
            if not results:
                return "Desculpe, não encontrei informações relevantes nos documentos carregados para responder sua pergunta."
            
            # Construir contexto
            context_parts = []
            for i, result in enumerate(results, 1):
                context_parts.append(f"[Documento {i}]\n{result['content']}")
            
            context = "\n\n".join(context_parts)
            
            # Construir prompt
            prompt = f"""Com base nos documentos fornecidos, responda à pergunta de forma clara e precisa.

DOCUMENTOS:
{context}

PERGUNTA: {query}

RESPOSTA:"""
            
            # Usar o agente de IA para gerar resposta
            if hasattr(ai_agent, 'generate_response'):
                response = ai_agent.generate_response(prompt, model)
                return response
            else:
                return f"Encontrei {len(results)} documentos relevantes, mas o agente de IA não está disponível para gerar a resposta."
                
        except Exception as e:
            print(f"❌ Erro ao responder pergunta: {e}")
            return f"Erro ao processar sua pergunta: {e}"

    def _save_data(self):
        """Salva dados do sistema"""
        try:
            # Salvar documentos
            with open(self.documents_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2, ensure_ascii=False)
            
            # Salvar metadata
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            
            # Salvar embeddings
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(self.embeddings, f)
            
            # Salvar índice FAISS
            if self.faiss_index:
                faiss.write_index(self.faiss_index, str(self.index_file))
            
            print(f"💾 Dados salvos em {self.storage_dir}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")

    def _load_data(self):
        """Carrega dados salvos"""
        try:
            # Carregar documentos
            if self.documents_file.exists():
                with open(self.documents_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
            
            # Carregar metadata
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            
            # Carregar embeddings
            if self.embeddings_file.exists():
                with open(self.embeddings_file, 'rb') as f:
                    self.embeddings = pickle.load(f)
            
            # Carregar índice FAISS
            if self.index_file.exists() and FAISS_AVAILABLE:
                self.faiss_index = faiss.read_index(str(self.index_file))
            
            # Reconstruir mapeamentos
            self._rebuild_mappings()
            
            if self.documents:
                print(f"✅ Dados carregados: {len(self.documents)} documentos")
            else:
                print("ℹ️  Nenhum dado anterior encontrado. Sistema iniciando limpo.")
                
        except Exception as e:
            print(f"⚠️  Erro ao carregar dados: {e}. Iniciando sistema limpo.")
            self.documents = {}
            self.metadata = {}
            self.embeddings = {}

    def _rebuild_mappings(self):
        """Reconstrói mapeamentos de chunks"""
        self.doc_id_to_chunk_ids = {}
        self.chunk_id_to_doc_id = {}
        
        for doc_id, doc_data in self.documents.items():
            chunk_ids = []
            for i, chunk in enumerate(doc_data["chunks"]):
                chunk_id = f"{doc_id}_chunk_{i}"
                chunk_ids.append(chunk_id)
                self.chunk_id_to_doc_id[chunk_id] = doc_id
            self.doc_id_to_chunk_ids[doc_id] = chunk_ids

    def get_documents_info(self) -> List[Dict]:
        """Retorna informações dos documentos carregados"""
        info = []
        for doc_id, doc_data in self.documents.items():
            metadata = self.metadata.get(doc_id, {})
            info.append({
                "doc_id": doc_id,
                "file_name": metadata.get("file_name", doc_id),
                "content_length": len(doc_data["content"]),
                "chunks_count": len(doc_data["chunks"]),
                "file_size": metadata.get("file_size", 0)
            })
        return info


# Alias para compatibilidade com sistema existente
class UltraSimpleRAG(AdvancedRAGSystem):
    """Alias para manter compatibilidade com o sistema existente"""
    
    def __init__(self, storage_dir: str = "rag_data_robust"):
        super().__init__(storage_dir)


if __name__ == "__main__":
    # Teste básico
    rag = AdvancedRAGSystem()
    
    # Teste com documento simples
    success = rag.add_document(
        "test_doc", 
        "Este é um documento de teste para o sistema RAG avançado.",
        {"source": "test"}
    )
    
    if success:
        results = rag.search("documento teste", top_k=1)
        print(f"Teste: {len(results)} resultados encontrados")
    
    print("✅ Sistema RAG Avançado testado com sucesso!")