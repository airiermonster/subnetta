@echo off
REM Subnetta Installation Script for Windows
REM This script installs Subnetta globally on your system

echo.
echo ================================================================
echo                 Subnetta Installer for Windows
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)

REM Display Python version
echo Detected Python version:
python --version
echo.

REM Check Python version (basic check)
echo Checking Python version compatibility...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.8 or higher is required
    echo Please upgrade your Python installation
    echo.
    pause
    exit /b 1
)

echo ✓ Python version is compatible
echo.

REM Install Subnetta
echo Installing Subnetta...
pip install -e .
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install Subnetta
    echo Please check your pip installation and try again
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo                 Installation Successful!
echo ================================================================
echo.
echo Subnetta has been installed successfully!
echo.
echo To run Subnetta, simply type 'subnetta' in any command prompt:
echo   subnetta
echo.
echo For help, use:
echo   subnetta --help
echo.
echo Happy subnetting! 🌐
echo.
pause