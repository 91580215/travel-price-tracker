import os
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "prices.db")


# 데이터베이스 준비
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                title TEXT NOT NULL,
                travel_date TEXT NOT NULL,
                price INTEGER NOT NULL,
                provider TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


# 웹사이트 화면
@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


# CSS 파일
@app.route("/style.css")
def style():
    return send_from_directory(BASE_DIR, "style.css")


# JavaScript 파일
@app.route("/script.js")
def script():
    return send_from_directory(BASE_DIR, "script.js")


# 항공권 검색: 테스트용 예시 데이터
@app.route("/api/search/flights", methods=["POST"])
def search_flights():
    data = request.get_json(silent=True) or {}

    origin = data.get("origin", "").strip()
    destination = data.get("destination", "").strip()
    travel_date = data.get("date", "").strip()

    if not origin or not destination or not travel_date:
        return jsonify({"error": "출발지, 도착지, 날짜를 입력해 주세요."}), 400

    if origin == destination:
        return jsonify({"error": "출발지와 도착지를 다르게 입력해 주세요."}), 400

    results = [
        {
            "kind": "flight",
            "title": f"{origin} → {destination}",
            "travel_date": travel_date,
            "price": 89000,
            "provider": "여행사 A (예시)"
        },
        {
            "kind": "flight",
            "title": f"{origin} → {destination}",
            "travel_date": travel_date,
            "price": 125000,
            "provider": "여행사 B (예시)"
        },
        {
            "kind": "flight",
            "title": f"{origin} → {destination}",
            "travel_date": travel_date,
            "price": 109000,
            "provider": "여행사 C (예시)"
        }
    ]

    results.sort(key=lambda item: item["price"])
    return jsonify(results)


# 숙소 검색: 테스트용 예시 데이터
@app.route("/api/search/hotels", methods=["POST"])
def search_hotels():
    data = request.get_json(silent=True) or {}

    destination = data.get("destination", "").strip()
    checkin = data.get("checkin", "").strip()
    checkout = data.get("checkout", "").strip()

    if not destination or not checkin or not checkout:
        return jsonify({"error": "여행지와 체크인·체크아웃 날짜를 입력해 주세요."}), 400

    try:
        start = datetime.strptime(checkin, "%Y-%m-%d")
        end = datetime.strptime(checkout, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "날짜를 올바르게 입력해 주세요."}), 400

    nights = (end - start).days

    if nights <= 0:
        return jsonify({"error": "체크아웃은 체크인보다 뒤 날짜여야 해요."}), 400

    # 가격은 1박 기준
    results = [
        {
            "kind": "hotel",
            "title": f"{destination} 숙소",
            "travel_date": f"{checkin} ~ {checkout}",
            "price": 55000 * nights,
            "provider": "숙소 A (예시)"
        },
        {
            "kind": "hotel",
            "title": f"{destination} 숙소",
            "travel_date": f"{checkin} ~ {checkout}",
            "price": 79000 * nights,
            "provider": "숙소 B (예시)"
        },
        {
            "kind": "hotel",
            "title": f"{destination} 숙소",
            "travel_date": f"{checkin} ~ {checkout}",
            "price": 68000 * nights,
            "provider": "숙소 C (예시)"
        }
    ]

    results.sort(key=lambda item: item["price"])
    return jsonify(results)


# 저장된 가격 기록 조회
@app.route("/api/history", methods=["GET"])
def get_history():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT *
            FROM price_history
            ORDER BY id DESC
        """).fetchall()

    return jsonify([dict(row) for row in rows])


# 가격 기록 저장
@app.route("/api/history", methods=["POST"])
def save_history():
    data = request.get_json(silent=True) or {}

    required = ["kind", "title", "travel_date", "price", "provider"]

    if any(key not in data for key in required):
        return jsonify({"error": "저장에 필요한 정보가 부족해요."}), 400

    if data["kind"] not in ("flight", "hotel"):
        return jsonify({"error": "올바르지 않은 상품 종류예요."}), 400

    try:
        price = int(data["price"])
    except (ValueError, TypeError):
        return jsonify({"error": "가격이 올바르지 않아요."}), 400

    if price < 0:
        return jsonify({"error": "가격은 음수일 수 없어요."}), 400

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            INSERT INTO price_history
            (kind, title, travel_date, price, provider, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["kind"],
            str(data["title"]),
            str(data["travel_date"]),
            price,
            str(data["provider"]),
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

        record_id = cursor.lastrowid

    return jsonify({"message": "가격을 저장했어요!", "id": record_id}), 201


# 가격 기록 삭제
@app.route("/api/history/<int:record_id>", methods=["DELETE"])
def delete_history(record_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "DELETE FROM price_history WHERE id = ?",
            (record_id,)
        )

    if cursor.rowcount == 0:
        return jsonify({"error": "해당 기록을 찾을 수 없어요."}), 404

    return jsonify({"message": "기록을 삭제했어요!"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
else:
    init_db()
