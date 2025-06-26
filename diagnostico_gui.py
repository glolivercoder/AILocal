#!/usr/bin/env python3
"""
Diagnóstico específico para problemas da GUI
"""

import sys
import os

def verificar_display():
    """Verifica se há problemas com display/GUI"""
    print("🔍 Verificando ambiente de display...")
    
    # Verificar variáveis de ambiente relacionadas ao display
    display_vars = ['DISPLAY', 'WAYLAND_DISPLAY', 'XDG_SESSION_TYPE']
    for var in display_vars:
        value = os.environ.get(var, 'Não definido')
        print(f"  {var}: {value}")
    
    # No Windows, verificar se estamos em um ambiente gráfico
    if sys.platform == 'win32':
        try:
            import ctypes
            user32 = ctypes.windll.user32
            if user32.GetSystemMetrics(0) > 0:  # SM_CXSCREEN
                print("  ✅ Ambiente gráfico Windows detectado")
                return True
            else:
                print("  ❌ Ambiente gráfico não detectado")
                return False
        except Exception as e:
            print(f"  ⚠️  Erro ao verificar ambiente gráfico: {e}")
            return False
    
    return True

def verificar_pyqt5():
    """Verifica se PyQt5 está funcionando"""
    print("\n🔍 Verificando PyQt5...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("  ✅ PyQt5.QtWidgets importado com sucesso")
        
        # Tentar criar uma aplicação QT (sem mostrar janela)
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
            print("  ✅ QApplication criada com sucesso")
            app.quit()
        else:
            print("  ✅ QApplication já existe")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro ao importar PyQt5: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro ao criar QApplication: {e}")
        return False

def verificar_dependencias_gui():
    """Verifica dependências específicas da GUI"""
    print("\n🔍 Verificando dependências da GUI...")
    
    dependencias = [
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets'
    ]
    
    sucesso = True
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"  ✅ {dep}")
        except ImportError as e:
            print(f"  ❌ {dep}: {e}")
            sucesso = False
    
    return sucesso

def teste_gui_minima():
    """Testa criação de uma GUI mínima"""
    print("\n🔍 Testando GUI mínima...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QLabel
        from PyQt5.QtCore import QTimer
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Criar uma janela simples que se fecha automaticamente
        label = QLabel("Teste GUI - Fechando em 2 segundos...")
        label.show()
        
        # Timer para fechar automaticamente
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(2000)  # 2 segundos
        
        print("  ✅ GUI mínima criada, executando por 2 segundos...")
        app.exec_()
        print("  ✅ GUI mínima executada com sucesso")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na GUI mínima: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("============================================================")
    print("   DIAGNÓSTICO DE PROBLEMAS DA GUI")
    print("============================================================")
    print(f"Python: {sys.version}")
    print(f"Plataforma: {sys.platform}")
    print(f"Diretório: {os.getcwd()}")
    
    # Executar verificações
    display_ok = verificar_display()
    pyqt5_ok = verificar_pyqt5()
    deps_ok = verificar_dependencias_gui()
    
    if display_ok and pyqt5_ok and deps_ok:
        gui_ok = teste_gui_minima()
    else:
        gui_ok = False
    
    print("\n============================================================")
    print("   RESUMO DO DIAGNÓSTICO")
    print("============================================================")
    print(f"Display/Ambiente Gráfico: {'✅' if display_ok else '❌'}")
    print(f"PyQt5 Básico: {'✅' if pyqt5_ok else '❌'}")
    print(f"Dependências GUI: {'✅' if deps_ok else '❌'}")
    print(f"Teste GUI Mínima: {'✅' if gui_ok else '❌'}")
    
    if all([display_ok, pyqt5_ok, deps_ok, gui_ok]):
        print("\n🎉 DIAGNÓSTICO: Ambiente GUI está funcionando!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Execute: python -c \"from ai_agent_gui import main; main()\"")
        print("2. Ou use: iniciar_gui.bat")
        print("3. Se ainda não funcionar, pode ser problema de timeout do terminal")
    else:
        print("\n❌ DIAGNÓSTICO: Problemas detectados no ambiente GUI")
        print("\n📋 SOLUÇÕES SUGERIDAS:")
        if not pyqt5_ok:
            print("- Reinstale PyQt5: pip install --upgrade PyQt5")
        if not display_ok:
            print("- Verifique se está em um ambiente gráfico")
            print("- No Windows, certifique-se de não estar em modo texto")
        if not deps_ok:
            print("- Reinstale todas as dependências GUI")

if __name__ == "__main__":
    main()