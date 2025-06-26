#!/usr/bin/env python3
"""
Script para iniciar a interface gráfica do AI Agent
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Importar e executar a GUI
    from ai_agent_gui import main
    print("🚀 Iniciando interface gráfica...")
    main()
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Verifique se todas as dependências estão instaladas.")
except Exception as e:
    print(f"❌ Erro ao iniciar a GUI: {e}")
    import traceback
    traceback.print_exc()