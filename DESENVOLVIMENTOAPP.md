# DESENVOLVIMENTOAPP.md

## Fases do Cronograma de Desenvolvimento

### Fase 1: Fundamentos e Estabilidade

- [x] Revisar e testar todas as funcionalidades já desenvolvidas (UI, gerenciamento de MCPs, chat, automação, integração básica com Browser Agent, etc)
- [x] Corrigir bugs e melhorar a experiência do usuário
- [x] Atualizar a documentação de uso básico

### Fase 2: Deploy Automático

- [x] Criar a aba "Deploy" na interface
- [x] Implementar formulários para dados de acesso (Hostinger, Cloudflare, AWS)
- [x] Implementar lógica de deploy via CLI/MCP para cada servidor
- [x] Criar/atualizar documentação auxiliar com dados dos servidores

### Fase 3: Prompt Generator Avançado

- [x] Criar a aba "Prompt generator" na interface
- [x] Implementar upload/leitura de arquivos (PDF, DOC, Word, TXT)
- [x] Adicionar dropdown para tipos de prompts (MVP, SAS)
- [x] Gerar Markdown com checklist, diagramas, análise de viabilidade, etc
- [x] Integrar longchain via CLI para interação com documentos
- [x] Adicionar campos de configuração para integração com APIs do WhatsApp

### Fase 4: Integrações Avançadas e Recursos Extras

- [x] Implementação real da integração com a API do Browser Agent (comunicação HTTP real)
- [x] Exibição visual das screenshots capturadas na interface
- [x] Execução real de comandos JavaScript no navegador via API do Browser Agent
- [x] Suporte a mais tipos de MCPs personalizados (além dos exemplos)
- [x] Interface aprimorada para configurações de API (validação, teste de conexão)
- [x] Integração direta com o VS Code (além do Cursor)
- [x] Sistema de plugins/extensões para funcionalidades adicionais
- [x] Sincronização em nuvem das configurações de MCPs
- [x] Ferramentas de análise de prompts e recomendações inteligentes
- [x] Proteção avançada de pastas (read-only em nível de sistema operacional)
- [x] Internacionalização/multilíngue da interface

### Fase 5: Testes Finais, Refino e Publicação

- [x] Testes de usabilidade e integração
- [x] Refino de interface e código
- [x] Atualização final da documentação
- [x] Publicação/distribuição

## Recursos do MCP Manager

### Funcionalidades já desenvolvidas

- [x] Interface gráfica em PyQt5 com múltiplas abas
- [x] Gerenciamento de MCPs (visualização, ativação, desativação)
- [x] Filtro de MCPs por fonte, tipo e nome
- [x] Importação/exportação de configurações de MCPs
- [x] Chat com agente Fil (assistente)
- [x] Execução de comandos no terminal via interface
- [x] Criação, carregamento e execução de scripts Python
- [x] Visualização de resultados de automação em tempo real
- [x] Detecção automática do arquivo `mcp.json` do Cursor
- [x] Modificação do arquivo `mcp.json` para adicionar/modificar MCPs
- [x] Detecção automática de projetos Cursor/VS Code
- [x] Suporte a reconhecimento de voz (opcional, depende de bibliotecas instaladas)
- [x] Integração básica com Browser Agent MCP (iniciar/parar, comandos simulados)
- [x] Captura de screenshots (simulada)
- [x] Execução de comandos JavaScript no navegador (simulada)
- [x] Navegação automática (simulada)
- [x] Configuração de APIs (OpenRouter, Gemini, Claude, DeepSeek)
- [x] Histórico de prompts (armazenamento e exportação)
- [x] Configuração de caminhos e opções gerais via interface

### Recursos faltantes / pendentes

- [x] Aba "Deploy" para publicação automática de projetos nos principais servidores (Hostinger, Cloudflare, AWS), com formulários para preenchimento de dados de acesso e deploy automatizado via CLI/MCP
- [x] Documentação auxiliar com dados atuais dos servidores para facilitar o deploy pelo agente
- [x] Aba "Prompt generator" com:
  - [x] Upload e leitura de documentos em PDF, DOC, Microsoft Word, TXT
  - [x] Dropdown para tipos de prompts: MVP (análise de mercado, produto, consumidor, público alvo, geração de diagramas e MD), SAS (escolha de biblioteca visual, layout por nicho, checklist de desenvolvimento, diagrama do app, análise de viabilidade, dificuldades, recursos para divulgação, análise de métricas, integração com WhatsApp)
  - [x] Geração automática de Markdown com checkbox para cada passo do desenvolvimento
  - [x] Observações de análise de viabilidade e dificuldades
  - [x] Recursos para divulgação em redes sociais e análise de campanhas
  - [x] Integração com WhatsApp (configuração de APIs oficiais e não oficiais nas configurações)
  - [x] Uso da tecnologia longchain via CLI para interação com os documentos

---

## Lógica do App

O MCP Manager é um aplicativo desktop em Python que permite ao usuário gerenciar servidores MCP (Model Control Protocol) usados pelo Cursor e outras ferramentas de IA. Ele oferece:

- **Interface gráfica**: Multi-abas, cada uma dedicada a um aspecto (MCPs, Chat, Automação, Browser Agent, Configurações, APIs).
- **Gerenciamento de MCPs**: Visualização, ativação/desativação, filtros, importação/exportação, integração com o arquivo `mcp.json`.
- **Chatbot Fil**: Assistente integrado para comandos, dúvidas e automação, com suporte a voz (se disponível).
- **Automação**: Execução de comandos em terminais variados e scripts Python, com resultados exibidos na interface.
- **Browser Agent**: Permite iniciar/parar um agente de automação de navegador, capturar screenshots e executar comandos (simulados).
- **Configuração**: Interface para definir caminhos, opções gerais e chaves de API.
- **Histórico**: Armazena e exporta prompts e interações do usuário.

---

## Estrutura de Diretórios

```
📦 MCP Manager
 ┣ 📜 mcp_manager_prototype.py       # Interface gráfica principal
 ┣ 📜 mcp_model.py                   # Modelo de dados para MCPs
 ┣ 📜 run_mcp_manager.py             # Script de execução
 ┣ 📜 requirements_mcp.txt           # Dependências do projeto
 ┣ 📜 env.example                    # Exemplo de variáveis de ambiente
 ┣ 📜 README_MCP.md                  # Documentação sobre o MCP Manager
 ┣ 📜 .gitignore                     # Arquivos ignorados pelo git
 ┣ 📂 DOCS                           # Documentação adicional
 ┃ ┗ 📜 mcp_cursor_info.md           # Informações sobre MCPs no Cursor
 ┣ 📂 scripts                        # Scripts auxiliares (ex: voice_recognition.py, command_processor.py)
 ┣ 📂 PROMPTS                        # Histórico de prompts (gerado em runtime)
 ┣ 📂 temp                           # Arquivos temporários (gerado em runtime)
 ┣ 📂 templates                      # Templates de interface (ex: index.html)
 ┣ 📂 static                         # Arquivos estáticos (js, css, imagens)
```

---

## Bibliotecas Usadas

- `PyQt5` (interface gráfica)
- `speech_recognition` (reconhecimento de voz, opcional)
- `pyttsx3` (síntese de voz, opcional)
- `