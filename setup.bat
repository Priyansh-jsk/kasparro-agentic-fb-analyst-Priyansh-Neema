@echo off
REM Setup script for Windows

echo Setting up Kasparro Agentic FB Analyst...

REM Create directory structure
echo Creating directory structure...
mkdir data
mkdir reports
mkdir logs

REM Check Python version
echo Checking Python version...
python --version

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Verify installation
echo Verifying installation...
python -c "import pandas, numpy, sklearn, yaml; print('All dependencies installed successfully!')"

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Copy your CSV file to data\synthetic_fb_ads_undergarments.csv
echo 2. Activate the virtual environment: .venv\Scripts\activate.bat
echo 3. Run analysis: python run.py "Your query here"
echo.

pause