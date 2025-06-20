# Guia de Instalação - Simple Agent-S

## O que é o Simple Agent-S

Uma versão simplificada do Agent-S framework, compatível com Python 3.12.10, que oferece:
- **Automação de desktop** baseada em visão computacional
- **Integração com Claude** para análise de screenshots
- **Compatibilidade total** com Python 3.12.10
- **Fácil configuração** e uso

## Instalação

### 1. Pré-requisitos
- Python 3.12.10 (já instalado)
- Chave de API da Anthropic
- PyAutoGUI (instalado automaticamente)

### 2. Configuração
1. Obtenha uma chave de API da Anthropic
2. Execute o script de exemplo
3. Digite sua chave de API quando solicitado

### 3. Uso
```bash
python scripts/simple_agent_s_example.py
```

## Exemplos de automação

### Básicos
- "Abra o Notepad"
- "Digite 'Hello World' no Notepad"
- "Salve o arquivo como 'test.txt'"
- "Feche o Notepad"

### Avançados
- "Abra o Paint e desenhe um círculo"
- "Abra o Chrome e vá para google.com"
- "Abra o Excel e crie uma planilha"

## Recursos

### Automações suportadas
- **Navegação de interface** - cliques, digitação
- **Manipulação de arquivos** - abrir, salvar, fechar
- **Controle de aplicativos** - iniciar, parar
- **Automação web** - navegação básica

### Segurança
- **FAILSAFE habilitado** - mova o mouse para o canto superior esquerdo para parar
- **Pausa entre ações** - 0.5 segundos por padrão
- **Execução segura** - código validado antes da execução

## Troubleshooting

### Problemas comuns
- **Erro de API**: Verifique sua chave da Anthropic
- **Erro de screenshot**: Verifique permissões de tela
- **Erro de automação**: Verifique se o elemento está visível

### Logs
- Verifique a saída do console
- Use print() para debug
- Verifique se PyAutoGUI está funcionando

## Arquivos criados

```
config/
└── simple_agent_s_config.json  # Configuração do agente

scripts/
└── simple_agent_s_example.py   # Script de exemplo

agent_s_alternative.py          # Módulo principal
```

## Próximos passos

1. **Configure sua API key** da Anthropic
2. **Teste com exemplos simples** primeiro
3. **Experimente automações mais complexas**
4. **Integre com outros sistemas** se necessário

## Suporte

Para problemas:
1. Verifique os logs do console
2. Teste com exemplos básicos
3. Verifique sua conexão com a internet
4. Confirme que sua API key está correta
