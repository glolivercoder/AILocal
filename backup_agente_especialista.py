#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Backup Completo do Agente Especialista em Desenvolvimento de Apps
Cria backup de todos os componentes principais e recursos do sistema
"""

import os
import shutil
import zipfile
import json
from datetime import datetime
from pathlib import Path

class AgenteEspecialistaBackup:
    """Classe para backup completo do Agente Especialista"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.backup_dir = self.base_dir / "backups_agente_especialista"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Timestamp para o backup
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_name = f"agente_especialista_backup_{self.timestamp}"
        
    def get_principais_componentes(self):
        """Define os principais componentes do agente"""
        return {
            # Interfaces Principais
            "interfaces": [
                "ai_agent_gui.py",
                "integrated_knowledge_interface.py",
                "prompt_manager_gui.py",
                "app.py",
                "start_main_interface.py"
            ],
            
            # Sistema RAG e Conhecimento
            "rag_sistema": [
                "rag_system_functional.py",
                "rag_system_langchain.py",
                "rag_system.py",
                "knowledge_enhancement_system.py"
            ],
            
            # Agentes e MCP
            "agentes_mcp": [
                "ai_agente_mcp.py",
                "mcp_manager.py",
                "mcp_manager_prototype.py",
                "mcp_model.py",
                "mcp_flow_agent.py"
            ],
            
            # Gerenciamento de Prompts
            "prompt_management": [
                "prompt_manager.py",
                "prompt_manager_gui.py"
            ],
            
            # Configuração e Backup
            "config_backup": [
                "config_manager.py",
                "config_ui.py",
                "config_ui_expanded.py"
            ],
            
            # Docker e Automação
            "docker_automation": [
                "docker_n8n_interface.py",
                "docker_compose_generator.py",
                "docker-compose.yml"
            ],
            
            # Scripts de Execução
            "scripts_execucao": [
                "run_ai_agent.py",
                "run_mcp_manager.py",
                "install_dependencies.py"
            ],
            
            # Widgets e Controles
            "widgets_controles": [
                "agent_selector_widget.py",
                "audio_control_widget.py",
                "voice_system.py"
            ],
            
            # Projetos e Gerenciamento
            "projetos": [
                "projects_manager.py",
                "openrouter_calculator.py"
            ],
            
            # Diretórios de Dados
            "diretorios_dados": [
                "rag_data",
                "config",
                "static",
                "templates",
                "models"
            ],
            
            # Arquivos de Configuração
            "config_files": [
                "requirements.txt",
                "requirements_mcp.txt",
                "requirements_langchain.txt",
                "requirements_knowledge_system.txt",
                ".env.example",
                "env.example"
            ],
            
            # Documentação
            "documentacao": [
                "README.md",
                "README_COMPLETO.md",
                "README_AI_AGENT.md",
                "DESENVOLVIMENTOAPP.md",
                "PROMPT_MANAGER_IMPLEMENTADO.md",
                "SISTEMA_RAG_FUNCIONAL_IMPLEMENTADO.md"
            ]
        }
    
    def criar_backup_completo(self):
        """Cria backup completo do agente especialista"""
        print(f"🚀 Iniciando backup completo do Agente Especialista...")
        print(f"📅 Timestamp: {self.timestamp}")
        
        # Criar diretório temporário para o backup
        temp_backup_dir = self.backup_dir / self.backup_name
        temp_backup_dir.mkdir(exist_ok=True)
        
        componentes = self.get_principais_componentes()
        backup_info = {
            "timestamp": self.timestamp,
            "backup_name": self.backup_name,
            "componentes_incluidos": {},
            "arquivos_copiados": [],
            "diretorios_copiados": [],
            "erros": []
        }
        
        # Copiar cada categoria de componentes
        for categoria, arquivos in componentes.items():
            print(f"\n📂 Processando categoria: {categoria}")
            categoria_dir = temp_backup_dir / categoria
            categoria_dir.mkdir(exist_ok=True)
            
            arquivos_categoria = []
            
            for arquivo in arquivos:
                arquivo_path = self.base_dir / arquivo
                
                if arquivo_path.exists():
                    if arquivo_path.is_file():
                        # Copiar arquivo
                        destino = categoria_dir / arquivo_path.name
                        shutil.copy2(arquivo_path, destino)
                        arquivos_categoria.append(arquivo)
                        backup_info["arquivos_copiados"].append(str(arquivo_path))
                        print(f"  ✅ Arquivo copiado: {arquivo}")
                        
                    elif arquivo_path.is_dir():
                        # Copiar diretório
                        destino = categoria_dir / arquivo_path.name
                        shutil.copytree(arquivo_path, destino, ignore_errors=True)
                        arquivos_categoria.append(arquivo)
                        backup_info["diretorios_copiados"].append(str(arquivo_path))
                        print(f"  ✅ Diretório copiado: {arquivo}")
                        
                else:
                    erro = f"Arquivo/diretório não encontrado: {arquivo}"
                    backup_info["erros"].append(erro)
                    print(f"  ❌ {erro}")
            
            backup_info["componentes_incluidos"][categoria] = arquivos_categoria
        
        # Salvar informações do backup
        info_file = temp_backup_dir / "backup_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(backup_info, f, indent=2, ensure_ascii=False)
        
        # Criar arquivo ZIP
        zip_path = self.backup_dir / f"{self.backup_name}.zip"
        print(f"\n📦 Criando arquivo ZIP: {zip_path.name}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_backup_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(temp_backup_dir)
                    zipf.write(file_path, arcname)
        
        # Remover diretório temporário
        shutil.rmtree(temp_backup_dir)
        
        # Criar script de restauração
        self.criar_script_restauracao(backup_info)
        
        print(f"\n✅ Backup completo criado com sucesso!")
        print(f"📁 Localização: {zip_path}")
        print(f"📊 Arquivos copiados: {len(backup_info['arquivos_copiados'])}")
        print(f"📊 Diretórios copiados: {len(backup_info['diretorios_copiados'])}")
        
        if backup_info["erros"]:
            print(f"⚠️  Erros encontrados: {len(backup_info['erros'])}")
            for erro in backup_info["erros"]:
                print(f"   - {erro}")
        
        return zip_path, backup_info
    
    def criar_script_restauracao(self, backup_info):
        """Cria script para restaurar o backup"""
        script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Restauração do Backup do Agente Especialista
Backup criado em: {backup_info['timestamp']}
"""

import os
import shutil
import zipfile
from pathlib import Path

def restaurar_backup():
    """Restaura o backup do agente especialista"""
    print("🔄 Iniciando restauração do backup...")
    
    backup_zip = "{self.backup_name}.zip"
    
    if not Path(backup_zip).exists():
        print(f"❌ Arquivo de backup não encontrado: {{backup_zip}}")
        return False
    
    # Extrair backup
    with zipfile.ZipFile(backup_zip, 'r') as zipf:
        zipf.extractall("restauracao_temp")
    
    print("✅ Backup restaurado em 'restauracao_temp'")
    print("📋 Para usar os arquivos, copie-os para o local desejado")
    
    return True

if __name__ == "__main__":
    restaurar_backup()
'''
        
        script_path = self.backup_dir / f"restaurar_{self.backup_name}.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"📜 Script de restauração criado: {script_path.name}")
    
    def criar_documentacao_backup(self):
        """Cria documentação detalhada do backup"""
        doc_content = f'''# Backup do Agente Especialista em Desenvolvimento de Apps

**Data do Backup:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
**Nome do Backup:** {self.backup_name}

## 🎯 Sobre o Agente Especialista

Este é um agente especializado em desenvolvimento de aplicações que inclui:

### 🚀 Funcionalidades Principais

1. **Geração de Prompts Especializados**
   - Prompts para desenvolvimento de apps móveis (iOS/Android)
   - Prompts para SaaS e micro-SaaS
   - Prompts para MVPs
   - Guias de desenvolvimento completos

2. **Sistema RAG (Retrieval-Augmented Generation)**
   - Base de conhecimento local
   - Integração com Chroma/Qdrant
   - Processamento de documentos

3. **Integração com APIs**
   - OpenRouter (todos os modelos)
   - OpenAI, Claude, Gemini, DeepSeek
   - Modelos gratuitos disponíveis

4. **Raspagem de Dados Web**
   - Puppeteer/Playwright
   - Coleta automatizada de informações

5. **Áreas Especializadas**
   - **Área RAG:** Gerenciamento de conhecimento
   - **Área Prompts:** Geração e gerenciamento de prompts
   - **Área Web Scraping:** Raspagem de dados
   - **Área Configuração:** APIs e configurações

### 🛠️ Tecnologias Incluídas

- **UI/UX:** Material Design, melhores práticas de layout
- **Bancos de Dados:** Recomendações e configurações
- **Segurança:** Proteção de APIs e dados
- **Deploy:** Com e sem Docker
- **Validação:** MVP e SaaS

### 📁 Estrutura do Backup

- `interfaces/`: Interfaces gráficas principais
- `rag_sistema/`: Sistema de conhecimento
- `agentes_mcp/`: Agentes e MCP
- `prompt_management/`: Gerenciamento de prompts
- `config_backup/`: Configurações e backup
- `docker_automation/`: Docker e automação
- `widgets_controles/`: Controles da interface
- `documentacao/`: Documentação completa

### 🔧 Como Restaurar

1. Extraia o arquivo ZIP do backup
2. Execute o script de restauração
3. Instale as dependências: `pip install -r requirements.txt`
4. Execute a interface principal: `python start_main_interface.py`

### 📞 Suporte

Este agente foi projetado para ser um assistente completo no desenvolvimento de aplicações modernas, desde a concepção até o deploy.
'''
        
        doc_path = self.backup_dir / f"DOCUMENTACAO_{self.backup_name}.md"
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print(f"📚 Documentação criada: {doc_path.name}")

def main():
    """Função principal"""
    backup_system = AgenteEspecialistaBackup()
    
    print("🤖 Sistema de Backup do Agente Especialista em Desenvolvimento de Apps")
    print("=" * 70)
    
    try:
        zip_path, backup_info = backup_system.criar_backup_completo()
        backup_system.criar_documentacao_backup()
        
        print("\n" + "=" * 70)
        print("✅ BACKUP CONCLUÍDO COM SUCESSO!")
        print(f"📦 Arquivo: {zip_path.name}")
        print(f"📁 Localização: {zip_path.parent}")
        
    except Exception as e:
        print(f"❌ Erro durante o backup: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()