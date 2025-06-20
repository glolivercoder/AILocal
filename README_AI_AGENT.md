# AiAgenteMCP - Sistema Completo de IA com RAG e Gerenciamento de MCPs

## 🚀 Visão Geral

O AiAgenteMCP é um sistema completo de inteligência artificial que integra:
- **Agente MCP Inteligente** com múltiplos modelos via OpenRouter
- **Sistema RAG** para processamento e busca em documentos PDF
- **Gerenciamento de MCPs** para Cursor com instalação e controle de sessões
- **Integração Ollama** com modelos otimizados para Ryzen 5600
- **Interface Gráfica** intuitiva para configuração e uso

## 📋 Funcionalidades

### 🤖 Agente MCP
- Integração com OpenRouter (modelos free e premium)
- Múltiplos modos de operação (assistente, desenvolvedor, analista, criativo)
- Cache de respostas para otimização
- Histórico de conversas persistente
- Configuração flexível de parâmetros

### 📚 Sistema RAG
- Processamento de PDFs com PyPDF2
- Indexação vetorial com FAISS
- Busca semântica com sentence-transformers
- Gerenciamento de documentos (upload, remoção, busca)
- Contexto aprimorado para respostas do agente

### 🔧 Gerenciamento de MCPs
- **Instalação automática** de MCPs via npm
- **Controle de sessões** (iniciar/parar MCPs)
- **Análise inteligente** de prompts para carregar MCPs necessários
- **Integração com Cursor** (atualização automática do mcp.json)
- **MCPs disponíveis**:
  - Browser Tools (navegação web)
  - File System (sistema de arquivos)
  - Git Tools (controle de versão)
  - SQLite/PostgreSQL (bancos de dados)
  - Ollama (modelos locais)
  - Puppeteer (automação web)
  - Brave Search (busca na web)

### 🦙 Integração Ollama
- **Modelos otimizados** para Ryzen 5600 (CPU only)
- **Instalação/remoção** de modelos via interface
- **Modelos recomendados**:
  - `llama3.2:3b` (1.8GB) - Rápido e eficiente
  - `llama3.2:7b` (4.1GB) - Equilibrado
  - `codellama:7b` (4.1GB) - Especializado em código
  - `mistral:7b` (4.1GB) - Versátil e eficiente
  - `microsoft/phi-3-mini` (1.8GB) - Muito rápido
  - `qwen2.5:7b` (4.1GB) - Multilingue

### 🖥️ Interface Gráfica
- Configuração da API OpenRouter
- Upload e gerenciamento de PDFs
- Busca semântica em documentos
- Gerenciamento completo de MCPs
- Configuração de modelos Ollama
- Chat interativo com o agente
- Status e monitoramento em tempo real

## 🛠️ Instalação

### 1. Pré-requisitos
- Python 3.8+
- pip
- Node.js (para MCPs)
- Ollama (opcional, para modelos locais)

### 2. Instalar Dependências
```bash
pip install -r requirements_mcp.txt
```

### 3. Instalar Ollama (Opcional)
```bash
# Windows
winget install Ollama.Ollama

# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

### 4. Executar o Sistema
```bash
python run_ai_agent.py
```

## 📖 Como Usar

### 1. Configuração da API OpenRouter

1. **Obter API Key**: Acesse [OpenRouter](https://openrouter.ai) e crie uma conta
2. **Configurar**: Na aba "Configuração API":
   - Cole sua API key no campo "API Key"
   - Selecione o modelo padrão
   - Ajuste parâmetros (max tokens, temperature)
   - Clique em "Salvar Configuração"
   - Teste a conexão com "Testar Conexão"

### 2. Gerenciamento de MCPs

1. **Instalar MCPs**: Na aba "Gerenciamento MCPs":
   - Selecione o MCP desejado na lista
   - Clique em "Instalar Selecionado"
   - Aguarde a instalação via npm

2. **Controlar Sessões**:
   - **Iniciar**: Selecione MCP e clique "Iniciar Selecionado"
   - **Parar**: Selecione MCP e clique "Parar Selecionado"
   - **Status**: Visualize status em tempo real (verde=rodando, vermelho=parado)

3. **Análise Inteligente**:
   - Digite seu prompt no campo "Análise de Prompt"
   - Clique "Analisar e Gerenciar MCPs"
   - Sistema automaticamente inicia/para MCPs necessários

### 3. Configuração Ollama

1. **Verificar Status**: Status do Ollama é mostrado automaticamente
2. **Instalar Modelos**:
   - Selecione modelo recomendado na lista
   - Clique "Instalar Modelo"
   - Aguarde download (pode demorar dependendo do tamanho)
3. **Remover Modelos**: Selecione e clique "Remover Modelo"

### 4. Sistema RAG - Upload de PDFs

1. **Upload**: Na aba "Sistema RAG":
   - Clique em "Selecionar PDF"
   - Escolha o arquivo PDF
   - Aguarde o processamento (extração de texto + embeddings)

2. **Gerenciar**: 
   - Visualize documentos processados na lista
   - Remova documentos específicos
   - Limpe todos os documentos se necessário

3. **Buscar**:
   - Digite sua pergunta no campo "Query"
   - Ajuste o número de resultados
   - Clique em "Buscar"
   - Visualize resultados com scores de relevância

### 5. Chat com o Agente

1. **Testar**: Na aba "Teste do Agente":
   - Verifique o status do agente
   - Digite mensagens no chat
   - Receba respostas aprimoradas com contexto dos PDFs

## 🔧 Configuração Avançada

### Modelos Disponíveis

#### Modelos Free (OpenRouter)
- `google/gemini-1.5-flash`
- `meta-llama/llama-3-8b-instruct`
- `microsoft/phi-3-mini`
- `nousresearch/nous-hermes-2-mixtral-8x7b-dpo`
- `openchat/openchat-3.5`
- `qwen/qwen2.5-7b-instruct`
- `snowflake/snowflake-arctic-instruct`

#### Modelos Premium
- `anthropic/claude-3-opus`
- `anthropic/claude-3-sonnet`
- `anthropic/claude-3-haiku`
- `google/gemini-pro`
- `google/gemini-1.5-pro`
- `mistralai/mistral-large`
- `openai/gpt-4-turbo`
- `openai/gpt-4o`
- `deepseek/deepseek-coder`

### Parâmetros de Configuração

- **Max Tokens**: Limite de tokens por resposta (100-8192)
- **Temperature**: Criatividade das respostas (0-100%)
- **Cache TTL**: Tempo de vida do cache (em segundos)
- **Top K**: Número de resultados da busca semântica

## 📁 Estrutura de Arquivos

```
AILocal/
├── ai_agente_mcp.py          # Agente principal
├── rag_system.py             # Sistema RAG
├── mcp_manager.py            # Gerenciador de MCPs
├── ai_agent_gui.py           # Interface gráfica
├── run_ai_agent.py           # Script de inicialização
├── requirements_mcp.txt      # Dependências
├── MCPAGENTMODE.md           # Documentação do agente
├── config/                   # Configurações
│   └── agent_config.json
├── rag_data/                 # Dados do sistema RAG
│   ├── faiss_index.idx
│   ├── documents.pkl
│   └── metadata.pkl
└── logs/                     # Logs do sistema
    └── ai_agent_mcp.log
