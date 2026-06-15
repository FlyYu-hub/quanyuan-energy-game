from __future__ import annotations
import random
from datetime import datetime, timezone
import os
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from storage import append_json_list, clear_json_list, read_json, write_json

ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"

app = Flask(__name__, static_folder=str(FRONTEND_DIST), static_url_path="")
CORS(app)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def ok(data=None, message="success"):
    return jsonify({"ok": True, "message": message, "data": data})


def fail(message="error", status=400, data=None):
    return jsonify({"ok": False, "message": message, "data": data}), status


def get_results():
    rows = read_json("results", [])
    return rows if isinstance(rows, list) else []


def summarize_player(player_name: str):
    name = (player_name or "Demo玩家").strip()
    rows = [r for r in get_results() if (r.get("playerName") or "Demo玩家") == name]
    total_points = sum(int(r.get("knowledgePoints", 0)) for r in rows)
    total_correct = sum(int(r.get("correct", 0)) for r in rows)
    total_answered = sum(int(r.get("correct", 0)) + int(r.get("wrong", 0)) for r in rows)
    avg_accuracy = round((total_correct / total_answered * 100), 1) if total_answered else 0

    weak_counter = {}
    for r in rows:
        weak = r.get("weakCategory")
        if weak:
            weak_counter[weak] = weak_counter.get(weak, 0) + 1
    weak_category = "待觀察" if not weak_counter else sorted(weak_counter.items(), key=lambda x: x[1], reverse=True)[0][0]

    badges = []
    if len(rows) >= 1:
        badges.append({"id": "starter", "name": "能源新手", "reason": "完成首次學習紀錄"})
    if total_points >= 80:
        badges.append({"id": "knowledge", "name": "知識充電中", "reason": "累積 80 點以上知識點數"})
    if total_points >= 160:
        badges.append({"id": "sdg7", "name": "SDG 7 守護者", "reason": "累積 160 點以上知識點數"})
    if avg_accuracy >= 80 and total_answered >= 5:
        badges.append({"id": "quiz", "name": "答題高手", "reason": "平均正確率達 80% 以上"})

    recent = sorted(rows, key=lambda r: r.get("createdAt", ""), reverse=True)[:5]
    return {
        "playerName": name,
        "playCount": len(rows),
        "totalPoints": total_points,
        "avgAccuracy": avg_accuracy,
        "weakCategory": weak_category,
        "badges": badges,
        "recent": recent,
    }


def build_leaderboard(limit: int = 10):
    grouped = {}
    for r in get_results():
        name = (r.get("playerName") or "Demo玩家").strip()
        if not name:
            name = "Demo玩家"
        g = grouped.setdefault(name, {
            "playerName": name,
            "totalPoints": 0,
            "bestScore": 0,
            "correct": 0,
            "answered": 0,
            "playCount": 0,
            "lastPlayedAt": "",
        })
        g["totalPoints"] += int(r.get("knowledgePoints", 0))
        g["bestScore"] = max(g["bestScore"], int(r.get("score", 0)))
        g["correct"] += int(r.get("correct", 0))
        g["answered"] += int(r.get("correct", 0)) + int(r.get("wrong", 0))
        g["playCount"] += 1
        g["lastPlayedAt"] = max(g["lastPlayedAt"], r.get("createdAt", ""))

    rows = []
    for g in grouped.values():
        g["accuracy"] = round(g["correct"] / g["answered"] * 100, 1) if g["answered"] else 0
        rows.append(g)
    rows.sort(key=lambda x: (x["totalPoints"], x["bestScore"], x["accuracy"]), reverse=True)
    return rows[:limit]


@app.route("/api/health")
def health():
    return ok({
        "service": "全源配服 Flask API",
        "status": "running",
        "storage": "local-json",
        "time": now_iso(),
    })


@app.route("/api/system-stats")
def system_stats():
    energies = read_json("energies", [])
    questions = read_json("questions", [])
    results = get_results()
    return ok({
        "energyCount": len(energies),
        "questionCount": len(questions),
        "resultCount": len(results),
        "leaderboardCount": len(build_leaderboard(100)),
        "storage": "local-json",
        "updatedAt": now_iso(),
    })


@app.route("/api/energies")
def energies():
    return ok(read_json("energies", []))


@app.route("/api/questions")
def questions():
    rows = read_json("questions", [])

    level = request.args.get("level")
    if level:
        rows = [q for q in rows if q.get("level") == level]

    shuffle = request.args.get("shuffle", "0").lower() in ("1", "true", "yes")

    try:
        limit = int(request.args.get("limit", 0))
    except ValueError:
        limit = 0

    if shuffle:
        rows = rows[:]
        random.shuffle(rows)

    if limit > 0:
        rows = rows[:limit]

    return ok(rows)


