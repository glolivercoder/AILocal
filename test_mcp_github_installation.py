#!/usr/bin/env python3
"""
Script para testar instalação de MCPs via GitHub
Demonstra as novas funcionalidades do módulo MCP
"""

import sys
import time
from pathlib import Path

def test_github_installation():
    """Testa as funcionalidades de instalação via GitHub"""
    
    print("🚀 Teste de Instalação de MCPs via GitHub")
    print("=" * 60)
    
    try:
        from mcp_manager import MCPManager, GitHubMCPInstaller
        
        # Criar instâncias
        mcp_manager = MCPManager()
        github_installer = GitHubMCPInstaller()
        
        print("✅ MCPManager e GitHubMCPInstaller carregados com sucesso")
        
        # Teste 1: Buscar MCPs no GitHub
        print("\n🔍 Teste 1: Buscando MCPs no GitHub")
        print("-" * 40)
        
        search_terms = ["filesystem", "database", "web", "ai"]
        
        for term in search_terms:
            print(f"Buscando: {term}")
            results = github_installer.search_mcp_on_github(term)
            
            if results:
                print(f"  ✅ Encontrados {len(results)} resultados")
                for i, result in enumerate(results[:3]):  # Mostrar apenas os 3 primeiros
                    print(f"    {i+1}. {result['full_name']} (⭐{result['stars']})")
                    print(f"       {result['description']}")
            else:
                print(f"  ❌ Nenhum resultado encontrado")
            
            print()
        
        # Teste 2: Verificar instalação inteligente
        print("\n🧠 Teste 2: Instalação Inteligente")
        print("-" * 40)
        
        # Simular instalação de um MCP que pode não existir no npm
        test_mcp = "test-custom-mcp"
        
        print(f"Testando instalação inteligente para: {test_mcp}")
        
        # Verificar se existe no npm primeiro
        import subprocess
        npm_check = subprocess.run(
            f"npm view {test_mcp}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if npm_check.returncode == 0:
            print(f"  ✅ Encontrado no npm")
        else:
            print(f"  ❌ Não encontrado no npm, tentando GitHub...")
            
            # Buscar no GitHub
            github_results = github_installer.search_mcp_on_github(test_mcp)
            if github_results:
                print(f"  ✅ Encontrado no GitHub: {github_results[0]['full_name']}")
            else:
                print(f"  ❌ Não encontrado no GitHub também")
        
        # Teste 3: Status de instalação
        print("\n📊 Teste 3: Status de Instalação")
        print("-" * 40)
        
        # Verificar status de alguns MCPs conhecidos
        known_mcps = ["filesystem", "postgres", "github"]
        
        for mcp_name in known_mcps:
            if mcp_name in mcp_manager.mcps:
                status = mcp_manager.get_installation_status(mcp_name)
                print(f"{mcp_name}:")
                print(f"  Instalado: {status.get('installed', False)}")
                print(f"  Método: {status.get('installation_method', 'npm')}")
                print(f"  Status: {status.get('status', 'unknown')}")
                if status.get('github_url'):
                    print(f"  GitHub: {status['github_url']}")
            else:
                print(f"{mcp_name}: Não configurado")
            print()
        
        # Teste 4: Funcionalidades avançadas
        print("\n⚡ Teste 4: Funcionalidades Avançadas")
        print("-" * 40)
        
        # Testar análise de prompt
        test_prompt = "Preciso navegar na web, acessar arquivos e trabalhar com banco de dados"
        print(f"Prompt de teste: '{test_prompt}'")
        
        suggested_mcps = mcp_manager.analyze_prompt_for_mcps(test_prompt)
        print(f"MCPs sugeridos: {suggested_mcps}")
        
        # Testar gerenciamento automático
        print("\nExecutando gerenciamento automático...")
        results = mcp_manager.auto_manage_mcps(test_prompt)
        
        print(f"Resultados:")
        print(f"  Sugeridos: {results['suggested_mcps']}")
        print(f"  Iniciados: {results['started']}")
        print(f"  Parados: {results['stopped']}")
        if results['errors']:
            print(f"  Erros: {results['errors']}")
        
        print("\n✅ Todos os testes concluídos com sucesso!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("Certifique-se de que o mcp_manager.py está no mesmo diretório")
        return False
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        return False

def test_custom_installation():
    """Testa instalação de MCP customizado"""
    
    print("\n🔧 Teste de Instalação Customizada")
    print("=" * 60)
    
    try:
        from mcp_manager import MCPManager
        
        mcp_manager = MCPManager()
        
        # Teste com um repositório GitHub conhecido
        test_repo = "https://github.com/modelcontextprotocol/server-filesystem"
        
        print(f"Testando instalação de: {test_repo}")
        
        success = mcp_manager.install_custom_mcp(
            mcp_name="test-filesystem",
            github_url=test_repo
        )
        
        if success:
            print("✅ Instalação customizada bem-sucedida")
            
            # Verificar se foi adicionado à lista
            if "test-filesystem" in mcp_manager.mcps:
                mcp = mcp_manager.mcps["test-filesystem"]
                print(f"  Nome: {mcp.name}")
                print(f"  Porta: {mcp.port}")
                print(f"  Método: {mcp.installation_method}")
                print(f"  GitHub: {mcp.github_url}")
            else:
                print("❌ MCP não foi adicionado à lista")
        else:
            print("❌ Falha na instalação customizada")
        
        return success
        
    except Exception as e:
        print(f"❌ Erro no teste customizado: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 Teste Completo do Sistema MCP com GitHub")
    print("=" * 60)
    
    # Verificar dependências
    print("Verificando dependências...")
    
    try:
        import requests
        print("✅ requests instalado")
    except ImportError:
        print("❌ requests não instalado")
        print("Execute: pip install requests")
        return
    
    try:
        import subprocess
        result = subprocess.run("npm --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm encontrado: v{result.stdout.strip()}")
        else:
            print("❌ npm não encontrado")
            return
    except Exception as e:
        print(f"❌ Erro ao verificar npm: {e}")
        return
    
    try:
        import subprocess
        result = subprocess.run("git --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ git encontrado: {result.stdout.strip()}")
        else:
            print("❌ git não encontrado")
            return
    except Exception as e:
        print(f"❌ Erro ao verificar git: {e}")
        return
    
    print("\n" + "=" * 60)
    
    # Executar testes
    success1 = test_github_installation()
    success2 = test_custom_installation()
    
    print("\n" + "=" * 60)
    print("📋 Resumo dos Testes:")
    print(f"  Teste GitHub: {'✅ Passou' if success1 else '❌ Falhou'}")
    print(f"  Teste Customizado: {'✅ Passou' if success2 else '❌ Falhou'}")
    
    if success1 and success2:
        print("\n🎉 Todos os testes passaram! O módulo está funcionando corretamente.")
        print("\n💡 Funcionalidades disponíveis:")
        print("  • Instalação automática via npm")
        print("  • Fallback para GitHub quando npm falha")
        print("  • Busca inteligente de MCPs no GitHub")
        print("  • Instalação de MCPs customizados")
        print("  • Análise de prompts para sugerir MCPs")
        print("  • Gerenciamento automático de sessões")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique as dependências e configurações.")

if __name__ == "__main__":
    main() 