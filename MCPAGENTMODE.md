# MCP Agent Mode - Configuração e Documentação

## Visão Geral
Este arquivo define o modo de operação do agente MCP (Model Control Protocol) para o sistema AILocal, incluindo configurações de modelos, APIs e funcionalidades avançadas.

## Configurações de Modelos

### OpenRouter Models (Free e Premium)
```json
{
  "openrouter_models": {
    "free": [
      "google/gemini-1.5-flash",
      "meta-llama/llama-3-8b-instruct",
      "microsoft/phi-3-mini",
      "nousresearch/nous-hermes-2-mixtral-8x7b-dpo",
      "openchat/openchat-3.5",
      "qwen/qwen2.5-7b-instruct",
      "snowflake/snowflake-arctic-instruct"
    ],
    "premium": [
      "anthropic/claude-3-opus",
      "anthropic/claude-3-sonnet", 
      "anthropic/claude-3-haiku",
      "google/gemini-pro",
      "google/gemini-1.5-pro",
      "mistralai/mistral-large",
      "mistralai/mistral-medium",
      "meta-llama/llama-3-70b-instruct",
      "openai/gpt-4-turbo",
      "openai/gpt-4o",
      "openai/gpt-3.5-turbo",
      "deepseek/deepseek-coder",
      "cohere/command-r-plus"
    ]
  }
}
```

### Configurações de API
```json
{
  "api_configs": {
    "openrouter": {
      "base_url": "https://openrouter.ai/api/v1",
      "default_model": "anthropic/claude-3-opus",
      "timeout": 30,
      "max_tokens": 4096,
      "temperature": 0.7
    },
    "gemini": {
      "base_url": "https://generativelanguage.googleapis.com",
      "default_model": "gemini-pro",
      "timeout": 30,
      "max_tokens": 8192,
      "temperature": 0.7
    },
    "claude": {
      "base_url": "https://api.anthropic.com",
      "default_model": "claude-3-opus-20240229",
      "timeout": 30,
      "max_tokens": 4096,
      "temperature": 0.7
    }
  }
}
```

## Funcionalidades do Agente

### 1. Modo de Operação
- **Assistente Inteligente**: Responde perguntas e executa tarefas
- **Desenvolvedor**: Gera código, debuga e otimiza
- **Analista**: Analisa dados e gera relatórios
- **Criativo**: Gera conteúdo criativo e artístico

### 2. Recursos Avançados
- **Multimodal**: Processa texto, imagem, áudio e vídeo
- **Contexto Persistente**: Mantém conversas e contexto entre sessões
- **Execução de Código**: Executa scripts Python, JavaScript, etc.
- **Integração Web**: Acessa APIs e navega na web
- **Síntese de Voz**: Converte texto em fala
- **Reconhecimento de Voz**: Converte fala em texto

### 3. Capacidades de MCP
- **Browser Tools**: Navegação web e automação
- **File System**: Manipulação de arquivos e diretórios
- **Terminal**: Execução de comandos do sistema
- **Database**: Conexão e consulta a bancos de dados
- **Git**: Controle de versão e gerenciamento de repositórios

## Configurações de Ambiente

### Variáveis de Ambiente
```bash
# OpenRouter
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Gemini
GOOGLE_API_KEY=your_google_api_key_here

# Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Configurações Gerais
AGENT_MODE=assistant
DEFAULT_MODEL=anthropic/claude-3-opus
VOICE_ENABLED=true
BROWSER_AGENT_ENABLED=true
```

### Configurações de Performance
```json
{
  "performance": {
    "max_concurrent_requests": 5,
    "request_timeout": 30,
    "retry_attempts": 3,
    "cache_enabled": true,
    "cache_ttl": 3600,
    "memory_limit": "2GB",
    "cpu_limit": "50%"
  }
}
```

## Instruções de Uso

### 1. Inicialização
```python
from mcp_manager_prototype import MCPManagerApp

app = MCPManagerApp()
app.show()
```

### 2. Configuração de APIs
1. Configure as chaves de API no arquivo `.env`
2. Selecione o modelo padrão na interface
3. Teste a conexão com cada API

### 3. Ativação de Recursos
- **Voz**: Ative o reconhecimento e síntese de voz
- **Browser**: Inicie o agente de navegador
- **MCPs**: Ative os MCPs desejados

### 4. Modos de Interação
- **Chat**: Conversa natural com o agente
- **Comandos**: Comandos específicos para tarefas
- **Voz**: Interação por voz
- **Interface**: Interface gráfica completa

## Troubleshooting

### Problemas Comuns
1. **API Key Inválida**: Verifique as chaves no arquivo `.env`
2. **Timeout**: Aumente o timeout nas configurações
3. **Erro de Conexão**: Verifique a conectividade de internet
4. **MCP não Inicia**: Verifique as dependências e permissões

### Logs e Debug
- Logs são salvos em `logs/agent.log`
- Debug mode pode ser ativado via variável de ambiente
- Relatórios de erro são gerados automaticamente

## Atualizações e Manutenção

### Atualização de Modelos
- Novos modelos são adicionados automaticamente
- Configurações são mantidas entre atualizações
- Backup automático das configurações

### Backup e Restauração
- Configurações são salvas em `config/backup/`
- Restauração automática em caso de erro
- Exportação manual de configurações

## Segurança

### Boas Práticas
- Nunca compartilhe chaves de API
- Use variáveis de ambiente para credenciais
- Mantenha o sistema atualizado
- Monitore logs de acesso

### Permissões
- Acesso limitado ao sistema de arquivos
- Execução de comandos com confirmação
- Logs de todas as ações do agente 