#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Correção Automática do Sistema
Corrige problemas identificados no diagnóstico
"""

import sys
import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def fix_rag_system_functional():
    """Corrige o sistema RAG funcional"""
    rag_file = Path("rag_system_functional.py")
    if not rag_file.exists():
        return {"status": "error", "message": "Arquivo rag_system_functional.py não encontrado"}
    
    try:
        content = rag_file.read_text(encoding='utf-8')
        
        # Verificar se o alias já existe
        if "RAGSystemFunctional = UltraSimpleRAG" in content:
            return {"status": "success", "message": "Alias já existe"}
        
        # Adicionar alias no final do arquivo
        if not content.endswith('\n'):
            content += '\n'
        
        content += "\n# Alias para compatibilidade\nRAGSystemFunctional = UltraSimpleRAG\n"
        
        # Fazer backup
        backup_file = rag_file.with_suffix('.py.backup')
        shutil.copy2(rag_file, backup_file)
        
        # Salvar arquivo corrigido
        rag_file.write_text(content, encoding='utf-8')
        
        return {
            "status": "success", 
            "message": "Alias RAGSystemFunctional adicionado",
            "backup": str(backup_file)
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Erro ao corrigir RAG: {e}"}

def fix_bat_file():
    """Corrige o arquivo .bat"""
    bat_file = Path("executar_interface_principal.bat")
    if not bat_file.exists():
        return {"status": "error", "message": "Arquivo .bat não encontrado"}
    
    try:
        content = bat_file.read_text(encoding='utf-8')
        
        # Verificar se já está correto
        if content.startswith('@echo off') and 'chcp 65001' in content:
            return {"status": "success", "message": "Arquivo .bat já está correto"}
        
        # Corrigir arquivo
        lines = content.split('\n')
        
        # Remover @echo off duplicado se existir
        lines = [line for line in lines if line.strip() != '@echo off' or lines.index(line) == 0]
        
        # Garantir que começa com @echo off
        if not lines[0].strip().startswith('@echo off'):
            lines.insert(0, '@echo off')
        
        # Garantir que tem chcp 65001
        if not any('chcp 65001' in line for line in lines):
            lines.insert(1, 'chcp 65001 >nul')
        
        new_content = '\n'.join(lines)
        
        # Fazer backup
        backup_file = bat_file.with_suffix('.bat.backup')
        shutil.copy2(bat_file, backup_file)
        
        # Salvar arquivo corrigido
        bat_file.write_text(new_content, encoding='utf-8')
        
        return {
            "status": "success", 
            "message": "Arquivo .bat corrigido",
            "backup": str(backup_file)
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Erro ao corrigir .bat: {e}"}

def create_requirements_check():
    """Cria script para verificar dependências"""
    check_script = Path("verificar_dependencias.py")
    
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e instalar dependências necessárias
"""

import subprocess
import sys

def check_and_install(package, import_name=None):
    """Verifica e instala um pacote se necessário"""
    if import_name is None:
        import_name = package
    
    try:
        __import__(import_name)
        print(f"✅ {package} já instalado")
        return True
    except ImportError:
        print(f"⚠️  {package} não encontrado. Instalando...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} instalado com sucesso")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Falha ao instalar {package}")
            return False

def main():
    """Verifica dependências principais"""
    print("🔍 Verificando dependências...")
    
    dependencies = [
        ("PyQt5", "PyQt5.QtWidgets"),
        ("requests", "requests"),
        ("pathlib", "pathlib"),
        ("json", "json"),
        ("datetime", "datetime")
    ]
    
    all_ok = True
    for package, import_name in dependencies:
        if not check_and_install(package, import_name):
            all_ok = False
    
    if all_ok:
        print("\n🎉 Todas as dependências estão disponíveis!")
    else:
        print("\n⚠️  Algumas dependências falharam. Verifique manualmente.")
    
    return all_ok

if __name__ == "__main__":
    main()
