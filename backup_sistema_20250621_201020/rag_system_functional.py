#!/usr/bin/env python3
"""
Sistema RAG Híbrido - Avançado + Fallback
Versão: 3.0
Data: 2024-06-21

Sistema RAG que usa PyMuPDF + FAISS + SentenceTransformers quando disponível,
com fallback para sistema TF-IDF básico para garantir compatibilidade.

Características:
- Sistema avançado: PyMuPDF + FAISS + SentenceTransformers
- Sistema fallback: TF-IDF manual + similaridade cosseno
- Persistência automática
- Interface unificada
- Detecção automática de capacidades
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
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
import csv
import urllib.request
import urllib.parse
from io import StringIO, BytesIO
import numpy as np
import markdown

# Tentar importar sistema avançado
try:
    from rag_system_advanced import AdvancedRAGSystem
    ADVANCED_RAG_AVAILABLE = True
    print("✅ Sistema RAG Avançado disponível (PyMuPDF + FAISS + SentenceTransformers)")
except (ImportError, KeyboardInterrupt, Exception) as e:
    ADVANCED_RAG_AVAILABLE = False
    print(f"⚠️  Sistema RAG Avançado não disponível: {type(e).__name__} - usando sistema básico TF-IDF")

# Imports for advanced file processing
try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    from odf import text as odf_text, opendocument
    ODFPY_AVAILABLE = True
except ImportError:
    ODFPY_AVAILABLE = False

class HTMLTextExtractor(HTMLParser):
    """Extrator de texto de HTML usando apenas bibliotecas nativas"""
    def __init__(self):
        super().__init__()
        self.text_content = []
        self.in_script = False
        self.in_style = False
    
    def handle_starttag(self, tag, attrs):
        if tag.lower() in ['script', 'style']:
            if tag.lower() == 'script':
                self.in_script = True
            else:
                self.in_style = True
    
    def handle_endtag(self, tag):
        if tag.lower() == 'script':
            self.in_script = False
        elif tag.lower() == 'style':
            self.in_style = False
    
    def handle_data(self, data):
        if not self.in_script and not self.in_style:
            self.text_content.append(data.strip())
    
    def get_text(self):
        return ' '.join(filter(None, self.text_content))

class UltraSimpleRAG:
    """Sistema RAG Híbrido - usa sistema avançado quando disponível, fallback para TF-IDF."""

    def __init__(self, persist_path: str = "rag_data_robust/rag_db.json"):
        """
        Inicializa o sistema RAG híbrido.
        :param persist_path: Caminho para o arquivo JSON de persistência.
        """
        # Verificar se deve usar sistema avançado
        if ADVANCED_RAG_AVAILABLE:
            try:
                # Usar diretório baseado no persist_path
                storage_dir = Path(persist_path).parent / "advanced"
                self._advanced_system = AdvancedRAGSystem(str(storage_dir))
                self._use_advanced = True
                print(f"✅ Sistema RAG UltraSimpleRAG carregado com sucesso")
                return
            except Exception as e:
                print(f"⚠️  Erro ao inicializar sistema avançado: {e}")
                self._use_advanced = False
        else:
            self._use_advanced = False
        
        # Fallback para sistema básico
        print("🔄 Usando sistema RAG básico (TF-IDF)")
        self.persist_path = Path(persist_path)
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Estruturas de dados principais
        self.documents: Dict[str, Dict[str, Any]] = {}  # {doc_id: {'content': str, 'metadata': {}}}
        self.vocabulary: Dict[str, int] = {}            # {token: doc_count}
        self.vectors: Dict[str, np.ndarray] = {}       # {doc_id: vector}
        self.metadata: Dict[str, Any] = {'created_at': datetime.now().isoformat()}

        self._load_data()

    def _load_data(self):
        """Carrega o estado do sistema RAG a partir do arquivo de persistência."""
        if self.persist_path.exists():
            try:
                with open(self.persist_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.documents = data.get('documents', {})
                self.vocabulary = data.get('vocabulary', {})
                self.metadata = data.get('metadata', self.metadata)
                
                # Desserializar vetores numpy
                vectors_serialized = data.get('vectors', {})
                self.vectors = {doc_id: np.array(vec) for doc_id, vec in vectors_serialized.items()}
                
                print(f"✅ Dados do RAG carregados de {self.persist_path}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Aviso: Não foi possível carregar o banco de dados do RAG. Um novo será criado. Erro: {e}")
        else:
            print("ℹ️  Nenhum banco de dados do RAG encontrado. Um novo será criado.")

    def _save_data(self):
        """Salva o estado atual do sistema RAG no arquivo de persistência."""
        try:
            # Serializar vetores numpy para listas
            vectors_serialized = {}
            for doc_id, vec in self.vectors.items():
                if isinstance(vec, np.ndarray):
                    vectors_serialized[doc_id] = vec.tolist()
                elif isinstance(vec, list):
                    vectors_serialized[doc_id] = vec
                else:
                    # Converter para numpy array primeiro, depois para lista
                    vectors_serialized[doc_id] = np.array(vec).tolist()
            
            data = {
                'documents': self.documents,
                'vocabulary': self.vocabulary,
                'vectors': vectors_serialized,
                'metadata': self.metadata
            }
            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # print(f"✅ Dados do RAG salvos em {self.persist_path}")
        except IOError as e:
            print(f"❌ Erro ao salvar dados do RAG: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado ao salvar dados do RAG: {e}")
    
    def answer_question(self, query: str, ai_agent, model: str = "anthropic/claude-3-haiku") -> str:
        """
        Responde a uma pergunta usando os documentos da base e um modelo de IA.
        :param query: A pergunta do usuário.
        :param ai_agent: A instância do AiAgenteMCP para acessar o modelo de IA.
        :param model: O modelo a ser usado para gerar a resposta.
        :return: A resposta gerada pela IA.
        """
        # Delegar para sistema avançado se disponível
        if hasattr(self, '_use_advanced') and self._use_advanced:
            return self._advanced_system.answer_question(query, ai_agent, model)
        
        # Sistema básico
        if not ai_agent or not ai_agent.openrouter_client:
            return "❌ Erro: O cliente de IA (OpenRouter) não está disponível ou configurado."

        print(f"🔍 Buscando documentos relevantes para a pergunta: '{query}'")
        search_results = self.search(query, top_k=5)

        if not search_results:
            return "ℹ️ Não encontrei informações relevantes nos documentos carregados para responder a esta pergunta."

        # Montar o contexto para a IA
        context = "Com base nos seguintes documentos, responda à pergunta do usuário.\n\n"
        for i, res in enumerate(search_results, 1):
            file_name = res.get('metadata', {}).get('file_name', res['doc_id'])
            context += f"--- Documento {i} (Fonte: {file_name}) ---\n"
            context += res['content']
            context += "\n\n"
        
        # Montar o prompt final
        final_prompt = [
            {
                "role": "system",
                "content": "Você é um assistente especialista em análise de documentos. Sua tarefa é responder às perguntas do usuário com base estritamente nas informações fornecidas nos documentos. Seja claro, conciso e direto. Se a resposta não estiver nos documentos, diga que não encontrou a informação."
            },
            {
                "role": "user",
                "content": f"{context}Pergunta do usuário: {query}"
            }
        ]
        
        print(f"🧠 Enviando prompt para o modelo: {model}")
        try:
            response = ai_agent.openrouter_client.chat_completion(
                messages=final_prompt,
                model=model,
                temperature=0.5
            )

            if response.success:
                print("✅ Resposta recebida com sucesso da IA.")
                return response.content
            else:
                print(f"❌ Erro da API da IA: {response.error_message}")
                return f"❌ Desculpe, ocorreu um erro ao contatar o modelo de IA: {response.error_message}"
        except Exception as e:
            print(f"❌ Exceção ao chamar a IA: {e}")
            return f"❌ Desculpe, ocorreu uma exceção ao processar sua pergunta: {e}"


    def _tokenize(self, text: str) -> List[str]:
        """Tokeniza o texto: minúsculas, remove pontuação e stopwords simples."""
        # Remove caracteres especiais e converte para minúsculas
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Divide em palavras e remove vazias
        tokens = [token.strip() for token in text.split() if token.strip()]
        return tokens
    
    def _build_vocabulary(self):
        """Constrói vocabulário de todos os documentos"""
        all_tokens = set()
        for doc_data in self.documents.values():
            tokens = self._tokenize(doc_data['content'])
            all_tokens.update(tokens)
        
        # Cria mapeamento palavra -> índice
        self.vocabulary = {word: idx for idx, word in enumerate(sorted(all_tokens))}
    
    def _calculate_tf_idf(self, doc_id: str, content: str) -> List[float]:
        """Calcula vetor TF-IDF para um documento"""
        tokens = self._tokenize(content)
        if not tokens:
            return []
        
        # Criar vocabulário único do documento
        doc_vocab = set(tokens)
        
        # Calcular TF-IDF para cada token único
        vector = []
        for token in sorted(doc_vocab):
            # Calcula TF (Term Frequency)
            count = tokens.count(token)
            total_tokens = len(tokens)
            tf = count / total_tokens
            
            # Calcula IDF (Inverse Document Frequency)
            docs_with_term = sum(1 for doc_data in self.documents.values() 
                               if token in self._tokenize(doc_data['content']))
            
            if docs_with_term > 0:
                idf = math.log(len(self.documents) / docs_with_term)
            else:
                idf = 0
            
            # TF-IDF
            tf_idf = tf * idf
            vector.append(tf_idf)
        
        return vector
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similaridade do cosseno entre dois vetores"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        # Converter para numpy arrays se necessário
        if not isinstance(vec1, np.ndarray):
            vec1 = np.array(vec1)
        if not isinstance(vec2, np.ndarray):
            vec2 = np.array(vec2)
        
        # Calcular produto escalar
        dot_product = np.dot(vec1, vec2)
        
        # Calcular normas
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        # Evitar divisão por zero
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def add_document(self, doc_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Adiciona documento ao sistema"""
        # Delegar para sistema avançado se disponível
        if hasattr(self, '_use_advanced') and self._use_advanced:
            return self._advanced_system.add_document(doc_id, content, metadata)
        
        # Sistema básico
        try:
            # Adiciona documento
            self.documents[doc_id] = {
                'content': content,
                'added_at': datetime.now().isoformat(),
                'hash': hashlib.md5(content.encode()).hexdigest()
            }
            
            # Adiciona metadados
            if metadata:
                self.metadata[doc_id] = metadata
            
            # Reconstrói vocabulário
            self._build_vocabulary()
            
            # Recalcula todos os vetores
            self._recalculate_vectors()
            
            # Salva dados
            self._save_data()
            
            print(f"✅ Documento '{doc_id}' adicionado com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar documento: {e}")
            return False
    
    def _recalculate_vectors(self):
        """Recalcula vetores de todos os documentos"""
        self.vectors = {}
        for doc_id, doc_data in self.documents.items():
            tokens = self._tokenize(doc_data['content'])
            self.vectors[doc_id] = self._calculate_tf_idf(doc_id, doc_data['content'])
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos similares à query"""
        # Delegar para sistema avançado se disponível
        if hasattr(self, '_use_advanced') and self._use_advanced:
            return self._advanced_system.search(query, top_k)
        
        # Sistema básico
        if not self.documents:
            return []
        
        # Tokeniza query
        query_tokens = self._tokenize(query)
        
        # Calcula vetor TF-IDF da query
        query_vector = self._calculate_tf_idf(doc_id="query", content=query)
        
        # Calcula similaridades
        similarities = []
        for doc_id, doc_vector in self.vectors.items():
            similarity = self._cosine_similarity(query_vector, doc_vector)
            similarities.append({
                'doc_id': doc_id,
                'similarity': similarity,
                'content': self.documents[doc_id]['content'],
                'metadata': self.metadata.get(doc_id, {})
            })
        
        # Ordena por similaridade
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Retorna top_k resultados
        results = similarities[:top_k]
        
        print(f"🔍 Busca por '{query}': {len(results)} resultados encontrados")
        return results
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """Lista todos os documentos"""
        docs_list = []
        for doc_id, doc_data in self.documents.items():
            docs_list.append({
                'doc_id': doc_id,
                'content_preview': doc_data['content'][:100] + '...' if len(doc_data['content']) > 100 else doc_data['content'],
                'added_at': doc_data['added_at'],
                'metadata': self.metadata.get(doc_id, {})
            })
        return docs_list
    
    def remove_document(self, doc_id: str) -> bool:
        """Remove documento do sistema"""
        try:
            if doc_id not in self.documents:
                print(f"⚠️ Documento '{doc_id}' não encontrado")
                return False
            
            # Remove documento
            del self.documents[doc_id]
            
            # Remove metadados
            if doc_id in self.metadata:
                del self.metadata[doc_id]
            
            # Remove vetor
            if doc_id in self.vectors:
                del self.vectors[doc_id]
            
            # Reconstrói vocabulário e vetores
            if self.documents:  # Se ainda há documentos
                self._build_vocabulary()
                self._recalculate_vectors()
            else:  # Se não há mais documentos
                self.vocabulary = {}
                self.vectors = {}
            
            # Salva dados
            self._save_data()
            
            print(f"✅ Documento '{doc_id}' removido com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao remover documento: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Remove todos os documentos e dados do sistema."""
        try:
            self.documents = {}
            self.vocabulary = {}
            self.vectors = {}
            self.metadata = {}
            self._save_data()
            print("✅ Todos os documentos foram removidos.")
            return True
        except Exception as e:
            print(f"❌ Erro ao limpar todos os documentos: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema"""
        if hasattr(self, '_use_advanced') and self._use_advanced:
            # Usar estatísticas do sistema avançado
            return self._advanced_system.get_stats()
        else:
            # Usar estatísticas do sistema básico
            return {
                'total_documents': len(self.documents),
                'vocabulary_size': len(self.vocabulary),
                'storage_dir': str(self.persist_path.parent),
                'files_exist': {
                    'persist_file': self.persist_path.exists()
                }
            }
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extrai texto de um arquivo com base na sua extensão"""
        file = Path(file_path)
        ext = file.suffix.lower()
        
        try:
            if ext == '.txt':
                return self._extract_from_txt(file)
            elif ext == '.md':
                return self._extract_from_markdown(file)
            elif ext == '.docx':
                return self._extract_from_word(file)
            elif ext == '.xlsx':
                return self._extract_from_excel(file)
            elif ext in ['.odt', '.ods']:
                return self._extract_from_libreoffice(file)
            elif ext == '.html':
                return self._extract_from_html(file)
            elif ext == '.csv':
                return self._extract_from_csv(file)
            elif ext == '.pdf':
                return self._extract_from_pdf(file)
            elif ext in ['.doc', '.xls']:
                print(f"⚠️ Arquivos legados '{ext}' podem não ser lidos corretamente. Salve como '.docx' ou '.xlsx' para melhores resultados.")
                return ""
            else:
                print(f"⚠️ Tipo de arquivo não suportado: {ext}")
                return ""
        except Exception as e:
            print(f"❌ Erro ao extrair texto de {file_path}: {e}")
            return ""
    
    def _extract_from_txt(self, file_path: Path) -> str:
        """Extrai texto de arquivo TXT"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        return ""
    
    def _extract_from_markdown(self, file_path: Path) -> str:
        """Extrai texto de um arquivo Markdown (tratado como texto simples)"""
        return self._extract_from_txt(file_path)
    
    def _extract_from_word(self, file_path: Path) -> str:
        """Extrai texto de arquivos .docx usando python-docx"""
        if not DOCX_AVAILABLE:
            print("⚠️ A biblioteca 'python-docx' não está instalada. Execute 'pip install python-docx'.")
            return ""
        try:
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"❌ Erro ao ler arquivo Word {file_path}: {e}")
            return ""
    
    def _extract_from_excel(self, file_path: Path) -> str:
        """Extrai texto de arquivos .xlsx usando openpyxl"""
        if not OPENPYXL_AVAILABLE:
            print("⚠️ A biblioteca 'openpyxl' não está instalada. Execute 'pip install openpyxl'.")
            return ""
        try:
            workbook = openpyxl.load_workbook(file_path)
            text_content = []
            for sheet in workbook:
                for row in sheet.iter_rows():
                    for cell in row:
                        if cell.value:
                            text_content.append(str(cell.value))
            return "\n".join(text_content)
        except Exception as e:
            print(f"❌ Erro ao ler arquivo Excel {file_path}: {e}")
            return ""
    
    def _extract_from_libreoffice(self, file_path: Path) -> str:
        """Extrai texto de arquivos .odt e .ods usando odfpy"""
        if not ODFPY_AVAILABLE:
            print("⚠️ A biblioteca 'odfpy' não está instalada. Execute 'pip install odfpy'.")
            return ""
        try:
            doc = opendocument.load(file_path)
            all_texts = []
            # Extrai texto de parágrafos
            for element in doc.getElementsByType(odf_text.P):
                all_texts.append(str(element))
            # Extrai texto de tabelas (para .ods)
            # Esta parte pode precisar de mais refinamento dependendo da estrutura do .ods
            return "\n".join(all_texts)
        except Exception as e:
            print(f"❌ Erro ao ler arquivo LibreOffice {file_path}: {e}")
            return ""
    
    def _extract_from_html(self, file_path: Path) -> str:
        """Extrai texto de um arquivo HTML"""
        try:
            html_content = self._extract_from_txt(file_path)
            extractor = HTMLTextExtractor()
            extractor.feed(html_content)
            return extractor.get_text()
        except Exception as e:
            print(f"❌ Erro ao extrair HTML: {e}")
            return ""
    
    def _extract_from_csv(self, file_path: Path) -> str:
        """Extrai texto de arquivo CSV"""
        try:
            content = self._extract_from_txt(file_path)
            csv_reader = csv.reader(StringIO(content))
            all_text = []
            for row in csv_reader:
                all_text.extend(row)
            return ' '.join(filter(None, all_text))
        except Exception as e:
            print(f"❌ Erro ao extrair CSV: {e}")
            return ""
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extrai texto de PDF usando pypdf."""
        if not PYPDF_AVAILABLE:
            print("⚠️ A biblioteca 'pypdf' não está instalada. Execute 'pip install pypdf'.")
            return ""
        try:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            print(f"❌ Erro ao ler arquivo PDF {file_path}: {e}")
            return ""
    
    def add_document_from_file(self, file_path: str, doc_id: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        """
        Adiciona um documento ao sistema a partir de um arquivo local.
        """
        # Delegar para sistema avançado se disponível
        if hasattr(self, '_use_advanced') and self._use_advanced:
            return self._advanced_system.add_document_from_file(file_path)
        
        # Sistema básico
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            print(f"❌ Arquivo não encontrado: {file_path_obj}")
            return False
        
        # Gera ID se não fornecido
        if doc_id is None:
            doc_id = file_path_obj.stem
        
        # Extrai texto do arquivo
        print(f"📄 Extraindo texto de: {file_path_obj.name}")
        content = self._extract_text_from_file(file_path) # Passa o path original como string
        
        if not content.strip():
            print(f"⚠️ Nenhum texto extraído de: {file_path_obj.name}")
            return False
        
        # Adiciona metadados do arquivo
        file_metadata = {
            'file_path': str(file_path_obj),
            'file_name': file_path_obj.name,
            'file_extension': file_path_obj.suffix,
            'file_size': file_path_obj.stat().st_size,
            'extraction_method': 'native_python'
        }
        
        if metadata:
            file_metadata.update(metadata)
        
        # Adiciona documento
        return self.add_document(doc_id, content, file_metadata)
    
    def add_documents_from_directory(self, directory_path: str, recursive: bool = True, 
                                   supported_extensions: Optional[List[str]] = None) -> Dict[str, bool]:
        """Adiciona múltiplos documentos de um diretório"""
        if supported_extensions is None:
            supported_extensions = ['.txt', '.md', '.docx', '.doc', '.xlsx', '.xls', 
                                  '.odt', '.ods', '.odp', '.html', '.htm', '.csv', '.pdf']
        
        dir_path_obj = Path(directory_path)
        if not dir_path_obj.is_dir():
            print(f"❌ Diretório não encontrado: {directory_path}")
            return {}
        
        results = {}
        pattern = '**/*' if recursive else '*'
        
        for file_path in dir_path_obj.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                doc_id = f"{file_path.parent.name}_{file_path.stem}"
                success = self.add_document_from_file(str(file_path), doc_id)
                results[str(file_path)] = success
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        print(f"\n📊 Processamento concluído: {successful}/{total} arquivos adicionados com sucesso")
        
        return results
    
    def add_document_from_url(self, url: str, doc_id: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        """Adiciona documento a partir de URL (HTML)"""
        try:
            print(f"🌐 Baixando conteúdo de: {url}")
            
            # Baixa conteúdo
            with urllib.request.urlopen(url) as response:
                content = response.read()
            
            # Detecta encoding
            encoding = 'utf-8'
            if 'charset=' in str(response.headers):
                charset_match = re.search(r'charset=([^;\s]+)', str(response.headers))
                if charset_match:
                    encoding = charset_match.group(1)
            
            # Decodifica conteúdo
            html_content = content.decode(encoding, errors='ignore')
            
            # Extrai texto
            extractor = HTMLTextExtractor()
            extractor.feed(html_content)
            text_content = extractor.get_text()
            
            if not text_content.strip():
                print(f"⚠️ Nenhum texto extraído da URL: {url}")
                return False
            
            # Gera ID se não fornecido
            if doc_id is None:
                parsed_url = urllib.parse.urlparse(url)
                doc_id = f"web_{parsed_url.netloc}_{parsed_url.path.replace('/', '_')}"
                doc_id = re.sub(r'[^\w\-_]', '_', doc_id)
            
            # Adiciona metadados da URL
            url_metadata = {
                'source_url': url,
                'content_type': 'web_page',
                'extraction_method': 'html_parser'
            }
            
            if metadata:
                url_metadata.update(metadata)
            
            # Adiciona documento
            return self.add_document(doc_id, text_content, url_metadata)
            
        except Exception as e:
            print(f"❌ Erro ao processar URL {url}: {e}")
            return False

# Função de conveniência
def create_rag_system(storage_dir: str = "rag_storage_simple") -> UltraSimpleRAG:
    """Cria uma instância do sistema RAG"""
    return UltraSimpleRAG(storage_dir)

# Demonstração do sistema
def demo_rag_system():
    """Demonstra o funcionamento do sistema RAG"""
    print("🚀 Demonstração do Sistema RAG Ultra-Simplificado")
    print("=" * 50)
    
    # Cria sistema
    rag = create_rag_system("demo_rag")
    
    # Adiciona documentos de exemplo
    docs = [
        ("python_intro", "Python é uma linguagem de programação de alto nível, interpretada e de propósito geral."),
        ("machine_learning", "Machine Learning é um subcampo da inteligência artificial que se concentra no desenvolvimento de algoritmos."),
        ("data_science", "Data Science combina estatística, programação e conhecimento de domínio para extrair insights dos dados."),
        ("web_development", "Desenvolvimento web envolve a criação de sites e aplicações web usando HTML, CSS e JavaScript.")
    ]
    
    print("\n📄 Adicionando documentos...")
    for doc_id, content in docs:
        rag.add_document(doc_id, content, {"category": "tech", "language": "pt"})
    
    # Lista documentos
    print("\n📋 Documentos no sistema:")
    for doc in rag.list_documents():
        print(f"  - {doc['doc_id']}: {doc['content_preview']}")
    
    # Faz buscas
    queries = ["programação", "algoritmos", "dados", "web"]
    
    print("\n🔍 Realizando buscas...")
    for query in queries:
        print(f"\nBusca: '{query}'")
        results = rag.search(query, top_k=2)
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['doc_id']} (similaridade: {result['similarity']:.3f})")
    
    # Estatísticas
    print("\n📊 Estatísticas do sistema:")
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Demonstração concluída!")
    return rag

# Alias para compatibilidade com importações
RAGSystemFunctional = UltraSimpleRAG

if __name__ == "__main__":
    demo_rag_system()
