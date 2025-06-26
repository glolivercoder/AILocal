# Guia de Instalação - Stata MCP

## O que foi instalado

✅ Extensão Stata MCP clonada do repositório
✅ Dependências Python instaladas
✅ Configuração MCP criada
✅ Integração com Cursor configurada

## Próximos passos

### 1. Instalar Stata
- Baixe e instale Stata 17+ (MP, SE ou BE)
- Certifique-se de que o Stata está no PATH do sistema

### 2. Configurar Cursor
1. Abra o Cursor
2. Vá para Configurações (Ctrl+,)
3. Procure por "MCP" ou "Model Context Protocol"
4. Adicione a configuração do arquivo: config/stata_mcp_config.json

### 3. Testar integração
1. Abra um arquivo .do no Cursor
2. A extensão deve aparecer na barra de status
3. Use Ctrl+Shift+P e digite "Stata" para ver comandos

### 4. Configuração avançada
Para configurar edição específica do Stata:
```json
{
  "stata-vscode.stataEdition": "MP"
}
```

## Troubleshooting

### Problemas comuns:
- **Extensão não carrega**: Verifique Python 3.11+
- **Stata não encontrado**: Verifique instalação e PATH
- **Erro de conexão**: Verifique se porta 4000 está livre

### Logs:
- VS Code: View > Output > Stata MCP
- Cursor: Help > Toggle Developer Tools > Console

## Recursos

- [Repositório original](https://github.com/hanlulong/stata-mcp.git)
- [Documentação oficial](https://github.com/hanlulong/stata-mcp#readme)
- [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=deepecon.stata-mcp)

## Suporte

Para problemas específicos:
1. Verifique os logs do editor
2. Consulte a documentação oficial
3. Abra uma issue no repositório GitHub
