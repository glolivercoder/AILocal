#!/usr/bin/env python3
"""
Sistema RAG Ultra-Simplificado - Funcional com Zero Dependências Externas
Versão: 2.0
Data: 2024-06-21

Este sistema implementa um RAG (Retrieval-Augmented Generation) completo
usando apenas bibliotecas nativas do Python, sem dependências externas.

Características:
- TF-IDF manual para embeddings
- Similaridade por cosseno
- Persistência automática em JSON/Pickle
- Interface simples e intuitiva
- Zero configuração necessária
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
            
            # Carrega metadados
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                    
        except Exception as e:
            print(f"⚠️ Erro ao carregar dados: {e}")
    
    def _save_data(self):
        """Salva dados no disco"""
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
            
            # Salva metadados
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokeniza texto simples"""
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
    
    def _calculate_tf_idf(self, tokens: List[str]) -> List[float]:
        """Calcula vetor TF-IDF para uma lista de tokens"""
        if not self.vocabulary:
            return []
        
        # Inicializa vetor com zeros
        vector = [0.0] * len(self.vocabulary)
        
        # Calcula TF (Term Frequency)
        token_counts = Counter(tokens)
        total_tokens = len(tokens)
        
        for token, count in token_counts.items():
            if token in self.vocabulary:
                tf = count / total_tokens
                
                # Calcula IDF (Inverse Document Frequency)
                docs_with_term = sum(1 for doc_data in self.documents.values() 
                                   if token in self._tokenize(doc_data['content']))
                
                if docs_with_term > 0:
                    idf = math.log(len(self.documents) / docs_with_term)
                    
                    # TF-IDF
                    tf_idf = tf * idf
                    vector[self.vocabulary[token]] = tf_idf
        
        return vector
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similaridade de cosseno entre dois vetores"""
        if len(vec1) != len(vec2):
            return 0.0
        
        # Produto escalar
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Normas
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(a * a for a in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def add_document(self, doc_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Adiciona documento ao sistema"""
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
            self.vectors[doc_id] = self._calculate_tf_idf(tokens)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos similares à query"""
        if not self.documents:
            return []
        
        # Tokeniza query
        query_tokens = self._tokenize(query)
        
        # Calcula vetor TF-IDF da query
        query_vector = self._calculate_tf_idf(query_tokens)
        
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
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema"""
        return {
            'total_documents': len(self.documents),
            'vocabulary_size': len(self.vocabulary),
            'storage_dir': str(self.storage_dir),
            'files_exist': {
                'documents': self.documents_file.exists(),
                'vocabulary': self.vocabulary_file.exists(),
                'vectors': self.vectors_file.exists(),
                'metadata': self.metadata_file.exists()
            }
        }
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extrai texto de diferentes tipos de arquivo"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        try:
            if extension == '.txt':
                return self._extract_from_txt(file_path)
            elif extension == '.md':
                return self._extract_from_markdown(file_path)
            elif extension in ['.docx', '.doc']:
                return self._extract_from_word(file_path)
            elif extension in ['.xlsx', '.xls']:
                return self._extract_from_excel(file_path)
            elif extension in ['.odt', '.ods', '.odp']:
                return self._extract_from_libreoffice(file_path)
            elif extension in ['.html', '.htm']:
                return self._extract_from_html(file_path)
            elif extension == '.csv':
                return self._extract_from_csv(file_path)
            elif extension == '.pdf':
                return self._extract_from_pdf_simple(file_path)
            else:
                # Tenta ler como texto simples
                return self._extract_from_txt(file_path)
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
        """Extrai texto de arquivo Markdown"""
        content = self._extract_from_txt(file_path)
        # Remove marcações básicas do Markdown
        content = re.sub(r'#{1,6}\s+', '', content)  # Headers
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*(.*?)\*', r'\1', content)  # Italic
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)  # Links
        content = re.sub(r'`([^`]+)`', r'\1', content)  # Code
        return content
    
    def _extract_from_word(self, file_path: Path) -> str:
        """Extrai texto de documento Word (.docx)"""
        try:
            if file_path.suffix.lower() == '.docx':
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    # Lê o documento principal
                    doc_xml = zip_file.read('word/document.xml')
                    root = ET.fromstring(doc_xml)
                    
                    # Extrai texto de todos os elementos de texto
                    text_elements = []
                    for elem in root.iter():
                        if elem.text:
                            text_elements.append(elem.text)
                    
                    return ' '.join(text_elements)
            else:
                # Para .doc, tenta ler como texto (limitado)
                print(f"⚠️ Formato .doc não totalmente suportado. Tentando extração básica...")
                return self._extract_from_txt(file_path)
        except Exception as e:
            print(f"❌ Erro ao extrair Word: {e}")
            return ""
    
    def _extract_from_excel(self, file_path: Path) -> str:
        """Extrai texto de planilha Excel (.xlsx)"""
        try:
            if file_path.suffix.lower() == '.xlsx':
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    # Lê strings compartilhadas
                    shared_strings = []
                    try:
                        strings_xml = zip_file.read('xl/sharedStrings.xml')
                        strings_root = ET.fromstring(strings_xml)
                        for si in strings_root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                            text_parts = []
                            for t in si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'):
                                if t.text:
                                    text_parts.append(t.text)
                            shared_strings.append(''.join(text_parts))
                    except:
                        pass
                    
                    # Lê dados das planilhas
                    all_text = []
                    try:
                        # Lista arquivos de planilha
                        sheet_files = [f for f in zip_file.namelist() if f.startswith('xl/worksheets/sheet')]
                        
                        for sheet_file in sheet_files:
                            sheet_xml = zip_file.read(sheet_file)
                            sheet_root = ET.fromstring(sheet_xml)
                            
                            for cell in sheet_root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                                cell_type = cell.get('t')
                                value_elem = cell.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                                
                                if value_elem is not None and value_elem.text:
                                    if cell_type == 's':  # String compartilhada
                                        try:
                                            idx = int(value_elem.text)
                                            if idx < len(shared_strings):
                                                all_text.append(shared_strings[idx])
                                        except:
                                            pass
                                    else:  # Valor direto
                                        all_text.append(value_elem.text)
                    except:
                        pass
                    
                    return ' '.join(all_text)
            else:
                print(f"⚠️ Formato .xls não totalmente suportado.")
                return ""
        except Exception as e:
            print(f"❌ Erro ao extrair Excel: {e}")
            return ""
    
    def _extract_from_libreoffice(self, file_path: Path) -> str:
        """Extrai texto de documentos LibreOffice (.odt, .ods, .odp)"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Lê o conteúdo principal
                content_xml = zip_file.read('content.xml')
                root = ET.fromstring(content_xml)
                
                # Extrai texto de todos os elementos
                text_elements = []
                for elem in root.iter():
                    if elem.text and elem.text.strip():
                        text_elements.append(elem.text.strip())
                
                return ' '.join(text_elements)
        except Exception as e:
            print(f"❌ Erro ao extrair LibreOffice: {e}")
            return ""
    
    def _extract_from_html(self, file_path: Path) -> str:
        """Extrai texto de arquivo HTML"""
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
    
    def _extract_from_pdf_simple(self, file_path: Path) -> str:
        """Extração básica de PDF (limitada sem bibliotecas externas)"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                
            # Busca por streams de texto (muito básico)
            text_parts = []
            content_str = content.decode('latin-1', errors='ignore')
            
            # Procura por padrões de texto em PDF
            import re
            # Busca texto entre parênteses (formato básico de PDF)
            text_matches = re.findall(r'\(([^\)]+)\)', content_str)
            text_parts.extend(text_matches)
            
            # Busca texto em formato de string
            string_matches = re.findall(r'/Title\s*\(([^\)]+)\)', content_str)
            text_parts.extend(string_matches)
            
            extracted_text = ' '.join(text_parts)
            
            if not extracted_text.strip():
                print(f"⚠️ PDF {file_path.name}: Extração limitada. Para melhor suporte a PDF, instale PyPDF2 ou pdfplumber.")
                return f"Documento PDF: {file_path.name} (extração de texto limitada)"
            
            return extracted_text
            
        except Exception as e:
            print(f"❌ Erro ao extrair PDF: {e}")
            print(f"💡 Dica: Para melhor suporte a PDF, instale: pip install PyPDF2")
            return f"Documento PDF: {file_path.name} (erro na extração)"
    
    def add_document_from_file(self, file_path: str, doc_id: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        """Adiciona documento a partir de arquivo"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ Arquivo não encontrado: {file_path}")
            return False
        
        # Gera ID se não fornecido
        if doc_id is None:
            doc_id = file_path.stem
        
        # Extrai texto do arquivo
        print(f"📄 Extraindo texto de: {file_path.name}")
        content = self._extract_text_from_file(str(file_path))
        
        if not content.strip():
            print(f"⚠️ Nenhum texto extraído de: {file_path.name}")
            return False
        
        # Adiciona metadados do arquivo
        file_metadata = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_extension': file_path.suffix,
            'file_size': file_path.stat().st_size,
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
        
        directory_path = Path(directory_path)
        if not directory_path.exists():
            print(f"❌ Diretório não encontrado: {directory_path}")
            return {}
        
        results = {}
        pattern = '**/*' if recursive else '*'
        
        for file_path in directory_path.glob(pattern):
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
