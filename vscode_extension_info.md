# Guia de Desenvolvimento: Extensão VS Code para MCPs do Cursor

## Introdução

Este documento descreve como desenvolver uma extensão para o VS Code que pode gerenciar MCPs (Model Control Protocol) do Cursor. A extensão permitirá que os usuários ativem/desativem MCPs, pesquisem por MCPs de diversas fontes e registrem suas interações com o Cursor.

## Requisitos de Desenvolvimento

Para desenvolver uma extensão VS Code, você precisará de:

1. **Node.js e npm**: Ambiente de execução para JavaScript
2. **TypeScript**: Linguagem recomendada para desenvolvimento de extensões VS Code
3. **VS Code Extension Generator**: Ferramenta para criar a estrutura básica da extensão
4. **API do VS Code**: Para integração com o editor

## Estrutura do Projeto

```
cursor-mcp-manager/
├── .vscode/            # Configurações do VS Code
├── node_modules/       # Dependências
├── src/
│   ├── extension.ts    # Ponto de entrada da extensão
│   ├── mcp-manager.ts  # Lógica para gerenciar MCPs
│   ├── mcp-api.ts      # API para comunicação com fontes de MCPs
│   ├── prompt-logger.ts # Registro de prompts
│   ├── views/          # UI da extensão
│   └── utils/          # Funções utilitárias
├── package.json        # Metadados e dependências
├── tsconfig.json       # Configuração do TypeScript
└── README.md           # Documentação
```

## Passos para Desenvolvimento

### 1. Configuração Inicial

Primeiro, crie o projeto de extensão:

```bash
npm install -g yo generator-code
yo code
```

Escolha "New Extension (TypeScript)" e preencha os campos solicitados.

### 2. Definindo Contribuições da Extensão

No arquivo `package.json`, defina os comandos, visualizações e configurações da extensão:

```json
"contributes": {
  "commands": [
    {
      "command": "cursor-mcp-manager.enable",
      "title": "Habilitar MCP"
    },
    {
      "command": "cursor-mcp-manager.disable",
      "title": "Desabilitar MCP"
    },
    {
      "command": "cursor-mcp-manager.refresh",
      "title": "Atualizar MCPs"
    }
  ],
  "views": {
    "explorer": [
      {
        "id": "mcpExplorer",
        "name": "MCPs Cursor"
      }
    ]
  },
  "configuration": {
    "title": "Cursor MCP Manager",
    "properties": {
      "cursor-mcp-manager.cursorPath": {
        "type": "string",
        "default": "",
        "description": "Caminho para a pasta do Cursor"
      },
      "cursor-mcp-manager.promptsPath": {
        "type": "string",
        "default": "",
        "description": "Caminho para armazenar histórico de prompts"
      }
    }
  }
}
```

### 3. Implementação da Comunicação com o Cursor

Para gerenciar os MCPs, a extensão precisa ler e modificar o arquivo `mcp.json` do Cursor:

```typescript
// src/mcp-manager.ts
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export class MCPManager {
  private mcpJsonPath: string | undefined;

  constructor() {
    this.updateMCPPath();
  }

  public updateMCPPath() {
    const config = vscode.workspace.getConfiguration('cursor-mcp-manager');
    const cursorPath = config.get<string>('cursorPath');
    
    if (cursorPath) {
      this.mcpJsonPath = path.join(cursorPath, 'mcp.json');
    }
  }

  public async getMCPs(): Promise<any[]> {
    if (!this.mcpJsonPath || !fs.existsSync(this.mcpJsonPath)) {
      return [];
    }

    try {
      const mcpContent = fs.readFileSync(this.mcpJsonPath, 'utf-8');
      const mcpData = JSON.parse(mcpContent);
      return mcpData.mcps || [];
    } catch (error) {
      console.error('Erro ao ler MCPs:', error);
      return [];
    }
  }

  public async toggleMCPStatus(mcpId: string, enable: boolean): Promise<boolean> {
    if (!this.mcpJsonPath || !fs.existsSync(this.mcpJsonPath)) {
      return false;
    }

    try {
      const mcpContent = fs.readFileSync(this.mcpJsonPath, 'utf-8');
      const mcpData = JSON.parse(mcpContent);
      
      // Encontrar e atualizar o MCP
      const mcpIndex = mcpData.mcps.findIndex((mcp: any) => mcp.id === mcpId);
      if (mcpIndex >= 0) {
        mcpData.mcps[mcpIndex].enabled = enable;
        
        // Salvar alterações
        fs.writeFileSync(this.mcpJsonPath, JSON.stringify(mcpData, null, 2));
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Erro ao atualizar MCP:', error);
      return false;
    }
  }
}
```

