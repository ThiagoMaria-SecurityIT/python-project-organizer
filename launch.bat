@echo off
title Python Project Organizer
echo ========================================
echo    Python Project Organizer Launcher
echo ========================================
echo.

if not exist "venv" (
    echo Setting up environment for first time...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install streamlit pandas plotly
) else (
    call venv\Scripts\activate.bat
)

echo Starting application...
echo.
echo The app will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run optimized_project_organizer.py

pause
