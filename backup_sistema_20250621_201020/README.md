# 🧠 Sistema Integrado de Conhecimento - Guia Completo

## 📖 Sobre o Sistema

O **Sistema Integrado de Conhecimento** é uma ferramenta completa que combina inteligência artificial, processamento de documentos, automação e backup em uma única interface. Ideal para estudantes, pesquisadores, profissionais e qualquer pessoa que trabalhe com documentos e queira aproveitar o poder da IA.

### 🎯 O que o Sistema Faz

- **📚 Processa documentos** de todos os tipos (PDF, Word, Excel, PowerPoint, E-books)
- **🧠 Analisa conteúdo** usando inteligência artificial (LangChain + TensorFlow)
- **🔍 Busca informações** de forma inteligente na sua base de conhecimento
- **📁 Gerencia projetos** com backup automático para Google Drive e Terabox
- **🔄 Automatiza tarefas** com Docker e N8N
- **📧 Envia notificações** por e-mail automaticamente

---

## 🚀 Primeiros Passos

### 1. 📥 Baixar e Instalar

#### Windows
1. **Baixe o Python** (versão 3.8 ou superior):
   - Acesse: https://www.python.org/downloads/
   - Clique em "Download Python"
   - **IMPORTANTE**: Marque a caixa "Add Python to PATH" durante a instalação

2. **Baixe o sistema**:
   - Extraia todos os arquivos para uma pasta (ex: `C:\AILocal`)
   - Abra o Prompt de Comando (cmd) na pasta

3. **Instale as dependências**:
   ```cmd
   pip install -r requirements_knowledge_system.txt
   pip install -r requirements_projects_manager.txt
   ```

#### Mac/Linux
1. **Instale o Python** (já vem instalado na maioria dos sistemas)
2. **Abra o Terminal** na pasta do sistema
3. **Execute**:
   ```bash
   pip3 install -r requirements_knowledge_system.txt
   pip3 install -r requirements_projects_manager.txt
   ```

### 2. 🎮 Iniciar o Sistema

```bash
python integrated_knowledge_interface.py
```

**O sistema abrirá uma janela com 7 abas principais:**

---

## 📋 Guia das Abas

### 🧠 Aba "Conhecimento"
**Para processar e analisar documentos**

#### Como Usar:
1. **Adicionar Documentos**:
   - Clique em "📁 Selecionar Arquivo" para um documento
   - Clique em "📂 Selecionar Pasta" para uma pasta inteira
   - O sistema processará automaticamente

2. **Fazer Perguntas**:
   - Digite sua pergunta no campo "Pergunta:"
   - Clique em "🔍 Consultar"
   - O sistema responderá baseado nos documentos processados

3. **Ver Resultados**:
   - As respostas aparecem na área "Resultados"
   - O sistema mostra de quais documentos a informação veio

#### Formatos Suportados:
- ✅ **Microsoft Office**: Word (.docx, .doc), Excel (.xlsx, .xls), PowerPoint (.pptx, .ppt)
- ✅ **LibreOffice**: Texto (.odt), Planilha (.ods), Apresentação (.odp)
- ✅ **E-books**: EPUB, MOBI (Kindle)
- ✅ **Outros**: PDF, TXT, Markdown, CSV

### 🐳 Aba "Docker"
**Para gerenciar aplicações em containers**

#### Como Usar:
1. **Ver Containers**:
   - A lista mostra todos os containers instalados
   - Status: "running" (rodando), "stopped" (parado)

2. **Controlar Containers**:
   - Selecione um container na lista
   - Clique em "▶️ Iniciar" para rodar
   - Clique em "⏹️ Parar" para parar
   - Clique em "🗑️ Remover" para deletar

3. **Ver Imagens**:
   - Lista todas as imagens disponíveis
   - Clique em "🚀 Executar" para criar um novo container

### 🔄 Aba "N8N"
**Para automação de tarefas**

