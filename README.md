# 全源配服：SDG 7 能源遊戲化學習平台

本專案為「網站後端開發」課程期末專題版本，延續前端課的能源翻牌網頁，升級為具備 Flask API、資料儲存、排行榜、學習成果與後端測試面板的零成本 Web App。

## 專案定位

- 完整後端展示：使用 Flask 單一入口 `http://127.0.0.1:5000/`
- 線上網址展示：可部署到 Render Web Service
- GitHub Pages：僅適合前端靜態備案，不支援 Flask 後端
- 資料儲存：預設使用本機 JSON，零成本且適合課堂 DEMO

## 技術架構

- 前端：Vue 3 + Vite + JavaScript + CSS RWD
- 後端：Flask + Flask-CORS
- 線上部署：Render Web Service + Gunicorn
- 資料：本機 JSON 檔案儲存，可於未來擴充 MongoDB
- 展示：本機 Flask 單一入口、Render 線上展示、操作影片備案

## 資料夾結構

```text
quanyuan_final_project/
├─ backend/
│  ├─ app.py
│  ├─ storage.py
│  ├─ requirements.txt
│  ├─ requirements-render.txt
│  ├─ data/
│  └─ wheelhouse/
├─ frontend/
│  ├─ src/
│  ├─ dist/
│  ├─ package.json
│  └─ vite.config.js
├─ docs/
├─ scripts/
├─ render.yaml
├─ Procfile
├─ .gitignore
└─ README.md
```

## 一、本機最終展示模式（推薦上台使用）

本模式只需要開啟 Flask，一個網址即可展示前端頁面與後端 API。

### 方式 A：直接雙擊

雙擊：

```text
scripts/run_backend.bat
```

啟動後打開：

```text
http://127.0.0.1:5000/
```

### 方式 B：手動執行

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

打開：

```text
http://127.0.0.1:5000/
```

## 二、前端開發模式

開發或修改前端時才需要使用此模式。

後端：

```powershell
cd backend
.venv\Scripts\activate
python app.py
```

前端：

```powershell
cd frontend
npm install
npm run dev
```

打開：

```text
http://127.0.0.1:5173/
```

## 三、重新 Build 前端

如果修改 `frontend/src/App.vue` 或 `frontend/src/style.css`，請重新 build：

```powershell
cd frontend
npm install
npm run build
```

完成後 Flask 會讀取新的 `frontend/dist`。

## 四、Render 線上部署方式

本專案已整理為 Render-ready。部署時請先把整個專案推到 GitHub，再到 Render 建立 Web Service。

### Render 建議設定

- Service Type：Web Service
- Repository：選擇本專案 GitHub repo
- Root Directory：留空
- Build Command：

```bash
pip install -r backend/requirements-render.txt
```

- Start Command：

```bash
cd backend && gunicorn app:app --bind 0.0.0.0:$PORT
```

或直接使用本專案的 `render.yaml` 建立服務。

### Render 注意事項

- Render 免費 Web Service 可能會在一段時間沒有流量後休眠，第一次開啟可能需要等待約 1 分鐘。
- 本專案使用本機 JSON 儲存，Render 免費環境的本機檔案不適合永久保存。因此線上版主要作為展示網址；正式上台建議仍使用本機 Flask 展示。
- Render 線上版可用來讓老師與組長不用下載也能開啟作品；本機版則保留完整且穩定的後端 DEMO。

## 五、離線套件與學校電腦注意事項

本專案附帶 `backend/wheelhouse/` 離線套件包，支援 Windows Python 3.11～3.13 的常用 Flask 依賴。

若學校電腦有 Python 但網路不穩，可在後端資料夾執行：

```powershell
pip install --no-index --find-links=wheelhouse -r requirements.txt
python app.py
```

若學校電腦完全沒有 Python，無法直接執行 Flask。正式展示建議使用已測試完成的個人電腦，並準備操作影片與截圖備案。

## 六、主要功能

1. 首頁 Dashboard：玩家暱稱、後端連線狀態、今日任務與統計卡片。
2. 能源圖鑑：由後端提供六種能源資料。
3. 翻牌配對：圖示卡與關鍵字卡配對，配對成功會顯示能源知識卡。
4. 問答闖關：題目由後端題庫提供，答題結果回傳後端儲存。
5. 學習成果：後端依玩家名稱彙整點數、正確率、徽章與建議複習。
6. 排行榜：由後端依遊戲結果即時計算。
7. 後端測試面板：顯示 API 狀態、資料數量與產生 DEMO 資料。
8. 刪除紀錄：排行榜頁可刪除目前玩家自己的紀錄，不清空全站資料。
9. DEMO 模式：提供提示下一組配對、一鍵完成翻牌、選擇本題正解、一鍵完成問答與產生展示資料。
10. 深色模式：內建主題切換，避免系統深色模式造成文字看不清。
11. RWD：支援桌機、筆電、平板與手機排版。

## 七、API 清單

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/api/health` | 後端健康檢查 |
| GET | `/api/system-stats` | 系統資料統計 |
| GET | `/api/energies` | 能源圖鑑資料 |
| GET | `/api/cards` | 翻牌配對卡片資料 |
| GET | `/api/questions` | 問答題庫 |
| POST | `/api/results` | 儲存遊戲結果 |
| GET | `/api/results` | 查詢所有遊戲結果 |
| GET | `/api/leaderboard` | 排行榜 |
| GET | `/api/player/<name>` | 玩家學習成果 |
| POST | `/api/demo/seed` | 產生 DEMO 資料 |
| DELETE/POST | `/api/player/<name>/results` | 刪除指定玩家自己的遊玩紀錄 |

## 八、最終 DEMO 驗收流程

1. 開啟 `http://127.0.0.1:5000/`，確認首頁顯示「後端連線正常」。
2. 進入能源圖鑑，確認六種能源資料正常顯示。
3. 開啟 DEMO 模式。
4. 進入翻牌配對，測試「提示下一組配對」與「一鍵完成翻牌」。
5. 進入問答闖關，測試「選擇本題正解」與「一鍵完成問答」。
6. 進入學習成果，確認玩家點數、正確率、徽章與弱點分析。
7. 進入排行榜，確認資料有更新，並測試「刪除我的紀錄」。
8. 進入後端面板，確認 API 狀態、能源資料數、題庫數與結果筆數。
9. 開啟深色模式逐頁檢查。
10. 用 Chrome DevTools 或手機測試 RWD。

## 九、展示定位提醒

- 最完整展示：本機 Flask `http://127.0.0.1:5000/`
- 線上展示：Render Web Service 網址
- 靜態備案：GitHub Pages 可展示前端，但不支援 Flask 後端
- 保險備案：操作影片、截圖、SourceCode.zip、GitHub repo

## 十、專題價值

本專題不只是前端翻牌遊戲，而是透過 Flask 後端建立資料流：前端取得能源資料與題庫、使用者完成遊戲後將結果送回後端、後端再彙整成學習成果與排行榜，展現完整的前後端整合流程。此設計呼應 SDG 7「可負擔的乾淨能源」，並以遊戲化方式提升能源教育的互動性與學習動機。
