@echo off
cd /d "%~dp0"
git add .
git commit -m "LLM Paper Tracker"
git push -u origin master
pause
