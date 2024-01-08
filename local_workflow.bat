@echo off
echo Running CodeCheck...

:: Print the current working directory
echo %CD%

:: Set the current directory to the directory of the batch file
cd /d %~dp0

:: Print the current working directory
echo %CD%

:: Set up Python
python -m pip install --upgrade pip
pip install wheel
pip install -r requirements.txt
pip install flake8
pip install pylint
pip install mypy
pip install -r mypy_stubs.txt

:: Lint with flake8
python -m flake8 . --count --show-source --statistics --max-line-length 82 --exit-zero

:: Lint with pylint
pylint *.py

:: Lint with mypy
mypy *.py

echo CodeCheck completed.

pause