```

## 🔍 Exemplos de Uso

### 1. Configuração Rápida
```python
# Configurar API key
agent = AiAgenteMCP()
agent.update_config("openrouter_api_key", "sua_api_key_aqui")

# Processar PDF
rag = RAGSystem()
rag.add_document("documento.pdf")

# Buscar contexto
context = rag.get_context_for_query("sua pergunta aqui")
```

### 2. Gerenciamento de MCPs
```python
# Inicializar gerenciador
manager = MCPManager()

# Analisar prompt e gerenciar MCPs
prompt = "Preciso navegar na web e ler um arquivo"
results = manager.auto_manage_mcps(prompt)

# Instalar MCP específico
manager.install_mcp("browser-tools")
manager.start_mcp("browser-tools")
```

### 3. Chat com Contexto RAG
```python
# Obter contexto relevante
context = rag_system.get_context_for_query(user_question)

# Enviar para o agente com contexto
message = f"Contexto: {context}\n\nPergunta: {user_question}"
response = agent.process_message(message)
```

## 🚨 Troubleshooting

### Problemas Comuns

1. **Erro de API Key**
   - Verifique se a API key está correta
   - Teste a conexão na interface
   - Verifique se tem créditos na OpenRouter

2. **Erro no Upload de PDF**
   - Verifique se o arquivo não está corrompido
   - Tente com um PDF menor
   - Verifique permissões de escrita

3. **Erro de Dependências**
   - Execute: `pip install -r requirements_mcp.txt`
   - Verifique versão do Python (3.8+)
   - Reinstale dependências se necessário

4. **MCPs não iniciam**
   - Verifique se Node.js está instalado
   - Execute: `npm install -g @modelcontextprotocol/server-filesystem`
   - Verifique se as portas não estão em uso

5. **Ollama não funciona**
   - Verifique se Ollama está instalado e rodando
   - Execute: `ollama serve` em terminal separado
   - Verifique se tem espaço suficiente para modelos

6. **Interface não abre**
   - Verifique se PyQt5 está instalado
   - Execute: `python run_ai_agent.py`
   - Verifique logs em `logs/ai_agent_mcp.log`

### Logs e Debug

- Logs principais: `logs/ai_agent_mcp.log`
- Configuração: `config/agent_config.json`
- Dados RAG: `rag_data/`
- Configuração Cursor: `~/.config/Cursor/User/mcp.json`

## 🔄 Atualizações

### Atualizar Dependências
```bash
pip install --upgrade -r requirements_mcp.txt
```

### Atualizar MCPs
```bash
npm update -g @modelcontextprotocol/server-*
```

### Backup de Configuração
```bash
cp config/agent_config.json config/backup_config.json
```

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs em `logs/ai_agent_mcp.log`
2. Teste com configurações básicas
3. Verifique a documentação em `MCPAGENTMODE.md`
4. Consulte a seção de troubleshooting

## 🎯 Próximos Passos

- [ ] Integração com mais formatos de documento (DOCX, TXT)
- [ ] Interface web para acesso remoto
- [ ] Sistema de plugins para extensões
- [ ] Análise de sentimentos e classificação
- [ ] Exportação de conversas e relatórios
- [ ] Suporte a mais modelos Ollama
- [ ] Integração com outros editores (VS Code, etc.)

---

**Desenvolvido com ❤️ para facilitar o uso de IA no dia a dia** 