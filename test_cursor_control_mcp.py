#!/usr/bin/env python3
"""
Script de Teste - Cursor Control MCP Server
Demonstra todas as funcionalidades do servidor MCP

Execute este script para testar as capacidades do sistema:
- Controle de terminal
- Gerenciamento de prompts
- Controle de conversas
- Manipulação de arquivos
- Status e configuração
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Importar o servidor MCP
try:
    from cursor_control_mcp_server import CursorControlMCPServer
except ImportError:
    print("❌ Erro: cursor_control_mcp_server.py não encontrado")
    print("Execute primeiro: python install_cursor_control_mcp.py")
    sys.exit(1)

class MCPTester:
    def __init__(self):
        self.server = CursorControlMCPServer()
        self.test_results = []
    
    async def run_test(self, test_name: str, tool_name: str, arguments: dict):
        """Executa um teste e registra o resultado"""
        print(f"\n🧪 Testando: {test_name}")
        print(f"🔧 Ferramenta: {tool_name}")
        print(f"📋 Argumentos: {json.dumps(arguments, indent=2)}")
        
        try:
            result = await self.server.call_tool(tool_name, arguments)
            
            if result and result.content:
                output = result.content[0].text
                print(f"✅ Resultado:")
                print(output[:500] + "..." if len(output) > 500 else output)
                
                self.test_results.append({
                    "test": test_name,
                    "tool": tool_name,
                    "status": "success",
                    "output": output[:200]
                })
            else:
                print("❌ Sem resultado")
                self.test_results.append({
                    "test": test_name,
                    "tool": tool_name,
                    "status": "no_result",
                    "output": ""
                })
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            self.test_results.append({
                "test": test_name,
                "tool": tool_name,
                "status": "error",
                "output": str(e)
            })
    
    async def test_terminal_control(self):
        """Testa controle de terminal"""
        print("\n" + "="*60)
        print("🖥️  TESTANDO CONTROLE DE TERMINAL")
        print("="*60)
        
        # Teste 1: Comando simples
        await self.run_test(
            "Comando Python Version",
            "execute_terminal_command",
            {"command": "python --version"}
        )
        
        # Teste 2: Comando com diretório
        await self.run_test(
            "Listar arquivos do projeto",
            "execute_terminal_command",
            {
                "command": "dir" if os.name == 'nt' else "ls -la",
                "working_directory": os.getcwd()
            }
        )
        
        # Teste 3: Criar sessão de terminal
        await self.run_test(
            "Criar sessão de terminal",
            "create_terminal_session",
            {
                "session_name": "test_session",
                "working_directory": os.getcwd()
            }
        )
        
        # Teste 4: Listar sessões
        await self.run_test(
            "Listar sessões de terminal",
            "list_terminal_sessions",
            {}
        )
    
    async def test_prompt_management(self):
        """Testa gerenciamento de prompts"""
        print("\n" + "="*60)
        print("💬 TESTANDO GERENCIAMENTO DE PROMPTS")
        print("="*60)
        
        # Teste 1: Salvar prompt
        await self.run_test(
            "Salvar prompt de análise",
            "save_prompt",
            {
                "title": "Análise de Performance",
                "content": "Analise o código em {file_path} e sugira otimizações de performance específicas.",
                "category": "code-review",
                "tags": "performance, análise, otimização"
            }
        )
        
        # Teste 2: Salvar outro prompt
        await self.run_test(
            "Salvar prompt de documentação",
            "save_prompt",
            {
                "title": "Documentação de Função",
                "content": "Crie documentação detalhada para a função {function_name} incluindo docstring, exemplos e casos de uso.",
                "category": "documentation",
                "tags": "docs, função, exemplos"
            }
        )
        
        # Teste 3: Buscar prompts
        await self.run_test(
            "Buscar prompts por categoria",
            "search_prompts",
            {"category": "code-review"}
        )
        
        # Teste 4: Buscar prompts por tag
        await self.run_test(
            "Buscar prompts por tag",
            "search_prompts",
            {"tags": "performance"}
        )
    
    async def test_conversation_management(self):
        """Testa gerenciamento de conversas"""
        print("\n" + "="*60)
        print("🤖 TESTANDO GERENCIAMENTO DE CONVERSAS")
        print("="*60)
        
        # Teste 1: Iniciar conversa
        conversation_result = await self.server.call_tool(
            "start_conversation",
            {
                "title": "Teste de Integração MCP",
                "initial_message": "Olá! Este é um teste do sistema MCP de controle do Cursor.",
                "context": {"test_mode": True}
            }
        )
        
        # Extrair ID da conversa do resultado
        conversation_id = None
        if conversation_result and conversation_result.content:
            output = conversation_result.content[0].text
            if "ID:" in output:
                # Tentar extrair ID da conversa
                lines = output.split('\n')
                for line in lines:
                    if "ID:" in line:
                        conversation_id = line.split("ID:")[1].strip().rstrip(")")
                        break
        
        self.test_results.append({
            "test": "Iniciar conversa",
            "tool": "start_conversation",
            "status": "success" if conversation_id else "partial",
            "output": conversation_result.content[0].text[:200] if conversation_result.content else ""
        })
        
        print(f"✅ Conversa iniciada com ID: {conversation_id}")
        
        # Teste 2: Enviar mensagem
        if conversation_id:
            await self.run_test(
                "Enviar mensagem para conversa",
                "send_message_to_cursor",
                {
                    "message": "Como posso melhorar a performance do meu código Python?",
                    "conversation_id": conversation_id,
                    "mode": "chat"
                }
            )
            
            # Teste 3: Recuperar histórico
            await self.run_test(
                "Recuperar histórico da conversa",
                "get_conversation_history",
                {
                    "conversation_id": conversation_id,
                    "limit": 10
                }
            )
    
    async def test_file_control(self):
        """Testa controle de arquivos"""
        print("\n" + "="*60)
        print("📁 TESTANDO CONTROLE DE ARQUIVOS")
        print("="*60)
        
        # Teste 1: Criar arquivo de teste
        test_file = "test_mcp_file.py"
        test_content = '''#!/usr/bin/env python3
"""
Arquivo de teste criado pelo Cursor Control MCP
"""

def test_function():
    """Função de teste"""
    print("Hello from MCP created file!")
    return "success"

if __name__ == "__main__":
    test_function()
'''
        
        await self.run_test(
            "Criar arquivo de teste",
            "create_file_in_cursor",
            {
                "file_path": test_file,
                "content": test_content,
                "open_after_create": False
            }
        )
        
        # Teste 2: Tentar abrir arquivo (pode falhar se Cursor não estiver disponível)
        await self.run_test(
            "Abrir arquivo no Cursor",
            "open_file_in_cursor",
            {
                "file_path": test_file,
                "line_number": 10
            }
        )
    
    async def test_status_and_config(self):
        """Testa status e configuração"""
        print("\n" + "="*60)
        print("⚙️  TESTANDO STATUS E CONFIGURAÇÃO")
        print("="*60)
        
        # Teste 1: Status do Cursor
        await self.run_test(
            "Obter status do Cursor",
            "get_cursor_status",
            {}
        )
        
        # Teste 2: Backup de configuração
        await self.run_test(
            "Criar backup de configuração",
            "backup_cursor_config",
            {"backup_name": "test_backup"}
        )
        
        # Teste 3: Configurar novo MCP (teste)
        await self.run_test(
            "Configurar MCP de teste",
            "configure_cursor_mcp",
            {
                "server_name": "test-mcp",
                "command": "python",
                "args": ["-c", "print('Test MCP')"],
                "env": {"TEST_VAR": "test_value"}
            }
        )
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        print("🎯 CURSOR CONTROL MCP - SUITE DE TESTES")
        print("="*60)
        print("Testando todas as funcionalidades do servidor MCP...")
        
        # Executar todos os grupos de teste
        await self.test_terminal_control()
        await self.test_prompt_management()
        await self.test_conversation_management()
        await self.test_file_control()
        await self.test_status_and_config()
        
        # Resumo dos resultados
        self.show_test_summary()
    
    def show_test_summary(self):
        """Mostra resumo dos testes"""
        print("\n" + "="*60)
        print("📊 RESUMO DOS TESTES")
        print("="*60)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["status"] == "success"])
        failed_tests = len([r for r in self.test_results if r["status"] == "error"])
        partial_tests = len([r for r in self.test_results if r["status"] in ["no_result", "partial"]])
        
        print(f"📈 Total de testes: {total_tests}")
        print(f"✅ Sucessos: {successful_tests}")
        print(f"❌ Falhas: {failed_tests}")
        print(f"⚠️  Parciais: {partial_tests}")
        print(f"📊 Taxa de sucesso: {(successful_tests/total_tests)*100:.1f}%")
        
        # Detalhes dos testes falhados
        if failed_tests > 0:
            print(f"\n❌ TESTES FALHADOS:")
            for result in self.test_results:
                if result["status"] == "error":
                    print(f"  • {result['test']}: {result['output']}")
        
        # Salvar resultados em arquivo
        self.save_test_results()
        
        print(f"\n🎉 Testes concluídos! Resultados salvos em test_results.json")
    
    def save_test_results(self):
        """Salva resultados dos testes em arquivo"""
        try:
            results_file = Path(".cursor") / "test_results.json"
            results_file.parent.mkdir(exist_ok=True)
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": str(asyncio.get_event_loop().time()),
                    "total_tests": len(self.test_results),
                    "results": self.test_results
                }, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar resultados: {e}")

async def main():
    """Função principal"""
    print("🚀 Iniciando testes do Cursor Control MCP Server...")
    
    tester = MCPTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 