import os
import re
from pathlib import Path
import sqlite3
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleRAGSystem:
    """
    Um sistema RAG simplificado que usa SQLite para armazenamento e busca textual.
    Não depende de embeddings, vetores ou bibliotecas pesadas.
    """
    def __init__(self, db_path="rag_data_simple/documents.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
        logger.info("Sistema RAG Simples inicializado.")

    def _init_db(self):
        """Inicializa o banco de dados SQLite."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id INTEGER PRIMARY KEY,
                        path TEXT UNIQUE NOT NULL,
                        content TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Erro ao inicializar o banco de dados: {e}")
            raise

    def add_document(self, file_path):
        """
        Adiciona um documento ao banco de dados. Suporta PDF, TXT, MD.
        Extrai texto e o armazena.
        """
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "message": f"Arquivo não encontrado: {file_path}"}

        # Verificar se o documento já existe
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM documents WHERE path = ?", (str(path),))
            if cursor.fetchone():
                return {"success": True, "skipped": True, "message": f"Documento já existe: {path.name}"}

        try:
            content = self._extract_text(path)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO documents (path, content) VALUES (?, ?)", (str(path), content))
                conn.commit()
            logger.info(f"Documento '{path.name}' adicionado com sucesso.")
            return {"success": True, "message": f"Documento '{path.name}' adicionado."}
        except Exception as e:
            logger.error(f"Falha ao adicionar o documento '{path.name}': {e}")
            return {"success": False, "message": f"Falha ao processar '{path.name}': {e}"}

    def _extract_text(self, path):
        """Extrai texto de um arquivo com base na sua extensão."""
        ext = path.suffix.lower()
        content = ""
        try:
            if ext == '.pdf':
                try:
                    import PyPDF2
                    with open(path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            content += page.extract_text() or ""
                except ImportError:
                    return "PyPDF2 não está instalado. Não é possível ler PDFs."
            elif ext in ['.txt', '.md']:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                return f"Formato de arquivo não suportado: {ext}"
        except Exception as e:
            raise IOError(f"Não foi possível ler o arquivo {path.name}: {e}")
        
        # Normalização básica do texto
        content = re.sub(r'\s+', ' ', content).strip()
        return content

    def search(self, query, context_window=2):
        """
        Busca por uma query no conteúdo dos documentos usando busca textual.
        Retorna trechos relevantes.
        """
        results = []
        query_words = set(query.lower().split())

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT path, content FROM documents")
                for path, content in cursor.fetchall():
                    if query.lower() in content.lower():
                        sentences = re.split(r'(?<=[.!?])\s+', content)
                        for i, sentence in enumerate(sentences):
                            if query.lower() in sentence.lower():
                                start = max(0, i - context_window)
                                end = min(len(sentences), i + context_window + 1)
                                context = " ".join(sentences[start:end])
                                results.append({
                                    "path": path,
                                    "context": context.strip(),
                                    "relevance": "Direct Match"
                                })
                                # Pular para o próximo arquivo após encontrar o primeiro match
                                break 
        except sqlite3.Error as e:
            logger.error(f"Erro durante a busca no banco de dados: {e}")
        
        return results

    def get_document_list(self):
        """Retorna a lista de todos os documentos no banco de dados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT path, timestamp FROM documents ORDER BY timestamp DESC")
                return [{"path": row[0], "timestamp": row[1]} for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Erro ao obter a lista de documentos: {e}")
            return []

    def clear_all_data(self):
        """Apaga todos os documentos do banco de dados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM documents")
                conn.commit()
            logger.info("Todos os documentos foram removidos da base de dados.")
            return {"success": True, "message": "Base de dados limpa com sucesso."}
        except sqlite3.Error as e:
            logger.error(f"Erro ao limpar a base de dados: {e}")
            return {"success": False, "message": f"Erro de banco de dados: {e}"}

if __name__ == '__main__':
    # Teste de uso
    print("Testando o SimpleRAGSystem...")
    rag = SimpleRAGSystem()
    
    # Criar um arquivo de teste
    test_dir = Path("rag_test_docs")
    test_dir.mkdir(exist_ok=True)
    test_file = test_dir / "test.txt"
    with open(test_file, "w") as f:
        f.write("Esta é a primeira frase. O sistema RAG simples é uma ferramenta de busca textual. A terceira frase contém a palavra-chave.")
    
    # Adicionar e buscar
    print(rag.add_document(str(test_file)))
    results = rag.search("busca textual")
    print("\nResultados da busca por 'busca textual':")
    print(results)
    
    # Limpar
    print("\nLimpando a base de dados...")
    print(rag.clear_all_data())
    print("\nLista de documentos após limpeza:")
    print(rag.get_document_list())

    # Remover arquivo de teste
    os.remove(test_file)
    os.rmdir(test_dir)
    print("\nTeste concluído.") 