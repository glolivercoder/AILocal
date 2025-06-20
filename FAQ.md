# ❓ Perguntas Frequentes (FAQ)

## 🤔 Perguntas Gerais

### Q: O que é o Sistema Integrado de Conhecimento?
**R**: É uma ferramenta que combina inteligência artificial, processamento de documentos, backup automático e automação em uma única interface. Permite analisar documentos, fazer perguntas sobre eles e gerenciar projetos automaticamente.

### Q: Preciso ser programador para usar?
**R**: Não! O sistema foi projetado para ser usado por qualquer pessoa. A interface é intuitiva e todas as funcionalidades são acessíveis através de botões e menus.

### Q: O sistema é gratuito?
**R**: O sistema em si é gratuito, mas algumas funcionalidades requerem serviços pagos:
- **OpenAI API**: Tem custo por uso (muito baixo)
- **Google Drive**: 15GB gratuitos
- **Terabox**: 1TB gratuitos

### Q: Funciona em qual sistema operacional?
**R**: Windows, Mac e Linux. Apenas certifique-se de ter Python 3.8 ou superior instalado.

---

## 📥 Instalação e Configuração

### Q: Como instalo o Python?
**R**: 
1. Acesse https://www.python.org/downloads/
2. Clique em "Download Python"
3. **IMPORTANTE**: Marque "Add Python to PATH" durante a instalação
4. Siga as instruções do instalador

### Q: Erro "pip não encontrado"
**R**: 
1. Reinstale o Python marcando "Add Python to PATH"
2. Ou use: `python -m pip install -r requirements_knowledge_system.txt`

### Q: Erro "Módulo não encontrado"
**R**: Execute novamente a instalação das dependências:
```bash
pip install -r requirements_knowledge_system.txt
pip install -r requirements_projects_manager.txt
```

### Q: O sistema não abre
**R**: 
1. Verifique se o Python está instalado: `python --version`
2. Verifique se as dependências foram instaladas
3. Execute: `python integrated_knowledge_interface.py`
4. Se der erro, copie a mensagem e procure ajuda

---

## 🔑 Configuração de Credenciais

### Q: Como obtenho uma chave da OpenAI?
**R**: 
1. Acesse https://platform.openai.com/api-keys
2. Faça login ou crie uma conta
3. Clique em "Create new secret key"
4. Copie a chave (começa com "sk-")
5. Cole na aba "Configuração" → "OpenAI API Key"

### Q: Quanto custa usar a OpenAI?
**R**: Muito pouco! Para uso pessoal, geralmente custa menos de R$ 10 por mês. A OpenAI dá créditos gratuitos para novos usuários.

### Q: Como configuro o e-mail para notificações?
**R**: 
1. **Para Gmail**: Ative verificação em duas etapas
2. Gere uma senha de app
3. Use essa senha no sistema (não sua senha normal)
4. Servidor: smtp.gmail.com, Porta: 587

### Q: Como configuro o Google Drive?
**R**: 
1. Acesse https://console.cloud.google.com/
2. Crie um projeto
3. Ative a API do Google Drive
4. Crie credenciais OAuth 2.0
5. Cole Client ID e Secret no sistema
6. Clique em "Autenticar Google Drive"

### Q: Como configuro o Terabox?
**R**: 
1. Crie uma conta em https://www.terabox.com/
2. Digite username e password no sistema
3. Clique em "Autenticar Terabox"
4. O sistema salvará o token automaticamente

---

## 📚 Uso do Sistema

### Q: Quais tipos de arquivo posso processar?
**R**: 
- **Microsoft Office**: Word (.docx, .doc), Excel (.xlsx, .xls), PowerPoint (.pptx, .ppt)
- **LibreOffice**: Texto (.odt), Planilha (.ods), Apresentação (.odp)
- **E-books**: EPUB, MOBI (Kindle)
- **Outros**: PDF, TXT, Markdown, CSV

### Q: Por que o processamento demora?
**R**: 
- **PDFs grandes**: Podem demorar alguns minutos
- **Muitos arquivos**: O sistema processa um por vez
- **Primeira vez**: O sistema baixa modelos de IA
- **Internet lenta**: Afeta o download de modelos

### Q: Como faço perguntas eficazes?
**R**: 
- **Seja específico**: "Quais são os principais métodos?" em vez de "Fale sobre o documento"
- **Use palavras-chave**: "métodos", "resultados", "conclusões"
- **Faça perguntas diretas**: "Qual é a conclusão principal?"

### Q: O sistema entende português?
**R**: Sim! O sistema funciona muito bem em português. Você pode fazer perguntas e receber respostas em português.

---

## 📁 Projects Manager

### Q: O que é o Projects Manager?
**R**: É uma ferramenta para fazer backup automático de seus projetos. Ele:
- Compacta projetos em arquivos zip protegidos por senha
- Envia para Google Drive e Terabox automaticamente
- Envia a senha por e-mail
- Mantém histórico de backups

