#!/usr/bin/env python3
"""
Script para iniciar a interface de backup
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from backup_tab import BackupTab

class BackupWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Backup - AILocalIniciar")
        self.setGeometry(100, 100, 800, 600)
        
        # Criar e definir a aba de backup como widget central
        self.backup_tab = BackupTab()
        self.setCentralWidget(self.backup_tab)

def main():
    app = QApplication(sys.argv)
    window = BackupWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 