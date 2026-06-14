# Render 部署說明

本專案可部署至 Render Web Service，讓老師或同學不需要下載專案也能開啟線上展示網址。

## 推薦設定

- Service Type：Web Service
- Root Directory：留空
- Build Command：`pip install -r backend/requirements-render.txt`
- Start Command：`cd backend && gunicorn app:app --bind 0.0.0.0:$PORT`

本專案已包含 `render.yaml`，也可以直接讓 Render 依照 Blueprint 建立服務。

## 注意事項

Render 免費方案可能休眠，第一次開啟網址可能需要等待。
本專案使用本機 JSON 儲存，免費線上環境不適合作為永久資料庫；課堂展示請以本機 Flask 版本作為主要 DEMO，Render 作為線上展示輔助。