### 4. Implementação do Registro de Prompts

Para registrar as interações do usuário com o Cursor:

```typescript
// src/prompt-logger.ts
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export class PromptLogger {
  private promptsPath: string | undefined;

  constructor() {
    this.updatePromptsPath();
  }

  public updatePromptsPath() {
    const config = vscode.workspace.getConfiguration('cursor-mcp-manager');
    const promptsPath = config.get<string>('promptsPath');
    
    if (promptsPath) {
      this.promptsPath = promptsPath;
      
      // Criar diretório se não existir
      if (!fs.existsSync(this.promptsPath)) {
        fs.mkdirSync(this.promptsPath, { recursive: true });
      }
      
      // Tentar tornar somente-leitura para preservar em commits
      try {
        fs.chmodSync(this.promptsPath, 0o444);
      } catch (error) {
        console.warn('Não foi possível definir pasta como somente-leitura:', error);
      }
    }
  }

  public logPrompt(prompt: string, mcp: string) {
    if (!this.promptsPath) {
      return;
    }

    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      prompt,
      mcp
    };
    
    const filename = `prompt_${timestamp.replace(/[:.]/g, '-')}.json`;
    const filePath = path.join(this.promptsPath, filename);
    
    fs.writeFileSync(filePath, JSON.stringify(logEntry, null, 2));
  }
}
```

### 5. Integração com Fontes de MCPs

Para buscar MCPs de fontes externas como HiMCP.ai, MCP.so, etc.:

```typescript
// src/mcp-api.ts
import * as vscode from 'vscode';
import axios from 'axios';

export interface MCPSource {
  name: string;
  url: string;
  apiKey?: string;
}

export interface MCP {
  id: string;
  name: string;
  description: string;
  source: string;
  type: string;
}

export class MCPApi {
  private sources: MCPSource[] = [
    { name: 'HiMCP.ai', url: 'https://api.himcp.ai/v1/mcps' },
    { name: 'MCP.so', url: 'https://api.mcp.so/mcps' },
    { name: 'Smithery', url: 'https://smithery.com/api/mcps' },
    { name: 'Cursor Directory', url: 'https://cursor.sh/api/mcps' },
    { name: 'PulseMCP', url: 'https://pulsemcp.com/api/mcps' }
  ];

  public async searchMCPs(query: string, source?: string): Promise<MCP[]> {
    const mcps: MCP[] = [];
    
    // Filtrar fontes se especificado
    const sourcesToSearch = source 
      ? this.sources.filter(s => s.name === source)
      : this.sources;
    
    // Buscar de cada fonte
    for (const src of sourcesToSearch) {
      try {
        const response = await axios.get(`${src.url}/search`, {
          params: { q: query },
          headers: src.apiKey ? { 'Authorization': `Bearer ${src.apiKey}` } : {}
        });
        
        if (response.data && Array.isArray(response.data.results)) {
          // Mapear para formato comum
          const sourceMCPs = response.data.results.map((item: any) => ({
            id: item.id,
            name: item.name || item.title,
            description: item.description || '',
            source: src.name,
            type: item.type || 'Unknown'
          }));
          
          mcps.push(...sourceMCPs);
        }
      } catch (error) {
        console.error(`Erro ao buscar MCPs de ${src.name}:`, error);
      }
    }
    
    return mcps;
  }
}
```

### 6. Implementação da UI

A interface do usuário pode ser implementada usando o WebView API do VS Code:

