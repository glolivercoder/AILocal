# Projeto MCP Manager

Este repositório contém um gerenciador de MCPs (Model Control Protocol) para o Cursor, uma ferramenta de desenvolvimento com IA. O projeto consiste em uma interface gráfica desenvolvida em PyQt5 que permite gerenciar MCPs de várias fontes, incluindo um agente de automação de browser.

## Estrutura do Projeto

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
 ┣ 📂 scripts                        # Scripts auxiliares (opcional)
 ┣ 📂 PROMPTS                        # Histórico de prompts (gerado em runtime)
 ┗ 📂 temp                           # Arquivos temporários (gerado em runtime)
```

## Componentes Principais

### 1. Interface Gráfica (`mcp_manager_prototype.py`)

A interface principal do projeto, desenvolvida em PyQt5, contendo:
- Janela principal com múltiplas abas
- Gerenciamento de MCPs (visualização, ativação, desativação)
- Chat com agente Fil
- Configuração de APIs
- Automação via terminal e scripts Python
- Integração com Browser Agent

### 2. Modelo de Dados (`mcp_model.py`)

Classes que representam os MCPs e fornecem funcionalidades para:
- Representar MCPs genéricos e específicos (como o Browser Agent)
- Gerenciar conjuntos de MCPs
- Carregar/salvar MCPs do/para o arquivo mcp.json do Cursor
- Importar/exportar configurações

### 3. Script de Execução (`run_mcp_manager.py`)

Script para iniciar o aplicativo com validação de dependências e configurações, responsável por:
- Verificar dependências instaladas
- Criar ícones necessários
- Verificar instalação do Cursor
- Iniciar a interface gráfica

## Funcionalidades Principais

### Gerenciamento de MCPs

- Visualização de MCPs disponíveis
- Filtro por fonte, tipo e nome
- Ativação/desativação de MCPs
- Importação/exportação de configurações

### Chatbot Fil

- Interface de chat com o agente Fil
- Processamento de comandos
- Suporte a reconhecimento de voz (opcional)
- Execução de comandos no terminal e scripts

### Browser Agent MCP

- Iniciar/parar o Browser Agent
- Capturar screenshots
- Executar JavaScript no navegador
- Navegação automática

### Automação

- Execução de comandos em diferentes terminais
- Criação e execução de scripts Python
- Visualização de resultados em tempo real

### Integração com Cursor

- Detecção automática do arquivo mcp.json
- Modificação do arquivo mcp.json para adicionar/modificar MCPs
- Detecção automática de projetos Cursor/VS Code

## Requisitos

- Python 3.7+
- PyQt5
- speech_recognition e pyttsx3 (opcionais, para recursos de voz)
- Node.js (opcional, para o Browser Agent)

## Instalação

1. Clone o repositório
2. Instale as dependências com `pip install -r requirements_mcp.txt`
3. Execute o aplicativo com `python run_mcp_manager.py`

## Configuração

As configurações podem ser definidas através do arquivo `.env` (use `env.example` como modelo):

```
# Caminhos
CURSOR_PATH=/caminho/para/o/cursor
HISTORY_PATH=/caminho/para/salvar/historico

# Opções
AUTO_START=false
READ_ONLY_HISTORY=false
AUTO_BACKUP=true
VOICE_ENABLED=true

# Chaves de API (deixe em branco se não for usar)
OPENROUTER_API_KEY=
GEMINI_API_KEY=
CLAUDE_API_KEY=
DEEPSEEK_API_KEY=

# Configurações de navegador
BROWSER_AGENT_PORT=3333

# Configurações avançadas
DEBUG=false
LOG_LEVEL=INFO
```

## Documentação

Para mais informações sobre MCPs no Cursor, consulte o arquivo `DOCS/mcp_cursor_info.md`.

## Notas sobre as Funcionalidades de Voz

Para usar os recursos de reconhecimento de voz, você precisa ter as seguintes bibliotecas instaladas:
- speech_recognition
- pyttsx3
- pyaudio (pode exigir instalação manual)

Se essas bibliotecas não estiverem disponíveis, o aplicativo ainda funcionará, mas sem os recursos de voz.

## Desenvolvimento Futuro

Possíveis melhorias futuras incluem:
- Implementação completa da integração com a API do Browser Agent
- Suporte a mais tipos de MCPs personalizados
- Interface melhorada para configurações de API
- Integração com o VS Code (além do Cursor)
- Sistema de plugins para extensão de funcionalidades

## Licença

Este projeto está licenciado sob a Licença MIT. 