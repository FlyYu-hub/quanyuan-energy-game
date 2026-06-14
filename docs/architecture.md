# 系統架構圖文字版

```text
使用者 / 老師 DEMO
        ↓
瀏覽器 Web App
        ↓
Vue 3 + Vite 前端
- 首頁 Dashboard
- 能源圖鑑
- 翻牌配對
- 問答闖關
- 學習成果
- 排行榜
- 後端測試面板
        ↓ Fetch API / HTTP Request
Flask 後端 API
- /api/health
- /api/energies
- /api/cards
- /api/questions
- /api/results
- /api/leaderboard
- /api/player/<name>
- /api/player/<name>/results（刪除自己的紀錄）
        ↓
本機 JSON 資料儲存
- energies.json
- questions.json
- results.json
        ↓
回傳題庫 / 能源資料 / 學習成果 / 排行榜
        ↓
前端即時視覺化呈現
```

## 最終展示架構

```text
python app.py
        ↓
Flask 伺服器 http://127.0.0.1:5000
        ├─ 提供前端 dist 靜態頁面
        └─ 提供 /api 後端資料服務
```

## 線上展示架構（Render）

```text
GitHub Repository
        ↓ Render Web Service
Build Command: pip install -r backend/requirements-render.txt
Start Command: cd backend && gunicorn app:app --bind 0.0.0.0:$PORT
        ↓
Render onrender.com 網址
        ├─ Flask 提供 frontend/dist 靜態頁面
        └─ Flask 提供 /api 後端資料服務
```

> Render 線上版適合讓老師、同學直接開網址觀看；正式上台仍建議保留本機 Flask 版本，避免免費服務休眠或線上資料不持久造成 DEMO 風險。