'''
    
    try:
        check_script.write_text(script_content, encoding='utf-8')
        return {
            "status": "success", 
            "message": "Script de verificação criado",
            "file": str(check_script)
        }
    except Exception as e:
        return {"status": "error", "message": f"Erro ao criar script: {e}"}

def create_simple_launcher():
    """Cria um launcher simples e robusto"""
    launcher = Path("launcher_simples.py")
    
    launcher_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher Simples e Robusto
Tenta executar a interface principal com máxima compatibilidade
"""

import sys
import os
from pathlib import Path

def try_import_and_run(module_name, class_name=None):
    """Tenta importar e executar um módulo"""
    try:
        print(f"🔄 Tentando carregar {module_name}...")
        
        # Importar módulo
        module = __import__(module_name)
        
        if class_name:
            # Executar classe específica
            cls = getattr(module, class_name)
            app = cls()
            app.run()
        else:
            # Executar função main se existir
            if hasattr(module, 'main'):
                module.main()
            else:
                print(f"⚠️  {module_name} carregado mas sem função main")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação em {module_name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar {module_name}: {e}")
        return False

def main():
    """Função principal do launcher"""
    print("🚀 LAUNCHER SIMPLES - Agente Especialista")
    print("=" * 50)
    
    # Verificar diretório
    current_dir = Path.cwd()
    print(f"📁 Diretório: {current_dir}")
    
    # Lista de módulos para tentar
    modules_to_try = [
        ("ai_agent_gui", None),
        ("integrated_knowledge_interface", None),
        ("start_main_interface", None),
        ("app", None)
    ]
    
    # Tentar cada módulo
    for module_name, class_name in modules_to_try:
        module_file = current_dir / f"{module_name}.py"
        if module_file.exists():
            print(f"\n📄 Encontrado: {module_file.name}")
            if try_import_and_run(module_name, class_name):
                print(f"✅ {module_name} executado com sucesso!")
                return
        else:
            print(f"❌ Não encontrado: {module_name}.py")
    
    # Se chegou aqui, nada funcionou
    print("\n❌ Nenhuma interface pôde ser executada")
    print("\n💡 Diagnósticos disponíveis:")
    print("   python diagnostico_sistema.py")
    print("   python verificar_dependencias.py")

if __name__ == "__main__":
    main()
'''
    
    try:
        launcher.write_text(launcher_content, encoding='utf-8')
        return {
            "status": "success", 
            "message": "Launcher simples criado",
            "file": str(launcher)
        }
    except Exception as e:
        return {"status": "error", "message": f"Erro ao criar launcher: {e}"}

def run_corrections():
    """Executa todas as correções"""
    print("🔧 Iniciando correções automáticas...")
    
    corrections = {
        "timestamp": datetime.now().isoformat(),
        "corrections_applied": [],
        "errors": [],
        "summary": {
            "total_corrections": 0,
            "successful_corrections": 0,
            "failed_corrections": 0
        }
    }
    
    # Lista de correções
    correction_functions = [
        ("RAG System Functional", fix_rag_system_functional),
        ("Arquivo BAT", fix_bat_file),
        ("Script de Dependências", create_requirements_check),
        ("Launcher Simples", create_simple_launcher)
    ]
    
    for name, func in correction_functions:
        print(f"\n🔧 Aplicando correção: {name}")
        try:
            result = func()
            corrections["corrections_applied"].append({
                "name": name,
                "result": result
            })
            
            if result["status"] == "success":
                print(f"✅ {name}: {result['message']}")
                corrections["summary"]["successful_corrections"] += 1
            else:
                print(f"❌ {name}: {result['message']}")
                corrections["summary"]["failed_corrections"] += 1
                corrections["errors"].append(f"{name}: {result['message']}")
                
        except Exception as e:
            error_msg = f"Erro em {name}: {e}"
            print(f"❌ {error_msg}")
            corrections["errors"].append(error_msg)
            corrections["summary"]["failed_corrections"] += 1
        
        corrections["summary"]["total_corrections"] += 1
    
    # Salvar relatório
    report_file = Path("Correcoes_Aplicadas.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(corrections, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 RESUMO DAS CORREÇÕES:")
    print(f"   Total: {corrections['summary']['total_corrections']}")
    print(f"   Sucessos: {corrections['summary']['successful_corrections']}")
    print(f"   Falhas: {corrections['summary']['failed_corrections']}")
    
    if corrections["errors"]:
        print(f"\n❌ ERROS:")
        for error in corrections["errors"]:
            print(f"   • {error}")
    
    print(f"\n📄 Relatório salvo em: {report_file}")
    
    # Próximos passos
    if corrections["summary"]["failed_corrections"] == 0:
        print(f"\n🎉 Todas as correções aplicadas com sucesso!")
        print(f"\n🚀 Próximos passos:")
        print(f"   1. python verificar_dependencias.py")
        print(f"   2. python launcher_simples.py")
        print(f"   3. python diagnostico_sistema.py")
    else:
        print(f"\n⚠️  Algumas correções falharam. Verifique os erros acima.")
    
    return corrections

def main():
    """Função principal"""
    try:
        return run_corrections()
    except Exception as e:
        print(f"❌ Erro crítico durante correções: {e}")
        return {"status": "critical_error", "error": str(e)}

if __name__ == "__main__":
    main()