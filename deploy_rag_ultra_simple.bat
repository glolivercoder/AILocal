@echo off
echo ========================================
echo Deploy do Sistema RAG Ultra-Simplificado
echo ========================================
echo.

echo 1. Fazendo backup do sistema atual...
python backup_rag_modern.py
if errorlevel 1 (
    echo Erro no backup, mas continuando...
)

echo.
echo 2. Adicionando arquivos ao Git...
git add .
if errorlevel 1 (
    echo Erro no git add, mas continuando...
)

echo.
echo 3. Fazendo commit...
git commit -m "Backup e implementacao do sistema RAG ultra-simplificado funcional"
if errorlevel 1 (
    echo Erro no commit, mas continuando...
)

echo.
echo 4. Fazendo push para repositorio...
git push
if errorlevel 1 (
    echo Erro no push, mas continuando...
)

echo.
echo 5. Criando backup do sistema funcional atual...
copy rag_system_functional.py rag_system_functional_backup.py
if errorlevel 1 (
    echo Erro no backup do funcional, mas continuando...
)

echo.
echo 6. Substituindo sistema funcional pelo ultra-simplificado...
copy rag_ultra_simple.py rag_system_functional.py
if errorlevel 1 (
    echo Erro na substituicao!
    goto :error
)

echo.
echo 7. Testando novo sistema...
python rag_system_functional.py
if errorlevel 1 (
    echo Erro no teste, restaurando backup...
    copy rag_system_functional_backup.py rag_system_functional.py
    goto :error
)

echo.
echo ========================================
echo ✅ Deploy concluido com sucesso!
echo ========================================
echo.
echo O sistema RAG ultra-simplificado foi implantado!
echo Arquivo: rag_system_functional.py
echo Backup: rag_system_functional_backup.py
echo.
goto :end

:error
echo.
echo ========================================
echo ❌ Erro no deploy!
echo ========================================
echo.
echo Verifique os logs acima para detalhes.
echo.

:end
pause