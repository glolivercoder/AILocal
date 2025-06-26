# Sistema de Backup

Sistema de backup com interface gráfica e compressão 7z.

## Funcionalidades

- Compressão eficiente usando formato 7z
- Interface gráfica intuitiva
- Barra de progresso em tempo real
- Exclusão múltipla de backups com confirmação
- Exibição de velocidade e tempo estimado
- Armazenamento de metadados em SQLite

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

Execute o arquivo `iniciar_backup.py`:

```bash
python iniciar_backup.py
```

1. Clique em "Selecionar" para escolher o diretório
2. Clique em "Criar Backup" para iniciar
3. Acompanhe o progresso na barra inferior
4. Use as caixas de seleção para excluir backups antigos

## Dependências

- py7zr>=0.20.5 - Compressão 7z
- humanize>=4.7.0 - Formatação de tamanhos
- tkinter - Interface gráfica (built-in)
- sqlite3 - Banco de dados (built-in) 