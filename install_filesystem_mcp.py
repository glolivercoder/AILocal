#!/usr/bin/env python3
"""
Script para instalar o MCP Filesystem no Cursor para o projeto atual
"""

import os
import sys
from cursor_mcp_manager import CursorMCPManager

def main():
    print("🚀 Instalando MCP Filesystem para o projeto AILocal")
    print("=" * 60)
    
    # Inicializar o gerenciador
    manager = CursorMCPManager()
    
    # Obter informações do Cursor
    info = manager.get_cursor_info()
    print(f"Sistema: {info['system']}")
    print(f"Arquivo MCP: {info['cursor_mcp_file']}")
    print(f"MCP existe: {info['cursor_mcp_exists']}")
    
    # Diretório do projeto atual
    project_path = os.getcwd()
    print(f"\n📁 Diretório do projeto: {project_path}")
    
    # Instalar MCP filesystem
    print("\n📦 Instalando MCP Filesystem...")
    success, message = manager.install_filesystem_mcp_for_project(project_path)
    
    if success:
        print(f"✅ {message}")
        
        # Mostrar configuração atual
        config, error = manager.read_cursor_mcp_config()
        if config:
            print("\n📄 Configuração do mcp.json:")
            print("-" * 40)
            import json
            print(json.dumps(config, indent=2, ensure_ascii=False))
            print("-" * 40)
            
            # Instruções para o usuário
            print("\n📋 Próximos passos:")
            print("1. Reinicie o Cursor para carregar a nova configuração")
            print("2. Abra o chat do Cursor e verifique se o MCP filesystem está disponível")
            print("3. Teste com comandos como: 'Liste os arquivos do projeto'")
            print("\n🎯 O MCP filesystem agora tem acesso ao diretório:")
            print(f"   {project_path}")
        else:
            print(f"⚠️ Erro ao ler configuração: {error}")
    else:
        print(f"❌ {message}")
        return 1
    
    print("\n✅ Instalação concluída!")
    return 0

if __name__ == "__main__":
    sys.exit(main())