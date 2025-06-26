"""
Sistema de backup com suporte a Google Drive e criptografia.

Este pacote fornece funcionalidades para:
- Criar backups locais
- Fazer upload para o Google Drive
- Criptografar backups com senha
- Enviar relatórios por email
"""

__version__ = "1.0.0"

from .backup_manager import BackupManager
from .backup_tab import BackupTab

__all__ = ['BackupManager', 'BackupTab'] 