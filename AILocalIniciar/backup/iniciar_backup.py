#!/usr/bin/env python3
"""
Interface principal do sistema de backup
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from backup_tab import BackupTab

def main():
    """Função principal que inicia a aplicação"""
    app = QApplication(sys.argv)
    
    # Criar janela principal
    window = QMainWindow()
    window.setWindowTitle("Sistema de Backup")
    window.setGeometry(100, 100, 1200, 800)
    
    # Criar widget de abas
    tabs = QTabWidget()
    
    # Adicionar aba de backup
    backup_tab = BackupTab()
    tabs.addTab(backup_tab, "Backup")
    
    # Definir abas como widget central
    window.setCentralWidget(tabs)
    
    # Mostrar janela
    window.show()
    
    # Executar aplicação
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 