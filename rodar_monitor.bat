@echo off
cd /d "%~dp0"
venv\Scripts\python.exe main.py >> log_execucao.txt 2>&1
