#!/usr/bin/env python3
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
        print("
🎉 Todas as dependências estão disponíveis!")
    else:
        print("
⚠️  Algumas dependências falharam. Verifique manualmente.")
    
    return all_ok

if __name__ == "__main__":
    main()