#### Como Usar:
1. **Conectar ao N8N**:
   - Digite a URL (padrão: http://localhost:5678)
   - Digite o token de acesso (se tiver)
   - Clique em "🔗 Conectar"

2. **Gerenciar Workflows**:
   - Lista todos os workflows criados
   - Clique em "▶️ Ativar" para ativar
   - Clique em "⏸️ Desativar" para parar

### 🔌 Aba "MCPs"
**Para integração com ferramentas externas**

#### Como Usar:
1. **Ver MCPs Disponíveis**:
   - Lista todas as ferramentas disponíveis
   - Sistema de arquivos, GitHub, banco de dados, etc.

2. **Criar Workflows MCP**:
   - Selecione o tipo: Webhook, Data Architecture, etc.
   - Clique em "⚡ Criar Workflow MCP"

### 📊 Aba "Análise"
**Para análises avançadas dos documentos**

#### Como Usar:
1. **Análise de Documentos**:
   - Ajuste o número de clusters (grupos)
   - Clique em "📊 Analisar Documentos"
   - Veja como os documentos se agrupam

2. **Análise de Sentimento**:
   - Clique em "😊 Analisar Sentimento"
   - Veja se os textos são positivos, negativos ou neutros

### 📁 Aba "Projects Manager"
**Para backup e gerenciamento de projetos**

#### Como Usar:
1. **Buscar Projetos**:
   - Digite o nome do projeto no campo de busca
   - Clique em "Buscar"

2. **Exportar Projeto**:
   - Selecione um projeto na lista
   - Clique em "Exportar e Enviar"
   - Digite os e-mails para receber a senha
   - O sistema criará um arquivo zip protegido e enviará para Google Drive/Terabox

3. **Ver Histórico**:
   - Lista todos os backups realizados
   - Mostra data, projeto e status

### 📦 Aba "Backup & Relatórios"
**Para backup automático e relatórios**

#### Como Usar:
1. **Configurar Backup**:
   - Digite seu email do Gmail
   - Digite a senha de app do Gmail
   - Clique em "💾 Salvar Configurações"
   - Teste as configurações com "🧪 Testar Configurações"

2. **Criar Backup**:
   - Selecione o projeto que deseja fazer backup
   - Adicione uma descrição (opcional)
   - Clique em "🔄 Criar Backup"
   - O sistema irá:
     - Criar um arquivo ZIP criptografado
     - Enviar para o Google Drive
     - Enviar email com a senha e link

3. **Ver Histórico**:
   - A tabela mostra todos os backups realizados
   - Inclui data, arquivo, tamanho e status
   - Links diretos para o Google Drive
   - Senhas dos arquivos ZIP

4. **Relatórios**:
   - Clique em "📧 Enviar Relatório"
   - Receba um relatório completo por email
   - Inclui todos os backups e estatísticas

#### Recursos:
- Backup automático para Google Drive
- Arquivos ZIP criptografados com senha
- Relatórios detalhados por email
- Histórico completo de backups
- Interface intuitiva e moderna

### ⚙️ Aba "Configuração"
**Para configurar todas as credenciais**

#### Configurações Principais:

**🤖 OpenAI & LangChain**
- **OpenAI API Key**: Sua chave da OpenAI (obtenha em: https://platform.openai.com/api-keys)
- **Modelo**: Escolha entre GPT-3.5, GPT-4, etc.

**📧 Configurações de E-mail**
- **E-mail**: Seu e-mail para envio de notificações
- **Senha**: Senha do e-mail (use senha de app para Gmail)
- **Servidor SMTP**: smtp.gmail.com (padrão)
- **Porta**: 587 (padrão)

**☁️ Google Drive**
- **Client ID**: ID do cliente Google (obtenha no Google Cloud Console)
- **Client Secret**: Chave secreta do Google
- **Clique em "🔐 Autenticar Google Drive"** para configurar

**📦 Terabox**
- **Username**: Seu usuário do Terabox
- **Password**: Sua senha do Terabox
- **Clique em "🔐 Autenticar Terabox"** para configurar

**🔄 N8N**
- **URL**: http://localhost:5678 (padrão)
- **Token**: Token de acesso (se configurado)

#### Botões de Ação:
- **💾 Salvar Configuração**: Salva todas as configurações
- **📂 Carregar Configuração**: Carrega configurações salvas
- **🧪 Testar Configurações**: Testa se tudo está funcionando
- **🔄 Resetar Configurações**: Limpa todas as configurações

---

## 🔧 Configuração Detalhada

### 1. 🔑 Obter OpenAI API Key

1. Acesse: https://platform.openai.com/api-keys
2. Faça login ou crie uma conta
3. Clique em "Create new secret key"
4. Copie a chave gerada
5. Cole na aba "Configuração" → "OpenAI API Key"

### 2. 📧 Configurar E-mail (Gmail)

1. **Ativar verificação em duas etapas**:
   - Acesse: https://myaccount.google.com/security
   - Ative "Verificação em duas etapas"

2. **Gerar senha de app**:
   - Ainda em Segurança, clique em "Senhas de app"
   - Selecione "E-mail" e "Windows"
   - Copie a senha gerada (16 caracteres)

3. **Configurar no sistema**:
   - E-mail: seu_email@gmail.com
   - Senha: a senha de app gerada
   - Servidor: smtp.gmail.com
   - Porta: 587

### 3. ☁️ Configurar Google Drive

1. **Criar projeto no Google Cloud**:
   - Acesse: https://console.cloud.google.com/
   - Crie um novo projeto
   - Ative a API do Google Drive

2. **Criar credenciais**:
   - Vá em "APIs & Services" → "Credentials"
   - Clique em "Create Credentials" → "OAuth 2.0 Client IDs"
   - Configure as URLs de redirecionamento

3. **Configurar no sistema**:
   - Cole o Client ID e Client Secret
   - Clique em "🔐 Autenticar Google Drive"
   - Siga as instruções na tela

### 4. 📦 Configurar Terabox

1. **Criar conta no Terabox** (se não tiver):
   - Acesse: https://www.terabox.com/
   - Registre-se gratuitamente

2. **Configurar no sistema**:
   - Digite seu username e password
   - Clique em "🔐 Autenticar Terabox"
   - O sistema salvará o token automaticamente

---

## 📚 Exemplos de Uso

### 📖 Exemplo 1: Análise de Documentos Acadêmicos

**Situação**: Você tem vários PDFs de artigos científicos e quer extrair informações específicas.

**Passos**:
1. Vá para a aba "Conhecimento"
2. Clique em "📂 Selecionar Pasta" e escolha a pasta com os PDFs
3. Aguarde o processamento (pode demorar alguns minutos)
4. Digite perguntas como:
   - "Quais são os principais métodos utilizados?"
   - "Quais autores são mais citados?"
   - "Quais são as conclusões principais?"

### 💼 Exemplo 2: Backup de Projetos de Trabalho

**Situação**: Você quer fazer backup de projetos importantes para a nuvem.

**Passos**:
1. Configure Google Drive e Terabox na aba "Configuração"
2. Vá para a aba "Projects Manager"
3. Selecione o projeto que quer fazer backup
4. Clique em "Exportar e Enviar"
5. Digite seu e-mail para receber a senha
6. O arquivo será enviado para a nuvem e você receberá a senha por e-mail

### 🔄 Exemplo 3: Automação de Tarefas

**Situação**: Você quer automatizar o processamento de documentos.

**Passos**:
1. Configure N8N na aba "Configuração"
2. Vá para a aba "N8N"
3. Crie workflows para automatizar tarefas
4. Use a aba "MCPs" para integrar com outras ferramentas

---

## 🚨 Solução de Problemas

### ❌ Erro: "Python não encontrado"
**Solução**: Instale o Python e marque "Add Python to PATH"

### ❌ Erro: "Módulo não encontrado"
**Solução**: Execute novamente:
```bash
pip install -r requirements_knowledge_system.txt
pip install -r requirements_projects_manager.txt
```

### ❌ Erro: "OpenAI API Key inválida"
**Solução**: 
1. Verifique se a chave está correta
2. Verifique se tem créditos na conta OpenAI
3. Teste a chave em: https://platform.openai.com/api-keys

### ❌ Erro: "E-mail não enviado"
**Solução**:
1. Verifique se ativou verificação em duas etapas no Gmail
2. Use senha de app (não a senha normal)
3. Verifique se o servidor SMTP está correto

### ❌ Erro: "Google Drive não conecta"
**Solução**:
1. Verifique se ativou a API do Google Drive
2. Verifique se as credenciais estão corretas
3. Tente autenticar novamente

### ❌ Erro: "Terabox não conecta"
**Solução**:
1. Verifique se o username e password estão corretos
2. Verifique se a conta não está bloqueada
3. Tente fazer login manualmente no site

### ❌ Erro: "Docker não funciona"
**Solução**:
1. Instale o Docker Desktop
2. Verifique se o Docker está rodando
3. No Windows, execute como administrador

---

## 📞 Suporte

### 🆘 Preciso de Ajuda!

**Antes de pedir ajuda, verifique**:
1. ✅ Python 3.8+ instalado
2. ✅ Todas as dependências instaladas
3. ✅ Credenciais configuradas corretamente
4. ✅ Internet funcionando

### 📧 Contato
- **Email**: suporte@sistema-conhecimento.com
- **Documentação**: [docs.sistema-conhecimento.com](https://docs.sistema-conhecimento.com)
- **Issues**: [GitHub Issues](https://github.com/sistema-conhecimento/issues)

### 📚 Recursos Adicionais
- **Tutorial em Vídeo**: [YouTube](https://youtube.com/sistema-conhecimento)
- **FAQ**: [Perguntas Frequentes](faq.md)
- **Exemplos**: [pasta examples/](examples/)

---

## 🎯 Dicas de Uso

### 💡 Dicas para Melhores Resultados

1. **📄 Qualidade dos Documentos**:
   - Use PDFs de boa qualidade
   - Evite documentos escaneados com baixa resolução
   - Prefira documentos em texto (não imagens)

2. **🔍 Perguntas Eficazes**:
   - Seja específico nas perguntas
   - Use palavras-chave relevantes
   - Faça perguntas diretas

3. **📁 Organização de Projetos**:
   - Mantenha projetos organizados em pastas
   - Use nomes descritivos
   - Faça backup regularmente

4. **⚙️ Configuração**:
   - Salve as configurações após configurar
   - Teste as configurações regularmente
   - Mantenha as credenciais atualizadas

### 🚀 Funcionalidades Avançadas

1. **Análise de Sentimento**: Use para entender o tom dos documentos
2. **Clustering**: Agrupe documentos similares automaticamente
3. **Backup Automático**: Configure backup automático de projetos
4. **Workflows**: Crie automações personalizadas com N8N

---

## 📈 Próximas Atualizações

### 🔄 Em Desenvolvimento
- [ ] Interface web (navegador)
- [ ] Reconhecimento de voz
- [ ] Mais formatos de documento
- [ ] Integração com mais serviços

### 📋 Planejado
- [ ] Versão mobile
- [ ] API para desenvolvedores
- [ ] Mais idiomas
- [ ] Análise de imagens

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- **OpenAI** pela API GPT
- **LangChain** pelo framework de IA
- **TensorFlow** pelas ferramentas de machine learning
- **Google** pelo Google Drive
- **Terabox** pelo armazenamento em nuvem
- **N8N** pela automação
- **Docker** pela containerização

---

**🎉 Obrigado por usar o Sistema Integrado de Conhecimento!**

*Transformando documentos em conhecimento inteligente desde 2024* 