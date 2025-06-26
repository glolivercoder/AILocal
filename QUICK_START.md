# ⚡ Guia de Início Rápido

## 🚀 Comece a Usar em 5 Minutos

### 1️⃣ Instalação Rápida

**Windows:**
```cmd
# 1. Baixe e instale Python (marque "Add Python to PATH")
# 2. Abra cmd na pasta do sistema
pip install -r requirements_knowledge_system.txt
pip install -r requirements_projects_manager.txt
```

**Mac/Linux:**
```bash
# 1. Abra terminal na pasta do sistema
pip3 install -r requirements_knowledge_system.txt
pip3 install -r requirements_projects_manager.txt
```

### 2️⃣ Iniciar o Sistema
```bash
python integrated_knowledge_interface.py
```

### 3️⃣ Configuração Mínima

**Para começar a usar imediatamente:**

1. **Abra a aba "Configuração"**
2. **Configure apenas o essencial:**
   - OpenAI API Key (obrigatório para IA)
   - E-mail SMTP (para notificações)

3. **Clique em "💾 Salvar Configuração"**

---

## 🎯 Primeiros Passos

### 📚 Processar seu Primeiro Documento

1. **Vá para a aba "Conhecimento"**
2. **Clique em "📁 Selecionar Arquivo"**
3. **Escolha um PDF ou documento**
4. **Aguarde o processamento**
5. **Digite uma pergunta** no campo "Pergunta:"
6. **Clique em "🔍 Consultar"**

**Exemplo de perguntas:**
- "Qual é o tema principal deste documento?"
- "Quais são os pontos mais importantes?"
- "Resuma este documento em 3 tópicos"

### 📁 Fazer seu Primeiro Backup

1. **Vá para a aba "Projects Manager"**
2. **Selecione um projeto na lista**
3. **Clique em "Exportar e Enviar"**
4. **Digite seu e-mail**
5. **Aguarde o envio**

---

## ⚙️ Configuração Completa (Opcional)

### 🔑 OpenAI API Key
1. Acesse: https://platform.openai.com/api-keys
2. Crie uma conta ou faça login
3. Clique em "Create new secret key"
4. Copie a chave (começa com "sk-")
5. Cole na aba "Configuração"

### 📧 E-mail para Notificações
1. **Para Gmail:**
   - Ative verificação em duas etapas
   - Gere senha de app
   - Use: smtp.gmail.com, porta 587

2. **Cole no sistema:**
   - E-mail: seu_email@gmail.com
   - Senha: senha_de_app_gerada

### ☁️ Google Drive (Opcional)
1. Acesse: https://console.cloud.google.com/
2. Crie projeto e ative API do Drive
3. Crie credenciais OAuth 2.0
4. Cole Client ID e Secret
5. Clique em "🔐 Autenticar Google Drive"

### 📦 Terabox (Opcional)
1. Crie conta em: https://www.terabox.com/
2. Digite username e password no sistema
3. Clique em "🔐 Autenticar Terabox"

---

## 🎮 Uso Básico

### 📖 Analisar Documentos
```
1. Adicione documentos (PDF, Word, Excel, etc.)
2. Aguarde o processamento
3. Faça perguntas sobre o conteúdo
4. Receba respostas inteligentes
```

### 📊 Análise Avançada
```
1. Vá para a aba "Análise"
2. Clique em "📊 Analisar Documentos"
3. Veja como os documentos se agrupam
4. Clique em "😊 Analisar Sentimento"
5. Veja o tom dos textos
```

### 🐳 Gerenciar Aplicações
```
1. Vá para a aba "Docker"
2. Veja containers rodando
3. Inicie/pare containers
4. Execute novas aplicações
```

### 🔄 Automatizar Tarefas
```
1. Configure N8N na aba "Configuração"
2. Vá para a aba "N8N"
3. Crie workflows de automação
4. Ative os workflows
```

---

## 🚨 Problemas Comuns

### ❌ "Python não encontrado"
**Solução:** Reinstale Python marcando "Add Python to PATH"

### ❌ "Módulo não encontrado"
**Solução:** Execute novamente:
```bash
pip install -r requirements_knowledge_system.txt
pip install -r requirements_projects_manager.txt
```

### ❌ "OpenAI API Key inválida"
**Solução:** 
1. Verifique se a chave está correta
2. Verifique se tem créditos na conta
3. Teste em: https://platform.openai.com/api-keys

### ❌ "E-mail não enviado"
**Solução:**
1. Ative verificação em duas etapas no Gmail
2. Use senha de app (não a senha normal)
3. Verifique: smtp.gmail.com, porta 587

---

## 💡 Dicas Rápidas

### 🎯 Para Melhores Resultados
- **Use documentos de boa qualidade**
- **Seja específico nas perguntas**
- **Processe poucos arquivos por vez**
- **Salve configurações regularmente**

### 🔍 Perguntas Eficazes
- ✅ "Quais são os principais métodos?"
- ✅ "Resuma as conclusões"
- ✅ "Liste os pontos importantes"
- ❌ "Fale sobre o documento"

### 📁 Organização
- **Mantenha projetos em pastas organizadas**
- **Use nomes descritivos**
- **Faça backup regularmente**

---

## 📞 Precisa de Ajuda?

### 🆘 Suporte Rápido
1. **Verifique se Python está instalado:** `python --version`
2. **Verifique se dependências estão instaladas**
3. **Teste configurações** na aba "Configuração"
4. **Consulte o FAQ:** [FAQ.md](FAQ.md)

### 📧 Contato
- **Email:** suporte@sistema-conhecimento.com
- **Documentação:** [README.md](README.md)
- **Issues:** GitHub do projeto

---

## 🎉 Pronto!

**Agora você pode:**
- ✅ Processar documentos com IA
- ✅ Fazer perguntas inteligentes
- ✅ Fazer backup de projetos
- ✅ Automatizar tarefas
- ✅ Gerenciar aplicações

**Próximo passo:** Explore as outras abas e funcionalidades avançadas!

---

**💡 Dica:** Comece com documentos simples (PDFs de texto) para testar. Depois experimente com documentos mais complexos. 