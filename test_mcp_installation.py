#!/usr/bin/env python3
"""
Script para testar instalação de MCPs disponíveis no npm
"""

import subprocess
import sys
import time
import json
from pathlib import Path

def run_command(command, timeout=30):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def check_npm_package(package_name):
    """Verifica se um pacote existe no npm"""
    command = f"npm view {package_name} --json"
    success, stdout, stderr = run_command(command)
    
    if success and stdout.strip():
        try:
            package_info = json.loads(stdout)
            return True, package_info
        except json.JSONDecodeError:
            return False, None
    return False, None

def test_mcp_installation():
    """Testa a instalação dos MCPs principais"""
    
    # Lista dos MCPs principais para testar
    mcps_to_test = [
        "@modelcontextprotocol/server-filesystem",
        "@modelcontextprotocol/server-postgres", 
        "@modelcontextprotocol/server-brave-search",
        "@modelcontextprotocol/server-puppeteer",
        "@modelcontextprotocol/server-slack",
        "@modelcontextprotocol/server-github",
        "@modelcontextprotocol/server-memory",
        "@modelcontextprotocol/server-redis",
        "@modelcontextprotocol/server-google-maps",
        "@modelcontextprotocol/server-sequential-thinking",
        "@modelcontextprotocol/server-everything",
        "@modelcontextprotocol/server-ollama",
        "@agentdeskai/browser-tools-server"
    ]
    
    print("🔍 Testando disponibilidade de MCPs no npm...")
    print("=" * 60)
    
    available_mcps = []
    unavailable_mcps = []
    
    for package in mcps_to_test:
        print(f"Verificando: {package}")
        exists, info = check_npm_package(package)
        
        if exists:
            version = info.get('version', 'N/A') if info else 'N/A'
            description = info.get('description', 'Sem descrição') if info else 'Sem descrição'
            print(f"  ✅ Disponível - v{version}")
            print(f"     {description}")
            available_mcps.append(package)
        else:
            print(f"  ❌ Não encontrado")
            unavailable_mcps.append(package)
        
        print()
    
    print("=" * 60)
    print(f"📊 Resumo:")
    print(f"   MCPs disponíveis: {len(available_mcps)}")
    print(f"   MCPs não encontrados: {len(unavailable_mcps)}")
    
    if available_mcps:
        print(f"\n✅ MCPs disponíveis para instalação:")
        for mcp in available_mcps:
            print(f"   - {mcp}")
    
    if unavailable_mcps:
        print(f"\n❌ MCPs não encontrados:")
        for mcp in unavailable_mcps:
            print(f"   - {mcp}")
    
    return available_mcps, unavailable_mcps

def test_mcp_execution(mcp_package, port=3333):
    """Testa a execução de um MCP específico"""
    print(f"\n🧪 Testando execução do {mcp_package}...")
    
    # Comando para executar o MCP
    command = f"npx {mcp_package}@latest --port {port}"
    
    print(f"Comando: {command}")
    
    try:
        # Inicia o processo
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguarda um pouco para ver se inicia
        time.sleep(5)
        
        # Verifica se o processo ainda está rodando
        if process.poll() is None:
            print(f"  ✅ MCP iniciado com sucesso na porta {port}")
            
            # Para o processo
            process.terminate()
            process.wait(timeout=5)
            print(f"  ✅ MCP parado com sucesso")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"  ❌ MCP falhou ao iniciar")
            print(f"     Erro: {stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro ao testar MCP: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Teste de Instalação de MCPs")
    print("=" * 60)
    
    # Verifica se npm está instalado
    success, stdout, stderr = run_command("npm --version")
    if not success:
        print("❌ npm não está instalado ou não está no PATH")
        return
    
    npm_version = stdout.strip()
    print(f"✅ npm encontrado: v{npm_version}")
    
    # Testa disponibilidade dos MCPs
    available_mcps, unavailable_mcps = test_mcp_installation()
    
    if not available_mcps:
        print("\n❌ Nenhum MCP disponível para teste")
        return
    
    # Pergunta se quer testar execução
    print(f"\n🤔 Deseja testar a execução dos MCPs disponíveis? (s/n): ", end="")
    
    try:
        response = input().lower().strip()
        if response in ['s', 'sim', 'y', 'yes']:
            print("\n🧪 Iniciando testes de execução...")
            
            # Testa apenas os primeiros 3 MCPs para não sobrecarregar
            test_mcps = available_mcps[:3]
            
            for i, mcp in enumerate(test_mcps):
                port = 3333 + i
                success = test_mcp_execution(mcp, port)
                
                if success:
                    print(f"  ✅ {mcp} - FUNCIONANDO")
                else:
                    print(f"  ❌ {mcp} - FALHOU")
                
                print()
        else:
            print("Teste de execução pulado.")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Teste interrompido pelo usuário")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    main() 