```typescript
// src/views/mcp-panel.ts
import * as vscode from 'vscode';
import { MCPManager } from '../mcp-manager';
import { MCPApi } from '../mcp-api';

export class MCPPanel {
  public static currentPanel: MCPPanel | undefined;
  private readonly panel: vscode.WebviewPanel;
  private readonly extensionUri: vscode.Uri;
  private readonly mcpManager: MCPManager;
  private readonly mcpApi: MCPApi;
  
  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
    this.panel = panel;
    this.extensionUri = extensionUri;
    this.mcpManager = new MCPManager();
    this.mcpApi = new MCPApi();
    
    this.update();
    
    this.panel.onDidDispose(() => {
      MCPPanel.currentPanel = undefined;
    });
    
    this.panel.webview.onDidReceiveMessage(async (message) => {
      switch (message.command) {
        case 'toggleMCP':
          await this.mcpManager.toggleMCPStatus(message.mcpId, message.enable);
          this.update();
          break;
        case 'searchMCPs':
          const mcps = await this.mcpApi.searchMCPs(message.query, message.source);
          this.panel.webview.postMessage({ command: 'searchResults', mcps });
          break;
      }
    });
  }
  
  public static createOrShow(extensionUri: vscode.Uri) {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;
    
    if (MCPPanel.currentPanel) {
      MCPPanel.currentPanel.panel.reveal(column);
      return;
    }
    
    const panel = vscode.window.createWebviewPanel(
      'mcpManager',
      'Cursor MCP Manager',
      column || vscode.ViewColumn.One,
      {
        enableScripts: true,
        localResourceRoots: [extensionUri]
      }
    );
    
    MCPPanel.currentPanel = new MCPPanel(panel, extensionUri);
  }
  
  private async update() {
    const mcps = await this.mcpManager.getMCPs();
    this.panel.webview.html = this.getWebviewContent(mcps);
  }
  
  private getWebviewContent(mcps: any[]) {
    // HTML para interface do usuário...
    return `
      <!DOCTYPE html>
      <html lang="pt">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cursor MCP Manager</title>
        <style>
          /* Estilos CSS omitidos para brevidade */
        </style>
      </head>
      <body>
        <h1>Gerenciador de MCPs do Cursor</h1>
        
        <div class="search-bar">
          <input type="text" id="search-input" placeholder="Buscar MCPs...">
          <select id="source-select">
            <option value="">Todas as fontes</option>
            <option value="HiMCP.ai">HiMCP.ai</option>
            <option value="MCP.so">MCP.so</option>
            <option value="Smithery">Smithery</option>
            <option value="Cursor Directory">Cursor Directory</option>
            <option value="PulseMCP">PulseMCP</option>
          </select>
          <button id="search-button">Buscar</button>
        </div>
        
        <div class="mcp-list">
          ${mcps.map(mcp => `
            <div class="mcp-item ${mcp.enabled ? 'enabled' : 'disabled'}">
              <div class="mcp-info">
                <h3>${mcp.name}</h3>
                <p>${mcp.description || 'Sem descrição'}</p>
                <span class="mcp-source">${mcp.source || 'Desconhecido'}</span>
              </div>
              <label class="switch">
                <input type="checkbox" data-mcp-id="${mcp.id}" ${mcp.enabled ? 'checked' : ''}>
                <span class="slider"></span>
              </label>
            </div>
          `).join('')}
        </div>
        
        <script>
          // JavaScript para interatividade...
          const vscode = acquireVsCodeApi();
          
          document.querySelectorAll('input[data-mcp-id]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
              vscode.postMessage({
                command: 'toggleMCP',
                mcpId: e.target.dataset.mcpId,
                enable: e.target.checked
              });
            });
          });
          
          document.getElementById('search-button').addEventListener('click', () => {
            const query = document.getElementById('search-input').value;
            const source = document.getElementById('source-select').value;
            
            vscode.postMessage({
              command: 'searchMCPs',
              query,
              source
            });
          });
          
          window.addEventListener('message', event => {
            const message = event.data;
            if (message.command === 'searchResults') {
              // Código para exibir resultados da pesquisa
            }
          });
        </script>
      </body>
      </html>
    `;
  }
}
```

## Como Publicar a Extensão

1. **Empacotamento**:
   ```bash
   npm install -g vsce
   vsce package
   ```

2. **Publicação no VS Code Marketplace**:
   ```bash
   vsce publish
   ```

## Considerações Finais

### Desafios de Implementação

1. **Integração com o Cursor**: Como o Cursor é um aplicativo separado do VS Code, a comunicação depende do arquivo `mcp.json` e possivelmente de comunicação entre processos.

2. **APIs não documentadas**: Algumas fontes de MCPs podem não ter APIs públicas, exigindo web scraping.

3. **Permissões de arquivo**: Tornar uma pasta somente leitura pode exigir permissões de administrador.

### Possibilidades Futuras

1. **Sincronização em nuvem**: Permitir compartilhar configurações de MCPs entre diferentes computadores.

2. **Análise de prompts**: Ferramentas para analisar padrões de uso e eficácia de diferentes MCPs.

3. **Recomendações de MCPs**: Sugerir MCPs com base no contexto do projeto atual.

---

Este guia fornece uma base para o desenvolvimento de uma extensão VS Code para gerenciar MCPs do Cursor. A implementação real dependerá das APIs disponíveis e das permissões do sistema. 