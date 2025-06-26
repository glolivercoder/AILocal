# 🧠 Sistema Integrado de Aprimoramento de Conhecimento

## 🎯 Visão Geral

Sistema completo de aprimoramento de conhecimento que integra:
- **LangChain** para processamento de linguagem natural
- **TensorFlow** para análise de dados e machine learning
- **Docker** para containerização e gerenciamento
- **N8N** para automação de workflows
- **MCPs** para integração com ferramentas externas
- **Suporte a múltiplos formatos** (Microsoft Office, LibreOffice, E-books)

---

## 🚀 Funcionalidades Principais

### 📚 Processamento de Documentos
- **Microsoft Office**: DOCX, XLSX, PPTX, DOC, XLS, PPT
- **LibreOffice**: ODT, ODS, ODP
- **E-books**: EPUB, MOBI (Kindle)
- **Outros**: PDF, TXT, MD, CSV
- **Processamento automático** em background
- **Extração inteligente** de conteúdo

### 🧠 Análise Inteligente
- **LangChain** para processamento de linguagem natural
- **TensorFlow** para análise de dados
- **Clustering** automático de documentos
- **Análise de sentimento** em tempo real
- **Embeddings** para busca semântica

### 🐳 Gerenciamento Docker
- **Interface gráfica** para containers
- **Start/Stop** automático de serviços
- **Monitoramento** de recursos
- **Execução** de imagens personalizadas
- **Integração** com N8N

### 🔄 Automação N8N
- **Criação** de workflows via interface
- **Webhooks** automáticos
- **Integração** com MCPs
- **Execução** de pipelines de dados
- **Monitoramento** de execuções

### 🔌 Integração MCP
- **Arquitetura de dados** com MCPs
- **Webhooks** inteligentes
- **Processamento** de conhecimento
- **Automação** de tarefas
- **Integração** com editores

---

## 📦 Instalação

### 1. **Dependências do Sistema**
```bash
# Instalar Python 3.8+
python --version

# Instalar Docker
docker --version

# Instalar N8N (opcional)
npm install -g n8n
```

### 2. **Dependências Python**
```bash
# Instalar dependências principais
pip install -r requirements_knowledge_system.txt

# Ou instalar individualmente
pip install langchain tensorflow PyQt5 docker requests
```

### 3. **Configuração Inicial**
```bash
# Criar diretórios necessários
mkdir -p config vectorstore knowledge_base

# Configurar variáveis de ambiente
cp env.example .env
# Editar .env com suas configurações
```

---

## 🎮 Como Usar

### 1. **Interface Gráfica Principal**
```bash
python integrated_knowledge_interface.py
```

### 2. **Sistema de Conhecimento**
```bash
python knowledge_enhancement_system.py
```

### 3. **Interface Docker/N8N**
```bash
python docker_n8n_interface.py
```

---

## 📋 Componentes do Sistema

### 🧠 Knowledge Enhancement System
```python
from knowledge_enhancement_system import KnowledgeEnhancementSystem

# Criar sistema
system = KnowledgeEnhancementSystem()

# Adicionar documento
system.add_document("documento.pdf")

# Consultar conhecimento
result = system.query_knowledge("O que é inteligência artificial?")

# Analisar documentos
analysis = system.analyze_documents(n_clusters=5)
```

### 🐳 Docker Manager
```python
from docker_n8n_interface import DockerManager

# Gerenciar containers
docker = DockerManager()
containers = docker.get_containers()
docker.start_container("container_id")
```

### 🔄 N8N Manager
```python
from docker_n8n_interface import N8NManager

# Gerenciar workflows
n8n = N8NManager("http://localhost:5678", "token")
workflows = n8n.get_workflows()
n8n.create_workflow(workflow_data)
```

### 🔌 MCP Integration
```python
from docker_n8n_interface import MCPIntegration

# Criar workflows MCP
mcp = MCPIntegration()
webhook_workflow = mcp.create_webhook_workflow("url", data)
data_workflow = mcp.create_data_architecture_workflow("source", "target")
```

---

## 🎯 Casos de Uso

### 1. **Processamento de Documentos Empresariais**
```
1. Upload de documentos (PDF, Word, Excel)
2. Processamento automático com LangChain
3. Análise de conteúdo com TensorFlow
4. Criação de workflows N8N para automação
5. Integração com sistemas via MCPs
```

### 2. **Análise de Conhecimento**
```
1. Carregamento de base de conhecimento
2. Clustering automático de documentos
3. Análise de sentimento
4. Geração de insights
5. Criação de relatórios automatizados
```

### 3. **Automação de Workflows**
```
1. Criação de webhooks N8N
2. Integração com Docker containers
3. Processamento de dados com MCPs
4. Execução de pipelines automatizados
5. Monitoramento de performance
```

### 4. **Arquitetura de Dados**
```
1. Conexão com bancos de dados via MCPs
2. Transformação de dados com TensorFlow
3. Armazenamento em vectorstores
4. Busca semântica com LangChain
5. Visualização de resultados
```

---

## ⚙️ Configuração

