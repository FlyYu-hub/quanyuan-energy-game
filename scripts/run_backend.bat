@echo off
cd /d %~dp0\..\backend
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate
if exist wheelhouse (
  echo 使用本機離線套件 wheelhouse 安裝後端需求...
  pip install --no-index --find-links=wheelhouse -r requirements.txt
) else (
  echo 未偵測到 wheelhouse，改用網路安裝後端需求...
  pip install -r requirements.txt
)
python app.py
pause
