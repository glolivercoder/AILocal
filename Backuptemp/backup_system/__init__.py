"""
Sistema de backup com interface gráfica e compressão 7z.

Este módulo fornece uma interface gráfica para criar, gerenciar e restaurar
backups usando compressão 7z e integração opcional com Google Drive.

Classes principais:
    - BackupManager: Gerencia operações de backup e restauração
    - BackupTab: Interface gráfica em tkinter
    - BackupDatabase: Armazena metadados dos backups
"""

__version__ = "1.0.0"
__author__ = "AILocal"

from .backup_manager import BackupManager
from .backup_tab import BackupTab

__all__ = ['BackupManager', 'BackupTab'] 