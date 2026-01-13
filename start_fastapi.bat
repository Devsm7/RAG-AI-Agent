@echo off
echo ========================================
echo   Twuaiq RAG Assistant - FastAPI Server
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
    echo Please create one with: python -m venv .venv
    echo.
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo.
    echo Installing required dependencies...
    pip install -r requirements.txt
    echo.
)

REM Start the FastAPI server
echo.
echo Starting FastAPI server...
echo.
python fastapi_app.py

pause
