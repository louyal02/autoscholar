@echo off
cd /d "%~dp0"
git add -A
git commit -m "Update: 优化代码结构，添加定时任务支持"
git push origin master
pause
