@echo off
echo ========================================
echo    BACKUP DO AGENTE ESPECIALISTA
echo ========================================
echo.

REM Criar diretório de backup com timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

set "backup_dir=backup_agente_%timestamp%"
mkdir "%backup_dir%"

echo Criando backup em: %backup_dir%
echo.

REM Copiar arquivos principais
echo Copiando arquivos principais...
if exist "ai_agent_gui.py" copy "ai_agent_gui.py" "%backup_dir%\" >nul
if exist "integrated_knowledge_interface.py" copy "integrated_knowledge_interface.py" "%backup_dir%\" >nul
if exist "prompt_manager_gui.py" copy "prompt_manager_gui.py" "%backup_dir%\" >nul
if exist "app.py" copy "app.py" "%backup_dir%\" >nul
if exist "start_main_interface.py" copy "start_main_interface.py" "%backup_dir%\" >nul
if exist "rag_system_functional.py" copy "rag_system_functional.py" "%backup_dir%\" >nul
if exist "config_manager.py" copy "config_manager.py" "%backup_dir%\" >nul
if exist "mcp_manager.py" copy "mcp_manager.py" "%backup_dir%\" >nul
if exist "requirements.txt" copy "requirements.txt" "%backup_dir%\" >nul
if exist "README.md" copy "README.md" "%backup_dir%\" >nul
if exist "RECURSOS_PRINCIPAIS_AGENTE.md" copy "RECURSOS_PRINCIPAIS_AGENTE.md" "%backup_dir%\" >nul
if exist "CHECKLIST_DESENVOLVIMENTO.md" copy "CHECKLIST_DESENVOLVIMENTO.md" "%backup_dir%\" >nul
if exist "backup_agente_especialista.py" copy "backup_agente_especialista.py" "%backup_dir%\" >nul

REM Copiar diretórios importantes
echo Copiando diretórios...
if exist "static" xcopy "static" "%backup_dir%\static\" /E /I /Q >nul
if exist "templates" xcopy "templates" "%backup_dir%\templates\" /E /I /Q >nul
if exist "config" xcopy "config" "%backup_dir%\config\" /E /I /Q >nul
if exist "rag_data" xcopy "rag_data" "%backup_dir%\rag_data\" /E /I /Q >nul

REM Criar arquivo de informações do backup
echo Criando arquivo de informações...
echo BACKUP DO AGENTE ESPECIALISTA EM DESENVOLVIMENTO DE APPS > "%backup_dir%\BACKUP_INFO.txt"
echo. >> "%backup_dir%\BACKUP_INFO.txt"
echo Data/Hora: %date% %time% >> "%backup_dir%\BACKUP_INFO.txt"
echo Timestamp: %timestamp% >> "%backup_dir%\BACKUP_INFO.txt"
echo. >> "%backup_dir%\BACKUP_INFO.txt"
echo ARQUIVOS INCLUIDOS: >> "%backup_dir%\BACKUP_INFO.txt"
echo - ai_agent_gui.py >> "%backup_dir%\BACKUP_INFO.txt"
echo - integrated_knowledge_interface.py >> "%backup_dir%\BACKUP_INFO.txt"
echo - prompt_manager_gui.py >> "%backup_dir%\BACKUP_INFO.txt"
echo - app.py >> "%backup_dir%\BACKUP_INFO.txt"
echo - start_main_interface.py >> "%backup_dir%\BACKUP_INFO.txt"
echo - rag_system_functional.py >> "%backup_dir%\BACKUP_INFO.txt"
echo - config_manager.py >> "%backup_dir%\BACKUP_INFO.txt"
echo - mcp_manager.py >> "%backup_dir%\BACKUP_INFO.txt"
echo - requirements.txt >> "%backup_dir%\BACKUP_INFO.txt"
echo - README.md >> "%backup_dir%\BACKUP_INFO.txt"
echo - RECURSOS_PRINCIPAIS_AGENTE.md >> "%backup_dir%\BACKUP_INFO.txt"
echo - CHECKLIST_DESENVOLVIMENTO.md >> "%backup_dir%\BACKUP_INFO.txt"
echo - backup_agente_especialista.py >> "%backup_dir%\BACKUP_INFO.txt"
echo. >> "%backup_dir%\BACKUP_INFO.txt"
echo DIRETORIOS INCLUIDOS: >> "%backup_dir%\BACKUP_INFO.txt"
echo - static/ >> "%backup_dir%\BACKUP_INFO.txt"
echo - templates/ >> "%backup_dir%\BACKUP_INFO.txt"
echo - config/ >> "%backup_dir%\BACKUP_INFO.txt"
echo - rag_data/ >> "%backup_dir%\BACKUP_INFO.txt"

echo.
echo ========================================
echo         BACKUP CONCLUIDO!
echo ========================================
echo.
echo Backup criado em: %backup_dir%
echo.
echo Para restaurar, copie os arquivos de volta para o diretorio principal.
echo.
pause