### 1. **Configuração do Sistema**
```json
{
  "openai_api_key": "sua_chave_aqui",
  "model_name": "gpt-3.5-turbo",
  "vectorstore_path": "vectorstore",
  "max_documents": 1000,
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "enable_tensorflow": true,
  "enable_langchain": true
}
```

### 2. **Configuração N8N**
```json
{
  "n8n_url": "http://localhost:5678",
  "n8n_token": "seu_token_aqui",
  "webhook_path": "/webhook",
  "auto_activate": true
}
```

### 3. **Configuração Docker**
```json
{
  "docker_socket": "/var/run/docker.sock",
  "auto_refresh": true,
  "refresh_interval": 30,
  "max_containers": 50
}
```

---

## 🔧 Arquitetura Técnica

### 📊 Diagrama de Componentes
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Interface     │    │   Sistema de    │    │   Docker &      │
│   Gráfica       │◄──►│   Conhecimento  │◄──►│   N8N           │
│   (PyQt5)       │    │   (LangChain)   │    │   Manager       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Processador   │    │   TensorFlow    │    │   MCP           │
│   de Documentos │    │   Analyzer      │    │   Integration   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔄 Fluxo de Dados
```
1. Upload de Documento
   ↓
2. Processamento com DocumentProcessor
   ↓
3. Análise com TensorFlowAnalyzer
   ↓
4. Indexação com LangChainEnhancer
   ↓
5. Armazenamento em VectorStore
   ↓
6. Consulta e Resposta
```

---

## 📈 Métricas e Performance

### 🚀 Performance Esperada
- **Processamento de documentos**: 10-50 docs/min
- **Análise de sentimento**: 1000 textos/min
- **Clustering**: 1000 docs em 30s
- **Consulta de conhecimento**: < 2s
- **Inicialização do sistema**: < 10s

### 📊 Recursos Utilizados
- **CPU**: 20-80% (dependendo da carga)
- **RAM**: 2-8 GB (baseado no tamanho da base)
- **Disco**: 1-10 GB (vectorstore + documentos)
- **Rede**: Baixo (apenas para APIs externas)

---

## 🛠️ Desenvolvimento

### 1. **Estrutura do Projeto**
```
sistema_conhecimento/
├── knowledge_enhancement_system.py    # Sistema principal
├── docker_n8n_interface.py           # Interface Docker/N8N
├── integrated_knowledge_interface.py  # Interface integrada
├── requirements_knowledge_system.txt  # Dependências
├── config/                           # Configurações
├── vectorstore/                      # Base de conhecimento
├── knowledge_base/                   # Documentos processados
└── logs/                            # Logs do sistema
```

### 2. **Extensibilidade**
```python
# Adicionar novo processador de documentos
class CustomDocumentProcessor:
    def process_document(self, file_path):
        # Implementar processamento customizado
        pass

# Adicionar novo analisador
class CustomAnalyzer:
    def analyze_data(self, data):
        # Implementar análise customizada
        pass
```

### 3. **Testes**
```bash
# Executar testes unitários
python -m pytest tests/

# Executar testes de integração
python test_integration.py

# Executar testes de performance
python test_performance.py
```

---

## 🔒 Segurança

### 1. **Autenticação**
- **API Keys** para serviços externos
- **Tokens** para N8N
- **Credenciais** criptografadas

### 2. **Dados**
- **Processamento local** por padrão
- **Criptografia** de dados sensíveis
- **Backup** automático de configurações

### 3. **Acesso**
- **Controle de permissões** por usuário
- **Logs** de auditoria
- **Validação** de entrada

---

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. **LangChain não carrega**
```bash
# Solução
pip install --upgrade langchain
pip install sentence-transformers
```

#### 2. **TensorFlow não funciona**
```bash
# Solução
pip install tensorflow-cpu  # Para CPU
pip install tensorflow-gpu  # Para GPU
```

#### 3. **Docker não conecta**
```bash
# Solução
sudo usermod -aG docker $USER
sudo systemctl start docker
```

#### 4. **N8N não responde**
```bash
# Solução
n8n start
# Verificar porta 5678
```

---

## 📞 Suporte

### 📧 Contato
- **Email**: suporte@sistema-conhecimento.com
- **Documentação**: [docs.sistema-conhecimento.com](https://docs.sistema-conhecimento.com)
- **Issues**: [GitHub Issues](https://github.com/sistema-conhecimento/issues)

### 📚 Recursos Adicionais
- **Tutorial**: [tutorial.md](tutorial.md)
- **API Reference**: [api_reference.md](api_reference.md)
- **Examples**: [examples/](examples/)

---

## 🎯 Roadmap

### ✅ Implementado
- [x] Sistema de processamento de documentos
- [x] Integração LangChain
- [x] Análise TensorFlow
- [x] Interface Docker
- [x] Interface N8N
- [x] Integração MCPs

### 🔄 Em Desenvolvimento
- [ ] Interface web (React)
- [ ] Machine Learning avançado
- [ ] Integração com mais MCPs
- [ ] Sistema de plugins

### 📋 Planejado
- [ ] API REST completa
- [ ] Sistema de usuários
- [ ] Backup automático
- [ ] Monitoramento avançado
- [ ] Integração com cloud

---

**🎉 Sistema Integrado de Conhecimento - Potencializando a Inteligência Artificial!** 