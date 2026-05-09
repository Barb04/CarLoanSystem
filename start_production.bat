@echo off
REM Car Loan System - Production Startup Script
REM This script sets up and runs the Django application with Waitress

echo Starting Car Loan System...

REM Navigate to backend directory
cd C:\Users\otien\CarLoanSystem\backend

REM Set PYTHONPATH for Django
set PYTHONPATH=C:\Users\otien\CarLoanSystem\backend

REM Install/update requirements
echo Installing requirements...
C:\Users\otien\CarLoanSystem\backend\venv\Scripts\python.exe -m pip install -r requirements.txt

REM Run database migrations
echo Running migrations...
C:\Users\otien\CarLoanSystem\backend\venv\Scripts\python.exe manage.py migrate

REM Collect static files
echo Collecting static files...
C:\Users\otien\CarLoanSystem\backend\venv\Scripts\python.exe manage.py collectstatic --noinput

REM Start Waitress server
echo Starting production server...
C:\Users\otien\CarLoanSystem\backend\venv\Scripts\waitress-serve --host=0.0.0.0 --port=8000 core.wsgi:application

pause