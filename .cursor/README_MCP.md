# Cursor Control MCP Server

## Funcionalidades Instaladas

### 🖥️ Controle de Terminal
- `execute_terminal_command`: Executa comandos no terminal
- `create_terminal_session`: Cria sessões persistentes de terminal
- `list_terminal_sessions`: Lista sessões ativas

### 💬 Gerenciamento de Prompts
- `save_prompt`: Salva prompts para reutilização
- `search_prompts`: Busca prompts por categoria/tags
- `use_prompt`: Usa prompts salvos com substituição de variáveis

### 🤖 Controle de Conversas
- `start_conversation`: Inicia nova conversa com IA
- `send_message_to_cursor`: Envia mensagens para IA do Cursor
- `get_conversation_history`: Recupera histórico de conversas

### 📁 Controle do Editor
- `open_file_in_cursor`: Abre arquivos no Cursor
- `create_file_in_cursor`: Cria novos arquivos
- `execute_cursor_command`: Executa comandos do Cursor

### ⚙️ Configuração e Status
- `get_cursor_status`: Obtém status do Cursor e MCPs
- `configure_cursor_mcp`: Configura novos MCPs
- `backup_cursor_config`: Faz backup das configurações

## Como Usar

### 1. Comandos de Terminal
```
Prompt: "Execute o comando 'python --version' no terminal"
Prompt: "Crie uma sessão de terminal chamada 'dev' no diretório src/"
```

### 2. Gerenciamento de Prompts
```
Prompt: "Salve este prompt: 'Analise o código em {file_path}' na categoria 'code-review'"
Prompt: "Busque prompts relacionados a 'documentação'"
Prompt: "Use o prompt de análise de código para o arquivo main.py"
```

### 3. Controle de Conversas
```
Prompt: "Inicie uma conversa sobre 'Refatoração do módulo auth'"
Prompt: "Envie mensagem para o Cursor: 'Como melhorar a performance desta função?'"
```

### 4. Controle do Editor
```
Prompt: "Abra o arquivo src/main.py na linha 45"
Prompt: "Crie um novo arquivo config.py com configurações básicas"
```

## Arquivos Criados

- `.cursor/mcp.json`: Configuração MCP do workspace
- `.cursor/conversations.db`: Banco de conversas
- `.cursor/prompts.db`: Banco de prompts
- `.cursor/examples/`: Exemplos de uso
- `.cursor/backups/`: Backups automáticos

## Próximos Passos

1. Reinicie o Cursor para carregar o servidor MCP
2. Teste com: "Qual é o status do Cursor e MCPs?"
3. Explore os exemplos em `.cursor/examples/`
4. Configure prompts personalizados para seu workflow
