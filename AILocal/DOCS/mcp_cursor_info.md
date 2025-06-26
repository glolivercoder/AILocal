# Model Control Protocol (MCP) no Cursor

Este documento explica o que é o MCP (Model Control Protocol) no Cursor e como o MCP Manager interage com ele.

## O que é o MCP no Cursor?

O Model Control Protocol (MCP) é uma interface padronizada no Cursor que permite conectar diversos modelos de IA e ferramentas ao editor. Ele funciona como um sistema de plugins, permitindo que o Cursor se comunique com diferentes serviços de IA.

Os MCPs podem ser:
- Modelos de linguagem (LLMs) como Claude, GPT-4, etc.
- Ferramentas especializadas como analisadores de código
- Assistentes de visualização de dados
- Ferramentas de automação de browser (como o Browser Agent)
- E muito mais

## Como o Cursor gerencia MCPs?

O Cursor armazena as configurações de MCP em um arquivo chamado `mcp.json`, tipicamente localizado em:

- Windows: `%APPDATA%\Cursor\mcp.json`
- macOS: `~/Library/Application Support/Cursor/mcp.json`
- Linux: `~/.config/Cursor/mcp.json`

Este arquivo contém um array de objetos MCP, cada um com propriedades como:
- `id`: Identificador único do MCP
- `name`: Nome amigável do MCP
- `origin`: Fonte/provedor do MCP
- `endpoint`: URL do endpoint da API (se aplicável)
- `enabled`: Status de ativação
- `type`: Tipo do MCP (LLM, Tool, Browser, etc.)

## Protocolo de Comunicação

Os MCPs se comunicam com o Cursor através de APIs RESTful, WebSockets ou outros protocolos definidos. Cada MCP implementa uma interface específica que permite:

1. Receber consultas/prompts do Cursor
2. Processar essas consultas usando seu modelo ou ferramenta
3. Retornar resultados formatados para o Cursor

## Browser Agent MCP

O Browser Agent MCP é um exemplo específico que permite ao Cursor controlar um navegador web. Este agente fornece funcionalidades como:

- Navegar para URLs específicas
- Capturar screenshots de páginas web
- Executar JavaScript no contexto da página
- Extrair informações de páginas web

Ele usa o pacote NPM `@agentdeskai/browser-tools-server` e normalmente é executado na porta 3333.

## Como o MCP Manager interage com o sistema MCP do Cursor

O MCP Manager fornece uma interface gráfica para:

1. **Descobrir MCPs**: Localiza automaticamente o arquivo `mcp.json` do Cursor
2. **Gerenciar MCPs**: Permite ativar/desativar MCPs existentes
3. **Configurar novos MCPs**: Adiciona novos MCPs ao arquivo de configuração
4. **Monitorar atividade**: Acompanha o status e as atividades dos MCPs
5. **Interagir com MCPs**: Permite enviar comandos e visualizar respostas

## Formato do MCP no arquivo de configuração

Exemplo de um MCP no arquivo `mcp.json`:

```json
{
  "mcps": [
    {
      "id": "claude-3-opus",
      "name": "Claude 3 Opus",
      "origin": "Anthropic",
      "endpoint": "https://api.anthropic.com/v1",
      "enabled": true,
      "type": "LLM"
    },
    {
      "id": "browser-agent",
      "name": "Browser Agent",
      "origin": "AgentDesk AI",
      "endpoint": "http://localhost:3333",
      "enabled": false,
      "type": "browser"
    }
  ]
}
```

## Estendendo o sistema MCP

Para desenvolvedores que desejam criar seus próprios MCPs:

1. Implemente um servidor que siga o protocolo esperado pelo Cursor
2. Registre seu MCP no arquivo `mcp.json`
3. Defina o endpoint, tipo e outras propriedades necessárias
4. Ative o MCP no Cursor ou através do MCP Manager

## Dicas de Segurança

- Sempre verifique a origem de MCPs de terceiros antes de adicioná-los
- MCPs têm acesso potencial ao conteúdo do seu código
- MCPs com controle de navegador podem ter acesso aos sites que você visita
- Mantenha suas chaves de API seguras e não as compartilhe em MCPs não confiáveis

## Recursos Adicionais

- [Documentação oficial do Cursor](https://cursor.sh/docs)
- [Repositório do Browser Tools Server](https://github.com/agentdesk/browser-tools-server)
- [Comunidade do Cursor no Discord](https://discord.gg/cursor) 