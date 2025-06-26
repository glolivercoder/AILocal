# Guia de Configuração do Google Drive

Este guia explica como configurar o Google Drive para uso com o sistema de backup.

## 1. Criar Projeto no Google Cloud

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Anote o ID do projeto

## 2. Ativar a API do Google Drive

1. No menu lateral, vá em "APIs e Serviços" > "Biblioteca"
2. Pesquise por "Google Drive API"
3. Clique em "Ativar"

## 3. Criar Credenciais

1. No menu lateral, vá em "APIs e Serviços" > "Credenciais"
2. Clique em "Criar Credenciais" > "ID do Cliente OAuth"
3. Configure a tela de consentimento:
   - Tipo de usuário: Externo
   - Nome do app: Sistema de Backup
   - Email de suporte: seu.email@gmail.com
   - Domínios autorizados: localhost

4. Crie um ID do Cliente OAuth:
   - Tipo de aplicativo: Aplicativo para Desktop
   - Nome: Sistema de Backup Desktop

5. Faça download do arquivo JSON de credenciais
6. Renomeie para `credentials.json` e coloque na pasta do projeto

## 4. Configurar Gmail

1. Acesse [Configurações de Segurança do Google](https://myaccount.google.com/security)
2. Ative a verificação em duas etapas
3. Crie uma senha de app:
   - Vá em "Senhas de app"
   - Selecione "Email" e "Windows Computer"
   - Copie a senha gerada (16 caracteres)

## 5. Configurar no Sistema

1. Abra a aba "📦 Backup & Relatórios"
2. Configure seu email:
   - Email: seu.email@gmail.com
   - Senha: a senha de app gerada

3. Clique em "💾 Salvar Configurações"
4. Teste a configuração:
   - Clique em "🧪 Testar Configurações"
   - Você receberá um email de teste
   - O sistema abrirá o navegador para autenticar com o Google

## Observações

- A senha de app do Gmail é diferente da sua senha normal
- As credenciais do Google Drive são salvas em `token.json`
- O sistema usa apenas as permissões mínimas necessárias
- Os backups são salvos em sua conta pessoal do Google Drive

## Solução de Problemas

### Erro de Autenticação do Gmail
- Verifique se está usando a senha de app correta
- Certifique-se que a verificação em duas etapas está ativa
- Tente gerar uma nova senha de app

### Erro no Google Drive
- Verifique se o arquivo `credentials.json` está correto
- Certifique-se que a API do Drive está ativa
- Delete o arquivo `token.json` e tente novamente

### Outros Problemas
- Verifique os logs do sistema
- Certifique-se que tem espaço no Google Drive
- Verifique sua conexão com a internet 