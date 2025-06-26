#!/usr/bin/env python3
"""
Script para iniciar o MCP Manager com integração com o modelo MCP.
Isso facilita a execução e fornece uma camada de abstração.
"""

import sys
import os
import platform

# Verificar se as dependências estão instaladas
try:
    from PyQt5.QtWidgets import QApplication
    import speech_recognition as sr
    import pyttsx3
except ImportError as e:
    print(f"Erro ao importar dependências: {e}")
    print("\nAlgumas dependências podem estar faltando. Instale-as com:")
    print("pip install -r requirements_mcp.txt")
    
    # Se a falha for apenas no reconhecimento de voz, continuar sem ele
    if "speech_recognition" in str(e) or "pyttsx3" in str(e):
        print("\nFuncionalidade de voz não estará disponível, mas o aplicativo continuará funcionando.")
    else:
        sys.exit(1)

# Importar nossos módulos
try:
    from mcp_manager_prototype import MCPManagerApp
    from mcp_model import MCPManager, MCP, BrowserAgentMCP
except ImportError as e:
    print(f"Erro ao importar módulos do MCP Manager: {e}")
    print("\nVerifique se os arquivos mcp_manager_prototype.py e mcp_model.py estão no mesmo diretório.")
    sys.exit(1)

def create_icons_if_needed():
    """Cria ícones de microfone se eles não existirem"""
    # Ícone de microfone ativado (simples)
    if not os.path.exists("mic_on.png"):
        with open("mic_on.png", "w") as f:
            f.write("Placeholder para ícone de microfone ativo")
    
    # Ícone de microfone desativado (simples)
    if not os.path.exists("mic_off.png"):
        with open("mic_off.png", "w") as f:
            f.write("Placeholder para ícone de microfone inativo")

def check_cursor_installation():
    """Verifica se o Cursor está instalado e localiza o arquivo mcp.json"""
    mcp_manager = MCPManager()
    
    if mcp_manager.cursor_path:
        print(f"Instalação do Cursor encontrada em: {mcp_manager.cursor_path}")
        
        if mcp_manager.mcp_json_path:
            print(f"Arquivo mcp.json encontrado em: {mcp_manager.mcp_json_path}")
        else:
            print("Arquivo mcp.json não encontrado.")
    else:
        print("Instalação do Cursor não detectada.")
    
    return mcp_manager

def main():
    """Função principal para iniciar o aplicativo"""
    print("Iniciando MCP Manager...")
    
    # Verificar sistema operacional
    system_name = platform.system()
    print(f"Sistema operacional: {system_name} {platform.version()}")
    
    # Criar ícones se necessário
    create_icons_if_needed()
    
    # Verificar instalação do Cursor
    mcp_manager = check_cursor_installation()
    
    # Criar aplicativo Qt
    app = QApplication(sys.argv)
    
    # Configurar estilo da aplicação
    app.setStyle("Fusion")
    
    # Iniciar janela principal
    window = MCPManagerApp()
    
    # Fornecer o gerenciador MCP para a janela (em uma implementação real)
    # window.set_mcp_manager(mcp_manager)
    
    # Mostrar janela
    window.show()
    
    # Executar loop de evento
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main()) 