# 🚀 Módulos Isolados - AILocalIniciar

## 📁 Estrutura de Pastas

```
AILocalIniciar/
├── google_drive/              # Módulo do Google Drive
│   ├── google_service_account.py
│   ├── testar_google_service.py
│   └── service_account_credentials.json
│
├── backup/                    # Módulo de Backup
│   ├── backup_manager.py
│   ├── backup_tab.py
│   └── requirements_backup.txt
│
├── config/                    # Configurações
│   ├── config_env.py
│   └── config_manager.py
│
└── utils/                     # Utilitários
    └── requirements.txt
```

## 🔧 Como Usar

Cada módulo pode ser executado isoladamente:

### Google Drive
```bash
cd google_drive
python testar_google_service.py
```

### Backup
```bash
cd backup
python backup_manager.py
```

### Configuração
```bash
cd config
python config_env.py
```

## 📋 Requisitos

1. Instale os requisitos base:
```bash
pip install -r utils/requirements.txt
```

2. Para módulos específicos, instale seus requisitos:
```bash
pip install -r backup/requirements_backup.txt
```

## ⚙️ Configuração

1. Coloque suas credenciais do Google em `google_drive/service_account_credentials.json`
2. Configure variáveis de ambiente em `config/config_env.py`
3. Ajuste configurações específicas em cada módulo conforme necessário

## 🔍 Testes

Cada módulo possui seu próprio script de teste que pode ser executado isoladamente. 