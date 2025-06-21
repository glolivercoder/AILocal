#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico do Sistema RAG e Interface Principal
Analisa problemas de importação, dependências e configuração
"""

import sys
import os
import json
import traceback
from pathlib import Path
from datetime import datetime

def test_import(module_name, description=""):
    """Testa importação de um módulo"""
    try:
        __import__(module_name)
        return {
            "status": "success",
            "module": module_name,
            "description": description,
            "error": None
        }
    except ImportError as e:
        return {
            "status": "error",
            "module": module_name,
            "description": description,
            "error": str(e),
            "error_type": "ImportError"
        }
    except Exception as e:
        return {
            "status": "error",
            "module": module_name,
            "description": description,
            "error": str(e),
            "error_type": type(e).__name__
        }

def test_file_exists(file_path, description=""):
    """Testa se um arquivo existe"""
    path = Path(file_path)
    return {
        "status": "success" if path.exists() else "error",
        "file": str(path),
        "description": description,
        "exists": path.exists(),
        "is_file": path.is_file() if path.exists() else False,
        "size": path.stat().st_size if path.exists() and path.is_file() else 0
    }

def test_rag_system():
    """Testa sistemas RAG disponíveis"""
    rag_tests = []
    
    # Teste RAG Funcional
    try:
        from rag_system_functional import UltraSimpleRAG, RAGSystemFunctional
        rag_tests.append({
            "system": "RAGSystemFunctional",
            "status": "success",
            "class_available": "UltraSimpleRAG" in dir(),
            "alias_available": "RAGSystemFunctional" in dir(),
            "error": None
        })
    except Exception as e:
        rag_tests.append({
            "system": "RAGSystemFunctional",
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        })
    
    # Teste RAG LangChain
    try:
        from rag_system_langchain import RAGSystemLangChain
        rag_tests.append({
            "system": "RAGSystemLangChain",
            "status": "success",
            "error": None
        })
    except Exception as e:
        rag_tests.append({
            "system": "RAGSystemLangChain",
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        })
    
    # Teste RAG Simples
    try:
        from rag_system_simple import RAGSystemSimple
        rag_tests.append({
            "system": "RAGSystemSimple",
            "status": "success",
            "error": None
        })
    except Exception as e:
        rag_tests.append({
            "system": "RAGSystemSimple",
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        })
    
    return rag_tests

def test_interface_components():
    """Testa componentes da interface"""
    interface_tests = []
    
    # PyQt5
    interface_tests.append(test_import("PyQt5.QtWidgets", "Interface gráfica principal"))
    interface_tests.append(test_import("PyQt5.QtCore", "Core do PyQt5"))
    interface_tests.append(test_import("PyQt5.QtGui", "GUI do PyQt5"))
    
    # Componentes específicos
    interface_tests.append(test_import("config_manager", "Gerenciador de configurações"))
    interface_tests.append(test_import("config_ui_expanded", "Interface de configurações expandida"))
    interface_tests.append(test_import("agent_selector_widget", "Widget seletor de agente"))
    interface_tests.append(test_import("audio_control_widget", "Widget controle de áudio"))
    interface_tests.append(test_import("ai_agente_mcp", "Agente MCP principal"))
    
    return interface_tests

def test_main_files():
    """Testa arquivos principais"""
    main_files = [
        ("ai_agent_gui.py", "Interface principal do agente"),
        ("start_main_interface.py", "Script de inicialização"),
        ("integrated_knowledge_interface.py", "Interface de conhecimento integrada"),
        ("executar_interface_principal.bat", "Script batch de execução"),
        ("rag_system_functional.py", "Sistema RAG funcional"),
        ("rag_system_langchain.py", "Sistema RAG LangChain"),
        ("rag_system_simple.py", "Sistema RAG simples")
    ]
    
    return [test_file_exists(file, desc) for file, desc in main_files]

def analyze_bat_file():
    """Analisa o arquivo .bat para problemas"""
    bat_file = Path("executar_interface_principal.bat")
    if not bat_file.exists():
        return {"status": "error", "error": "Arquivo .bat não encontrado"}
    
    try:
        content = bat_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        issues = []
        if not content.startswith('@echo off'):
            issues.append("Falta '@echo off' no início")
        
        if 'chcp 65001' not in content:
            issues.append("Falta configuração de codificação UTF-8")
        
        return {
            "status": "success" if not issues else "warning",
            "content_lines": len(lines),
            "issues": issues,
            "has_python_calls": "python" in content.lower()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def check_python_environment():
    """Verifica ambiente Python"""
    return {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "current_directory": str(Path.cwd()),
        "python_path": sys.path[:5],  # Primeiros 5 caminhos
        "platform": sys.platform
    }

def run_full_diagnosis():
    """Executa diagnóstico completo"""
    print("🔍 Iniciando diagnóstico completo do sistema...")
    
    diagnosis = {
        "timestamp": datetime.now().isoformat(),
        "python_environment": check_python_environment(),
        "main_files": test_main_files(),
        "interface_components": test_interface_components(),
        "rag_systems": test_rag_system(),
        "bat_file_analysis": analyze_bat_file(),
        "summary": {
            "total_tests": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "critical_issues": [],
            "recommendations": []
        }
    }
    
    # Calcular estatísticas
    all_tests = (
        diagnosis["main_files"] + 
        diagnosis["interface_components"] + 
        diagnosis["rag_systems"]
    )
    
    diagnosis["summary"]["total_tests"] = len(all_tests)
    diagnosis["summary"]["successful_tests"] = len([t for t in all_tests if t.get("status") == "success"])
    diagnosis["summary"]["failed_tests"] = len([t for t in all_tests if t.get("status") == "error"])
    
    # Identificar problemas críticos
    critical_issues = []
    recommendations = []
    
    # Verificar PyQt5
    pyqt5_available = any(t.get("module") == "PyQt5.QtWidgets" and t.get("status") == "success" 
                         for t in diagnosis["interface_components"])
    if not pyqt5_available:
        critical_issues.append("PyQt5 não disponível - interface gráfica não funcionará")
        recommendations.append("Instalar PyQt5: pip install PyQt5")
    
    # Verificar sistemas RAG
    rag_available = any(t.get("status") == "success" for t in diagnosis["rag_systems"])
    if not rag_available:
        critical_issues.append("Nenhum sistema RAG disponível")
        recommendations.append("Verificar arquivos rag_system_*.py")
    
    # Verificar arquivos principais
    main_gui_exists = any(t.get("file", "").endswith("ai_agent_gui.py") and t.get("exists") 
                         for t in diagnosis["main_files"])
    if not main_gui_exists:
        critical_issues.append("Arquivo principal ai_agent_gui.py não encontrado")
    
    diagnosis["summary"]["critical_issues"] = critical_issues
    diagnosis["summary"]["recommendations"] = recommendations
    
    return diagnosis

def main():
    """Função principal"""
    try:
        # Executar diagnóstico
        diagnosis = run_full_diagnosis()
        
        # Salvar em arquivo JSON
        output_file = Path("Diagnostico.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(diagnosis, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Diagnóstico salvo em: {output_file}")
        
        # Mostrar resumo
        summary = diagnosis["summary"]
        print(f"\n📊 RESUMO DO DIAGNÓSTICO:")
        print(f"   Total de testes: {summary['total_tests']}")
        print(f"   Sucessos: {summary['successful_tests']}")
        print(f"   Falhas: {summary['failed_tests']}")
        
        if summary["critical_issues"]:
            print(f"\n❌ PROBLEMAS CRÍTICOS:")
            for issue in summary["critical_issues"]:
                print(f"   • {issue}")
        
        if summary["recommendations"]:
            print(f"\n💡 RECOMENDAÇÕES:")
            for rec in summary["recommendations"]:
                print(f"   • {rec}")
        
        # Determinar próximos passos
        if not summary["critical_issues"]:
            print(f"\n🎉 Sistema parece estar funcionando! Tente executar:")
            print(f"   python ai_agent_gui.py")
        else:
            print(f"\n⚠️  Corrija os problemas críticos antes de continuar.")
        
        return diagnosis
        
    except Exception as e:
        error_diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "traceback": traceback.format_exc(),
            "status": "critical_error"
        }
        
        with open("Diagnostico.json", 'w', encoding='utf-8') as f:
            json.dump(error_diagnosis, f, indent=2, ensure_ascii=False)
        
        print(f"❌ Erro crítico durante diagnóstico: {e}")
        print(f"Detalhes salvos em Diagnostico.json")
        return error_diagnosis

if __name__ == "__main__":
    main()