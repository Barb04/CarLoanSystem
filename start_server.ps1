# Car Loan System - Production Server Startup
# Run this from the root directory

Write-Host "Starting Car Loan System Production Server..." -ForegroundColor Green

# Navigate to backend directory
Set-Location "C:\Users\otien\CarLoanSystem\backend"

# Set PYTHONPATH
$env:PYTHONPATH = "C:\Users\otien\CarLoanSystem\backend"

# Install requirements (if needed)
Write-Host "Ensuring requirements are installed..." -ForegroundColor Yellow
& "C:\Users\otien\CarLoanSystem\backend\venv\Scripts\python.exe" -m pip install waitress

# Collect static files
Write-Host "Collecting static files..." -ForegroundColor Yellow
& "C:\Users\otien\CarLoanSystem\backend\venv\Scripts\python.exe" manage.py collectstatic --noinput

# Start Waitress server
Write-Host "Starting Waitress server on http://0.0.0.0:8000" -ForegroundColor Green
& "C:\Users\otien\CarLoanSystem\backend\venv\Scripts\waitress-serve" --host=0.0.0.0 --port=8000 core.wsgi:application