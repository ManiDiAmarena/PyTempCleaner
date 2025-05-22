@echo off
REM Richiede i privilegi di amministratore
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Richiesta dei privilegi di amministratore in corso...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    REM Modificato per passare il nome corretto dello script batch
    echo UAC.ShellExecute "%~f0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    REM Cambia la directory corrente alla directory dello script batch
    cd /d "%~dp0"

    REM Esegui qui il tuo script Python
    REM Assicurati che 'python' sia nel tuo PATH o fornisci il percorso completo a python.exe
    REM 'main.py' dovrebbe essere ora trovato correttamente
    echo Avvio dello script Python ('main.py') con privilegi di amministratore dalla directory:
    echo %CD%
    python main.py
    
    echo.
    echo Esecuzione dello script terminata. Premere un tasto per chiudere.
    pause >nul
    exit /B