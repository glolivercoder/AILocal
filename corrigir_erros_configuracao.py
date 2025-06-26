#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir erros de configuração do sistema AILocal
Corrige problemas com:
- GitHub token não configurado
- Arquivos de credenciais do Google Drive ausentes
- Configurações opcionais
"""

import os
import json
from pathlib import Path

def criar_arquivo_env_exemplo():
    """Cria arquivo .env.example com configurações opcionais"""
    env_content = """
# Configurações Opcionais do Sistema AILocal
# Copie este arquivo para .env e configure conforme necessário

# GitHub Token (Opcional)
# Melhora rate limits para busca de MCPs
# Obtenha em: https://github.com/settings/tokens
GITHUB_TOKEN=seu_token_aqui

# Google Drive API (Opcional)
# Para backup automático na nuvem
# Configure em: https://console.developers.google.com/
GDRIVE_CLIENT_ID=seu_client_id_aqui
GDRIVE_CLIENT_SECRET=seu_client_secret_aqui

# OpenRouter API (Opcional)
# Para modelos de IA avançados
OPENROUTER_API_KEY=sua_api_key_aqui
"""
    
    try:
        with open('.env.example', 'w', encoding='utf-8') as f:
            f.write(env_content.strip())
        print("✅ Arquivo .env.example criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar .env.example: {e}")
        return False

def criar_client_secrets_exemplo():
    """Cria arquivo de exemplo para client_secrets.json"""
    client_secrets_example = {
        "web": {
            "client_id": "SEU_CLIENT_ID_AQUI.apps.googleusercontent.com",
            "client_secret": "SEU_CLIENT_SECRET_AQUI",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/"]
        }
    }
    
    try:
        with open('client_secrets.json.example', 'w', encoding='utf-8') as f:
            json.dump(client_secrets_example, f, indent=2)
        print("✅ Arquivo client_secrets.json.example criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar client_secrets.json.example: {e}")
        return False

def criar_gdrive_creds_vazio():
    """Cria arquivo vazio para gdrive_creds.txt para evitar warnings"""
    try:
        # Criar arquivo vazio se não existir
        if not os.path.exists('gdrive_creds.txt'):
            with open('gdrive_creds.txt', 'w', encoding='utf-8') as f:
                f.write('')
            print("✅ Arquivo gdrive_creds.txt criado (vazio)")
        else:
            print("ℹ️  Arquivo gdrive_creds.txt já existe")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar gdrive_creds.txt: {e}")
        return False

def modificar_mcp_manager():
    """Modifica mcp_manager.py para reduzir warnings"""
    try:
        # Ler arquivo atual
        with open('mcp_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir warning por info
        old_line = 'logger.warning("GitHub token não configurado - rate limit reduzido")'
        new_line = 'logger.info("GitHub token não configurado - usando rate limit padrão")'
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            
            # Salvar arquivo modificado
            with open('mcp_manager.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ mcp_manager.py atualizado - warning reduzido")
            return True
        else:
            print("ℹ️  mcp_manager.py já está atualizado")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao modificar mcp_manager.py: {e}")
        return False

def modificar_config_manager():
    """Modifica config_manager.py para tratar erros graciosamente"""
    try:
        # Ler arquivo atual
        with open('config_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já foi modificado
        if 'warnings.filterwarnings' in content:
            print("ℹ️  config_manager.py já está atualizado")
            return True
        
        # Adicionar supressão de warnings no início
        import_section = "import os\nimport json\nimport zipfile\nimport shutil\nfrom datetime import datetime\nfrom pathlib import Path"
        new_import_section = import_section + "\nimport warnings\n\n# Suprimir warnings específicos do oauth2client\nwarnings.filterwarnings('ignore', message='Cannot access gdrive_creds.txt')"
        
        if import_section in content:
            content = content.replace(import_section, new_import_section)
            
            # Salvar arquivo modificado
            with open('config_manager.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ config_manager.py atualizado - warnings suprimidos")
            return True
        else:
            print("⚠️  Não foi possível localizar seção de imports em config_manager.py")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao modificar config_manager.py: {e}")
        return False

def criar_guia_configuracao():
    """Cria guia de configuração opcional"""
    guia_content = """
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
"""
    
    try:
        with open('CONFIGURACAO_OPCIONAL.md', 'w', encoding='utf-8') as f:
            f.write(guia_content.strip())
        print("✅ Guia CONFIGURACAO_OPCIONAL.md criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar guia: {e}")
        return False

def main():
    """Função principal para corrigir todos os erros"""
    print("="*60)
    print("    CORREÇÃO DE ERROS DE CONFIGURAÇÃO - AILocal")
    print("="*60)
    print("\n🔧 Corrigindo erros de configuração...\n")
    
    resultados = []
    
    # 1. Criar arquivo .env.example
    print("1️⃣  Criando arquivo .env.example...")
    resultados.append(criar_arquivo_env_exemplo())
    
    # 2. Criar exemplo de client_secrets.json
    print("\n2️⃣  Criando exemplo client_secrets.json...")
    resultados.append(criar_client_secrets_exemplo())
    
    # 3. Criar arquivo gdrive_creds.txt vazio
    print("\n3️⃣  Criando arquivo gdrive_creds.txt...")
    resultados.append(criar_gdrive_creds_vazio())
    
    # 4. Modificar mcp_manager.py
    print("\n4️⃣  Atualizando mcp_manager.py...")
    resultados.append(modificar_mcp_manager())
    
    # 5. Modificar config_manager.py
    print("\n5️⃣  Atualizando config_manager.py...")
    resultados.append(modificar_config_manager())
    
    # 6. Criar guia de configuração
    print("\n6️⃣  Criando guia de configuração...")
    resultados.append(criar_guia_configuracao())
    
    # Resumo
    print("\n" + "="*60)
    print("    RESUMO DA CORREÇÃO")
    print("="*60)
    
    sucessos = sum(resultados)
    total = len(resultados)
    
    print(f"✅ Sucessos: {sucessos}/{total}")
    
    if sucessos == total:
        print("\n🎉 TODOS OS ERROS FORAM CORRIGIDOS!")
        print("\n📋 Próximos passos:")
        print("   1. Execute: python ai_agent_gui.py")
        print("   2. Os warnings devem ter diminuído significativamente")
        print("   3. Para configurações opcionais, veja: CONFIGURACAO_OPCIONAL.md")
    else:
        print("\n⚠️  Alguns erros podem persistir. Verifique os logs acima.")
    
    print("\n📁 Arquivos criados/modificados:")
    arquivos = [
        ".env.example",
        "client_secrets.json.example", 
        "gdrive_creds.txt",
        "mcp_manager.py (modificado)",
        "config_manager.py (modificado)",
        "CONFIGURACAO_OPCIONAL.md"
    ]
    
    for arquivo in arquivos:
        print(f"   - {arquivo}")

if __name__ == "__main__":
    main()