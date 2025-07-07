@echo off
echo Activating virtual environment...
call venv312\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Starting Flask application...
python app.py

pause 