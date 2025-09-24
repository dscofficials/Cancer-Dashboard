@echo off
echo 

echo Setting up the environment...
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process"
python -m venv cancer
call cancer/Scripts/activate

echo 
echo Installing required packages...
pip install --upgrade pip
pip install -r requirements.txt

echo 
echo Setup complete

echo To run the app.py
echo      streamlit run app.py