#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Integração MCP - Cursor
Testa as funcionalidades de integração com MCPs do Cursor
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def test_cursor_mcp_manager():
    """Testa o gerenciador de MCPs do Cursor"""
    print("🔍 Testando CursorMCPManager...")
    
    try:
        from cursor_mcp_manager import CursorMCPManager
        
        manager = CursorMCPManager()
        print("✅ CursorMCPManager importado com sucesso")
        
        # Testar busca de configuração
        config_path = manager.find_mcp_config()
        if config_path:
            print(f"✅ Configuração MCP encontrada em: {config_path}")
        else:
            print("⚠️  Configuração MCP não encontrada")
        
        # Testar leitura de configuração
        config = manager.read_mcp_config()
        if config:
            print(f"✅ Configuração lida com sucesso: {len(config.get('mcpServers', {}))} MCPs")
            
            # Listar MCPs encontrados
            for name, mcp_config in config.get('mcpServers', {}).items():
                command = mcp_config.get('command', 'N/A')
                if isinstance(command, list):
                    command = ' '.join(command)
                print(f"  📦 {name}: {command}")
        else:
            print("⚠️  Nenhuma configuração MCP encontrada")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar CursorMCPManager: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro no teste CursorMCPManager: {e}")
        return False

def test_ai_agent_gui_mcp():
    """Testa a integração MCP na interface principal"""
    print("\n🔍 Testando integração MCP na interface...")
    
    try:
        # Verificar se o arquivo foi modificado corretamente
        with open('ai_agent_gui.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se os novos métodos foram adicionados
        required_methods = [
            'execute_npx_command',
            'add_npx_command', 
            'show_terminal_output',
            'browse_root_directory',
            'load_cursor_mcps',
            'save_cursor_mcps'
        ]
        
        missing_methods = []
        for method in required_methods:
            if f"def {method}(self):" not in content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Métodos faltando: {missing_methods}")
            return False
        else:
            print("✅ Todos os métodos MCP foram adicionados")
        
        # Verificar se os botões NPX foram adicionados
        npx_buttons = [
            'execute_npx_btn',
            'add_npx_command_btn',
            'terminal_output_btn'
        ]
        
        missing_buttons = []
        for button in npx_buttons:
            if button not in content:
                missing_buttons.append(button)
        
        if missing_buttons:
            print(f"❌ Botões faltando: {missing_buttons}")
            return False
        else:
            print("✅ Todos os botões NPX foram adicionados")
        
        # Verificar se a tabela Cursor MCPs foi adicionada
        if 'cursor_mcps_table' not in content:
            print("❌ Tabela Cursor MCPs não encontrada")
            return False
        else:
            print("✅ Tabela Cursor MCPs adicionada")
        
        # Verificar se o campo de diretório raiz foi adicionado
        if 'root_directory_input' not in content:
            print("❌ Campo de diretório raiz não encontrado")
            return False
        else:
            print("✅ Campo de diretório raiz adicionado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste da interface: {e}")
        return False

def test_npx_availability():
    """Testa se NPX está disponível no sistema"""
    print("\n🔍 Testando disponibilidade do NPX...")
    
    try:
        result = subprocess.run(['npx', '--version'], 
                              capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print(f"✅ NPX disponível: {result.stdout.strip()}")
            return True
        else:
            print("❌ NPX não está disponível")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar NPX: {e}")
        return False

def test_directory_structure():
    """Testa a estrutura de diretórios necessária"""
    print("\n🔍 Testando estrutura de diretórios...")
    
    required_files = [
        'ai_agent_gui.py',
        'cursor_mcp_manager.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Arquivos faltando: {missing_files}")
        return False
    else:
        print("✅ Todos os arquivos necessários estão presentes")
        return True

def generate_test_report(results):
    """Gera relatório de teste"""
    print("\n" + "="*50)
    print("📊 RELATÓRIO DE TESTE - INTEGRAÇÃO MCP")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"Total de testes: {total_tests}")
    print(f"Testes aprovados: {passed_tests}")
    print(f"Testes falharam: {total_tests - passed_tests}")
    print(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetalhes dos testes:")
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {test_name}: {status}")
    
    # Salvar relatório em arquivo
    report_data = {
        'timestamp': str(Path().absolute()),
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'success_rate': (passed_tests/total_tests)*100,
        'test_results': results
    }
    
    with open('Teste_MCP_Integration_Report.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório salvo em: Teste_MCP_Integration_Report.json")
    
    if passed_tests == total_tests:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema MCP pronto para uso.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os problemas acima.")

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes de integração MCP...")
    
    # Executar testes
    results = {
        'Estrutura de Diretórios': test_directory_structure(),
        'CursorMCPManager': test_cursor_mcp_manager(),
        'Interface MCP': test_ai_agent_gui_mcp(),
        'Disponibilidade NPX': test_npx_availability()
    }
    
    # Gerar relatório
    generate_test_report(results)

if __name__ == "__main__":
    main()