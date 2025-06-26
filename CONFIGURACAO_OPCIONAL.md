# Guia de Configuração Opcional - AILocal

## Visão Geral
Todos os recursos do AILocal funcionam sem configuração adicional. 
As configurações abaixo são **opcionais** e melhoram a experiência:

## 1. GitHub Token (Opcional)
**Benefício**: Melhora rate limits para busca de MCPs

### Como configurar:
1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token (classic)"
3. Selecione escopo: `public_repo`
4. Copie o token gerado
5. Adicione ao arquivo `.env`:
   ```
   GITHUB_TOKEN=seu_token_aqui
   ```

## 2. Google Drive API (Opcional)
**Benefício**: Backup automático na nuvem

### Como configurar:
1. Acesse: https://console.developers.google.com/
2. Crie um novo projeto ou selecione existente
3. Ative a "Google Drive API"
4. Crie credenciais OAuth 2.0
5. Baixe o arquivo `client_secrets.json`
6. Coloque na pasta raiz do projeto

## 3. OpenRouter API (Opcional)
**Benefício**: Acesso a modelos de IA avançados

### Como configurar:
1. Acesse: https://openrouter.ai/
2. Crie uma conta
3. Gere uma API key
4. Adicione ao arquivo `.env`:
   ```
   OPENROUTER_API_KEY=sua_api_key_aqui
   ```

## Arquivo .env
Copie `.env.example` para `.env` e configure:
```bash
cp .env.example .env
```

## Verificação
Após configurar, execute:
```bash
python ai_agent_gui.py
```

Os warnings devem desaparecer e recursos adicionais estarão disponíveis.