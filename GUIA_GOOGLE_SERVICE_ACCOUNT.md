# 🔧 Guia de Configuração - Google Service Account

## 🎯 **Por que Service Account?**

O Service Account elimina o problema de OAuth interativo que estava causando timeouts na interface. É mais estável e adequado para automação.

## 📋 **Passo a Passo:**

### 1. **Criar Service Account no Google Cloud:**

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Vá para **IAM & Admin** > **Service Accounts**
4. Clique em **Create Service Account**
5. Preencha:
   - **Name**: AiAgenteMCP
   - **Description**: Service Account para AiAgenteMCP

### 2. **Gerar Credenciais:**

1. Clique no Service Account criado
2. Vá para a aba **Keys**
3. Clique **Add Key** > **Create New Key**
4. Escolha **JSON** e clique **Create**
5. Baixe o arquivo JSON

### 3. **Configurar no Projeto:**

1. Renomeie o arquivo baixado para `service_account_credentials.json`
2. Coloque na pasta raiz do projeto (`G:\AILocal\`)

### 4. **Habilitar APIs:**

No Google Cloud Console, habilite:
- Google Drive API
- Gmail API (se necessário)

### 5. **Instalar Dependências:**

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 6. **Testar:**

```python
from google_service_account import google_service

# Testar conexão
success, message = google_service.test_connection()
print(f"Teste: {message}")
```

## ✅ **Benefícios:**

- ❌ **Sem OAuth interativo**
- ❌ **Sem timeouts**
- ❌ **Sem abertura de navegador**
- ✅ **Conexão direta e estável**
- ✅ **Ideal para automação**
- ✅ **Sem intervenção do usuário**

## 🔒 **Segurança:**

- Mantenha `service_account_credentials.json` seguro
- Não compartilhe as credenciais
- Use apenas as permissões necessárias

## 🚀 **Resultado:**

Após a configuração, a interface carregará **instantaneamente** sem problemas de autenticação!
