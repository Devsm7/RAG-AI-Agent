@echo off
echo ============================================================
echo    Starting Twuaiq RAG Assistant Web Interface
echo    مساعد أكاديمية طويق - واجهة الويب
echo ============================================================
echo.
echo Opening web interface at http://localhost:7860
echo فتح واجهة الويب على http://localhost:7860
echo.
echo Press Ctrl+C to stop the server
echo اضغط Ctrl+C لإيقاف الخادم
echo ============================================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate
python app.py

pause
