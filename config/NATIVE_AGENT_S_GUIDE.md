# Guia de Instalação - Native Agent-S

## O que é o Native Agent-S

Uma versão nativa do Agent-S que usa capacidades nativas de IA para automação de desktop:
- **Sem dependência de APIs externas** - funciona offline
- **Análise inteligente de instruções** - entende comandos em português
- **Detecção automática de elementos** - encontra botões, textos, etc.
- **Execução segura** - validação e controle de ações

## Vantagens

### ✅ Sem API Keys
- Não precisa de chaves da Anthropic, OpenAI, etc.
- Funciona completamente offline
- Sem custos de API

### ✅ Análise Nativa
- Usa capacidades nativas de IA
- Entende contexto e intenções
- Gera planos de ação inteligentes

## Instalação

### 1. Pré-requisitos
- Python 3.12.10 (já instalado)
- PyAutoGUI (instalado automaticamente)

### 2. Uso
```bash
python scripts/native_agent_s_example.py
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

## Como funciona

### 1. Análise de Instrução
O sistema analisa a instrução em português e identifica:
- Ações a serem executadas
- Aplicativos a serem abertos
- Textos a serem digitados
- Elementos a serem clicados

### 2. Geração de Plano
Cria um plano de ações sequenciais:
- Abrir aplicativos
- Navegar pela interface
- Executar comandos
- Salvar resultados

### 3. Execução Segura
Executa cada ação com:
- Validação de segurança
- Pausas entre ações
- Tratamento de erros
- Feedback em tempo real

## Recursos

### Automações suportadas
- **Abertura de aplicativos** - Notepad, Paint, Chrome, etc.
- **Digitação de texto** - com suporte a caracteres especiais
- **Navegação de interface** - cliques, menus, botões
- **Manipulação de arquivos** - salvar, fechar, etc.

### Segurança
- **FAILSAFE habilitado** - mova o mouse para parar
- **Pausa entre ações** - 0.5 segundos por padrão
- **Validação de ações** - verifica antes de executar
- **Tratamento de erros** - recuperação automática

## Arquivos criados

```
config/
└── native_agent_s_config.json   # Configuração do agente

scripts/
└── native_agent_s_example.py    # Script de exemplo

agent_s_native.py                # Módulo principal
```

## Troubleshooting

### Problemas comuns
- **Erro de permissão**: Execute como administrador
- **Erro de screenshot**: Verifique permissões de tela
- **Erro de aplicativo**: Verifique se o app está instalado

### Logs
- Verifique a saída do console
- Use print() para debug
- Verifique configurações em native_agent_s_config.json

## Próximos passos

1. **Teste com exemplos básicos** primeiro
2. **Experimente comandos mais complexos**
3. **Personalize configurações** se necessário
4. **Integre com outros sistemas** se necessário

## Suporte

Para problemas:
1. Verifique os logs do console
2. Teste com exemplos básicos
3. Verifique permissões do sistema
4. Consulte a documentação
