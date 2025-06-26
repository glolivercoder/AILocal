# 📚 Sistema RAG - Suporte a Múltiplos Formatos de Documentos

## 🎯 Visão Geral

O sistema RAG foi expandido para suportar múltiplos tipos de documentos, permitindo importação e processamento de:

### ✅ Formatos Suportados

| Formato | Extensão | Suporte | Observações |
|---------|----------|---------|-------------|
| **Texto** | `.txt` | ✅ Completo | Múltiplas codificações |
| **Markdown** | `.md` | ✅ Completo | Remove marcações MD |
| **HTML** | `.html`, `.htm` | ✅ Completo | Extrai apenas texto |
| **CSV** | `.csv` | ✅ Completo | Processa todas as células |
| **Word** | `.docx` | ✅ Parcial | Apenas .docx (XML) |
| **Excel** | `.xlsx` | ✅ Parcial | Apenas .xlsx (XML) |
| **LibreOffice** | `.odt`, `.ods`, `.odp` | ✅ Completo | Formatos OpenDocument |
| **PDF** | `.pdf` | ⚠️ Básico | Extração limitada* |

*Para melhor suporte a PDF, instale: `pip install PyPDF2 pdfplumber`

## 🚀 Como Usar

### 1. Importação Básica

```python
from rag_system_functional import UltraSimpleRAG

# Cria sistema RAG
rag = UltraSimpleRAG("meu_rag_storage")

# Adiciona documento individual
success = rag.add_document_from_file(
    "caminho/para/documento.pdf",
    doc_id="meu_documento",
    metadata={"categoria": "manual", "versao": "1.0"}
)
```

### 2. Importação de Diretório

```python
# Importa todos os documentos de um diretório
resultados = rag.add_documents_from_directory(
    "caminho/para/diretorio",
    recursive=True,  # Inclui subdiretórios
    supported_extensions=['.pdf', '.docx', '.txt', '.md']  # Opcional
)

# Verifica resultados
for arquivo, sucesso in resultados.items():
    print(f"{arquivo}: {'✅' if sucesso else '❌'}")
```

### 3. Importação de Páginas Web

```python
# Adiciona página web
success = rag.add_document_from_url(
    "https://example.com/documentacao",
    doc_id="doc_web",
    metadata={"fonte": "web", "tipo": "documentacao"}
)
```

### 4. Busca Unificada

```python
# Busca em todos os documentos independente do formato
resultados = rag.search("desenvolvimento aplicações móveis", top_k=5)

for resultado in resultados:
    print(f"Documento: {resultado['doc_id']}")
    print(f"Similaridade: {resultado['similarity']:.3f}")
    print(f"Tipo: {resultado['metadata'].get('file_extension', 'N/A')}")
    print(f"Preview: {resultado['content'][:100]}...\n")
```

## 🔧 Funcionalidades Avançadas

### Metadados Automáticos

Cada documento importado recebe metadados automáticos:

```python
{
    'file_path': '/caminho/completo/arquivo.pdf',
    'file_name': 'arquivo.pdf',
    'file_extension': '.pdf',
    'file_size': 1024000,
    'extraction_method': 'native_python'
}
```

### Tratamento de Erros

O sistema trata automaticamente:
- Arquivos corrompidos
- Codificações diferentes
- Formatos não suportados
- Arquivos vazios

### Extração Inteligente

#### HTML
- Remove scripts e estilos
- Extrai apenas conteúdo textual
- Preserva estrutura semântica

#### Markdown
- Remove marcações (`#`, `**`, `*`, etc.)
- Preserva links (apenas texto)
- Mantém estrutura de parágrafos

#### Excel/Word
- Processa arquivos XML modernos
- Extrai strings compartilhadas
- Combina múltiplas planilhas/seções

## 📋 Exemplos Práticos

### Exemplo 1: Documentação Técnica

```python
# Importa documentação completa
rag = UltraSimpleRAG("docs_tecnicas")

# Adiciona manuais em PDF
rag.add_document_from_file("manual_api.pdf", "manual_api")

# Adiciona guias em Markdown
rag.add_document_from_file("guia_instalacao.md", "guia_install")

# Adiciona especificações em Word
rag.add_document_from_file("especificacoes.docx", "specs")

# Busca informações
resultados = rag.search("configuração banco dados")
```