### Q: Como faço backup de um projeto?
**R**: 
1. Vá para a aba "Projects Manager"
2. Selecione o projeto na lista
3. Clique em "Exportar e Enviar"
4. Digite os e-mails para receber a senha
5. Aguarde o envio

### Q: Onde ficam os arquivos de backup?
**R**: 
- **Localmente**: Na pasta "backups" do sistema
- **Google Drive**: Na sua conta do Google Drive
- **Terabox**: Na sua conta do Terabox

### Q: Como recupero um projeto?
**R**: 
1. Baixe o arquivo zip do Google Drive ou Terabox
2. Use a senha enviada por e-mail
3. Extraia o arquivo
4. O projeto estará completo

---

## 🐳 Docker e N8N

### Q: O que é Docker?
**R**: Docker permite rodar aplicações em "containers" isolados. É útil para:
- Rodar aplicações sem instalar no sistema
- Manter diferentes versões de programas
- Organizar aplicações

### Q: Preciso instalar Docker?
**R**: Sim, se quiser usar a aba Docker:
1. Baixe Docker Desktop: https://www.docker.com/products/docker-desktop
2. Instale e reinicie o computador
3. O Docker deve estar rodando

### Q: O que é N8N?
**R**: N8N é uma ferramenta de automação que permite criar "workflows" (fluxos de trabalho) para automatizar tarefas repetitivas.

### Q: Como uso o N8N?
**R**: 
1. Instale o N8N: `npm install -g n8n`
2. Inicie: `n8n start`
3. Acesse: http://localhost:5678
4. Configure no sistema

---

## 🚨 Problemas Comuns

### Q: "OpenAI API Key inválida"
**R**: 
1. Verifique se a chave está correta (começa com "sk-")
2. Verifique se tem créditos na conta OpenAI
3. Teste a chave em: https://platform.openai.com/api-keys

### Q: "E-mail não enviado"
**R**: 
1. Verifique se ativou verificação em duas etapas no Gmail
2. Use senha de app (não a senha normal)
3. Verifique se o servidor SMTP está correto (smtp.gmail.com)

### Q: "Google Drive não conecta"
**R**: 
1. Verifique se ativou a API do Google Drive
2. Verifique se as credenciais estão corretas
3. Tente autenticar novamente

### Q: "Terabox não conecta"
**R**: 
1. Verifique se o username e password estão corretos
2. Verifique se a conta não está bloqueada
3. Tente fazer login manualmente no site

### Q: "Docker não funciona"
**R**: 
1. Instale o Docker Desktop
2. Verifique se o Docker está rodando
3. No Windows, execute como administrador

### Q: "Sistema muito lento"
**R**: 
1. Feche outros programas
2. Verifique se tem RAM suficiente (mínimo 4GB)
3. Verifique a conexão com a internet
4. Processe menos arquivos por vez

---

## 💡 Dicas e Truques

### Q: Como organizar melhor meus documentos?
**R**: 
- Use pastas organizadas por projeto
- Use nomes descritivos para arquivos
- Mantenha uma estrutura consistente
- Faça backup regularmente

### Q: Como obter melhores respostas da IA?
**R**: 
- Use documentos de boa qualidade
- Seja específico nas perguntas
- Use palavras-chave relevantes
- Faça perguntas diretas

### Q: Como economizar com a OpenAI?
**R**: 
- Use o modelo GPT-3.5 (mais barato)
- Faça perguntas específicas
- Processe documentos menores
- Use os créditos gratuitos

### Q: Como manter o sistema atualizado?
**R**: 
- Salve as configurações regularmente
- Teste as configurações periodicamente
- Mantenha as credenciais atualizadas
- Faça backup das configurações

---

## 📞 Suporte

### Q: Onde encontro mais ajuda?
**R**: 
- **Documentação**: README.md (este arquivo)
- **Vídeos**: Canal do YouTube
- **Email**: suporte@sistema-conhecimento.com
- **GitHub**: Issues do projeto

### Q: Como reporto um bug?
**R**: 
1. Descreva o problema detalhadamente
2. Inclua mensagens de erro
3. Explique o que estava tentando fazer
4. Envie para: suporte@sistema-conhecimento.com

### Q: Posso sugerir novas funcionalidades?
**R**: Sim! Envie suas sugestões para:
- Email: suporte@sistema-conhecimento.com
- GitHub: Issues do projeto
- Todas as sugestões são bem-vindas!

---

## 🎯 Próximas Atualizações

### Q: Quando sai a versão web?
**R**: Está em desenvolvimento. Será lançada em breve, permitindo usar o sistema pelo navegador.

### Q: Terá reconhecimento de voz?
**R**: Sim! Está sendo desenvolvido para permitir comandos por voz.

### Q: Terá mais idiomas?
**R**: O sistema já funciona bem em português e inglês. Mais idiomas estão planejados.

### Q: Terá versão mobile?
**R**: Está planejado para o futuro, permitindo usar no celular.

---

**💡 Dica Final**: Se tiver dúvidas, sempre comece verificando se todas as dependências estão instaladas e se as credenciais estão configuradas corretamente. A maioria dos problemas é resolvida assim! 