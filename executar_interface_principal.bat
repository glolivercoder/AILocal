@echo off
chcp 65001 >nul
echo ========================================
echo    AGENTE ESPECIALISTA EM DESENVOLVIMENTO
echo    Sistema RAG Integrado - Interface Principal
echo ========================================
echo.
echo Iniciando interface principal...
echo.

REM Tentar executar a interface principal
if exist "ai_agent_gui.py" (
    echo Executando ai_agent_gui.py...
    python ai_agent_gui.py
    if %ERRORLEVEL% EQU 0 (
        echo Interface executada com sucesso!
        goto :end
    )
)

if exist "integrated_knowledge_interface.py" (
    echo Tentando integrated_knowledge_interface.py...
    python integrated_knowledge_interface.py
    if %ERRORLEVEL% EQU 0 (
        echo Interface executada com sucesso!
        goto :end
    )
)

if exist "start_main_interface.py" (
    echo Tentando start_main_interface.py...
    python start_main_interface.py
    if %ERRORLEVEL% EQU 0 (
        echo Interface executada com sucesso!
        goto :end
    )
)

echo.
echo ❌ Erro: Nenhuma interface pôde ser executada
echo.
echo Interfaces disponíveis:
if exist "ai_agent_gui.py" echo - ai_agent_gui.py
if exist "integrated_knowledge_interface.py" echo - integrated_knowledge_interface.py
if exist "start_main_interface.py" echo - start_main_interface.py
echo.
echo Tente executar manualmente:
echo python ai_agent_gui.py
echo.

:end
echo.
echo Pressione qualquer tecla para sair...
pause >nul