### Exemplo 2: Base de Conhecimento

```python
# Importa diretório completo
rag = UltraSimpleRAG("base_conhecimento")

resultados = rag.add_documents_from_directory(
    "documentos/",
    recursive=True
)

print(f"Importados: {sum(resultados.values())} documentos")

# Estatísticas
stats = rag.get_stats()
print(f"Total: {stats['total_documents']} documentos")
print(f"Vocabulário: {stats['vocabulary_size']} palavras")
```

### Exemplo 3: Monitoramento Web

```python
# Monitora páginas web
rag = UltraSimpleRAG("web_content")

urls = [
    "https://docs.python.org/3/",
    "https://reactjs.org/docs/",
    "https://nodejs.org/docs/"
]

for url in urls:
    rag.add_document_from_url(url)

# Busca em conteúdo web
resultados = rag.search("async await promises")
```

## 🛠️ Configuração e Otimização

### Extensões Personalizadas

```python
# Define extensões específicas
extensoes_custom = ['.txt', '.md', '.pdf', '.docx']

resultados = rag.add_documents_from_directory(
    "meus_docs/",
    supported_extensions=extensoes_custom
)
```

### Metadados Personalizados

```python
# Adiciona metadados específicos
metadata_custom = {
    "projeto": "MeuApp",
    "versao": "2.1",
    "autor": "Equipe Dev",
    "categoria": "documentacao",
    "prioridade": "alta"
}

rag.add_document_from_file(
    "especificacoes.pdf",
    "specs_v2",
    metadata_custom
)
```

## 🔍 Busca e Filtros

### Busca por Tipo

```python
# Lista documentos por tipo
docs = rag.list_documents()

pdf_docs = [d for d in docs if d['metadata'].get('file_extension') == '.pdf']
md_docs = [d for d in docs if d['metadata'].get('file_extension') == '.md']

print(f"PDFs: {len(pdf_docs)}")
print(f"Markdowns: {len(md_docs)}")
```

### Busca Avançada

```python
# Busca com contexto
query = "desenvolvimento aplicações móveis React Native"
resultados = rag.search(query, top_k=10)

# Filtra por similaridade
relevantes = [r for r in resultados if r['similarity'] > 0.3]

print(f"Resultados relevantes: {len(relevantes)}")
```

## 📊 Monitoramento e Estatísticas

```python
# Estatísticas detalhadas
stats = rag.get_stats()

print(f"📄 Documentos: {stats['total_documents']}")
print(f"📚 Vocabulário: {stats['vocabulary_size']}")
print(f"💾 Storage: {stats['storage_dir']}")

# Lista todos os documentos
docs = rag.list_documents()
for doc in docs:
    print(f"• {doc['doc_id']}")
    print(f"  Tipo: {doc['metadata'].get('file_extension')}")
    print(f"  Tamanho: {doc['metadata'].get('file_size')} bytes")
    print(f"  Adicionado: {doc['added_at']}")
```

## ⚠️ Limitações e Soluções

### PDF
**Limitação**: Extração básica sem bibliotecas externas
**Solução**: Instalar PyPDF2 ou pdfplumber

```bash
pip install PyPDF2 pdfplumber
```

### Word (.doc)
**Limitação**: Apenas .docx suportado nativamente
**Solução**: Converter .doc para .docx ou usar python-docx

### Excel (.xls)
**Limitação**: Apenas .xlsx suportado nativamente
**Solução**: Converter .xls para .xlsx ou usar xlrd

## 🚀 Próximos Passos

1. **Teste o sistema** com seus documentos
2. **Configure metadados** personalizados
3. **Implemente busca** em sua aplicação
4. **Monitore performance** com estatísticas
5. **Expanda funcionalidades** conforme necessário

## 💡 Dicas de Performance

- Use IDs únicos e descritivos
- Adicione metadados relevantes
- Monitore tamanho do vocabulário
- Faça backup regular dos dados
- Teste diferentes queries de busca

---

**✅ Sistema RAG agora suporta múltiplos formatos com zero dependências externas!**