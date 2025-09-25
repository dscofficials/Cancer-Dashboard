@echo off
echo  Cancer Dashboard - Environment Setup
echo 
echo.

echo [1/4] Setting up Python virtual environment...
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process"
python -m venv cancer
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call cancer\Scripts\activate
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo [3/4] Upgrading pip...
pip install --upgrade pip

echo [4/4] Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

echo.
echo 
echo  Setup Complete Successfully!
echo 