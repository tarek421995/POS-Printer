@echo off
SETLOCAL

:: Check for Python and exit if not installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python and rerun this installer.
    exit /b
)

:: Create a virtual environment
python -m venv myenv
call myenv\Scripts\activate

:: Install requirements
pip install -r requirements.txt

:: Run migrations
python manage.py migrate

:: Start the server
python manage.py runserver 0.0.0.0:8000

ENDLOCAL
