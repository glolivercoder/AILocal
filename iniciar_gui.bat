@echo off
echo ============================================================
echo   INICIANDO AI AGENT GUI
echo ============================================================
echo.

cd /d "%~dp0"

echo Verificando Python...
python --version
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo Instale o Python 3.8+ e tente novamente.
    pause
    exit /b 1
)

echo.
echo 🚀 Iniciando interface gráfica...
echo.

python iniciar_gui.py

if errorlevel 1 (
    echo.
    echo ❌ Erro ao iniciar a GUI!
    echo Verifique os logs acima para mais detalhes.
    pause
)