@app.route("/api/cards")
def cards():
    energies = read_json("energies", [])
    card_rows = []
    for e in energies:
        card_rows.append({
            "uid": f"{e['id']}-visual",
            "pairId": e["id"],
            "cardType": "visual",
            "title": e["name"],
            "icon": e.get("icon", "⚡"),
            "text": e.get("principle", ""),
            "keywords": e.get("keywords", []),
            "energy": e,
        })
        card_rows.append({
            "uid": f"{e['id']}-concept",
            "pairId": e["id"],
            "cardType": "concept",
            "title": "關鍵字卡",
            "icon": "🔎",
            "text": "、".join(e.get("keywords", [])),
            "keywords": e.get("keywords", []),
            "energy": e,
        })
    return ok(card_rows)


@app.route("/api/results", methods=["GET", "POST"])
def results():
    if request.method == "GET":
        return ok(sorted(get_results(), key=lambda r: r.get("createdAt", ""), reverse=True))

    payload = request.get_json(silent=True) or {}
    player_name = (payload.get("playerName") or "Demo玩家").strip()[:30] or "Demo玩家"
    mode = payload.get("mode") or "unknown"
    result = {
        "id": str(uuid4()),
        "playerName": player_name,
        "mode": mode,
        "score": int(payload.get("score", 0)),
        "correct": int(payload.get("correct", 0)),
        "wrong": int(payload.get("wrong", 0)),
        "skipped": int(payload.get("skipped", 0)),
        "timeSpent": int(payload.get("timeSpent", 0)),
        "moves": int(payload.get("moves", 0)),
        "knowledgePoints": int(payload.get("knowledgePoints", 0)),
        "weakCategory": payload.get("weakCategory") or "待觀察",
        "detail": payload.get("detail", {}),
        "createdAt": now_iso(),
    }
    append_json_list("results", result)
    return ok(result, "result saved")


@app.route("/api/leaderboard")
def leaderboard():
    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        limit = 10
    return ok(build_leaderboard(limit))


@app.route("/api/player/<name>")
def player(name):
    return ok(summarize_player(name))


@app.route("/api/player/<name>/results", methods=["DELETE", "POST"])
def delete_player_results(name):
    """刪除指定玩家自己的遊玩紀錄。

    設計成玩家層級刪除，而不是全站清空，避免展示時誤刪其他組員或 DEMO 資料。
    POST 也接受是為了相容部分環境不方便送 DELETE 的狀況。
    """
    player_name = (name or "Demo玩家").strip()[:30] or "Demo玩家"
    rows = get_results()
    kept = [r for r in rows if (r.get("playerName") or "Demo玩家").strip() != player_name]
    removed = len(rows) - len(kept)
    write_json("results", kept)
    return ok({
        "playerName": player_name,
        "removed": removed,
        "remaining": len(kept),
        "leaderboard": build_leaderboard(10),
    }, "player results deleted")


@app.route("/api/demo/seed", methods=["POST"])
def seed_demo():
    demo_rows = [
        {"playerName": "倚臣", "mode": "quiz", "score": 120, "correct": 6, "wrong": 1, "skipped": 1, "timeSpent": 180, "moves": 0, "knowledgePoints": 120, "weakCategory": "太陽光電"},
        {"playerName": "能博", "mode": "memory", "score": 105, "correct": 0, "wrong": 0, "skipped": 0, "timeSpent": 95, "moves": 18, "knowledgePoints": 105, "weakCategory": "待觀察"},
        {"playerName": "翊豪", "mode": "quiz", "score": 95, "correct": 5, "wrong": 2, "skipped": 1, "timeSpent": 210, "moves": 0, "knowledgePoints": 95, "weakCategory": "廢棄物發電"},
        {"playerName": "Demo玩家", "mode": "quiz", "score": 140, "correct": 8, "wrong": 0, "skipped": 0, "timeSpent": 150, "moves": 0, "knowledgePoints": 140, "weakCategory": "待觀察"},
    ]
    for row in demo_rows:
        row.update({"id": str(uuid4()), "detail": {}, "createdAt": now_iso()})
        append_json_list("results", row)
    return ok({"inserted": len(demo_rows), "leaderboard": build_leaderboard(10)}, "demo data seeded")


@app.route("/api/demo/reset", methods=["POST"])
def reset_demo():
    clear_json_list("results")
    return ok({"resultCount": 0}, "results cleared")


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path: str):
    if FRONTEND_DIST.exists():
        target = FRONTEND_DIST / path
        if path and target.exists() and target.is_file():
            return send_from_directory(FRONTEND_DIST, path)
        return send_from_directory(FRONTEND_DIST, "index.html")
    return ok({
        "service": "全源配服 Flask API",
        "health": "/api/health",
        "note": "前端尚未 build；開發模式請另開 frontend 並執行 npm run dev。",
    })


if __name__ == "__main__":
    # Local execution uses 127.0.0.1 by default.
    # Render or other web hosts provide PORT in environment variables.
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
