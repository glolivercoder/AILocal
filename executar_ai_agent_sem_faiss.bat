@echo off
echo Iniciando AI Agent GUI sem FAISS...
set DISABLE_FAISS=true
set PYTHONUNBUFFERED=1
python ai_agent_gui.py
pause
