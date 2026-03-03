@echo off
REM LLM Paper Tracker 启动脚本

echo ========================================
echo   LLM Paper Tracker
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
echo Checking dependencies...
pip show openai >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM 解析命令行参数
if "%1"=="-r" goto run_now
if "%1"=="--run-now" goto run_now
if "%1"=="-s" goto setup_task
if "%1"=="--setup-task" goto setup_task
if "%1"=="-t" goto test_email
if "%1"=="--test-email" goto test_email

REM 默认运行
echo Starting LLM Paper Tracker...
echo Daily run time: 09:30
echo Press Ctrl+C to stop.
echo.
python -m llm_paper_tracker.main
pause
exit /b

:run_now
echo Running now...
python -m llm_paper_tracker.main --run-now
pause
exit /b

:setup_task
echo Setting up Windows scheduled task...
python -m llm_paper_tracker.main --setup-task
pause
exit /b

:test_email
echo Testing email configuration...
python -m llm_paper_tracker.main --test-email
pause
exit /b
