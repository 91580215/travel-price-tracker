
from flask import Flask, render_template, request, jsonify
from datetime import date
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "prices.db"
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                item_name TEXT NOT NULL,
                price INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT
                    (datetime('now', 'localtime'))
            )
        """)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/search/flights", methods=["POST"])
def search_flights():
    data = request.get_json(silent=True) or {}

    origin = str(data.get("origin", "")).strip()
    destination = str(data.get("destination", "")).strip()
    depart_date = str(data.get("depart_date", "")).strip()

    if not origin or not destination or not depart_date:
        return jsonify({"error": "출발지, 도착지, 날짜를 입력해 주세요."}), 400

    if origin == destination:
        return jsonify({"error": "출발지와 도착지를 다르게 선택해 주세요."}), 400

    try:
        date.fromisoformat(depart_date)
    except ValueError:
        return jsonify({"error": "올바른 날짜를 선택해 주세요."}), 400

    # 테스트용 예시 가격입니다. 실시간 항공권 가격이 아닙니다.
    results = [
        {"id": "flight-a", "name": "항공권 예시 A", "price": 85000},
        {"id": "flight-b", "name": "항공권 예시 B", "price": 112000},
        {"id": "flight-c", "name": "항공권 예시 C", "price": 139000},
    ]

    return jsonify({
        "demo": True,
        "message": "테스트용 예시 가격입니다. 실제 예약 가격이 아닙니다.",
        "route": f"{origin} → {destination}",
        "date": depart_date,
        "results": results,
    })


@app.route("/api/search/hotels", methods=["POST"])
def search_hotels():
    data = request.get_json(silent=True) or {}

    city = str(data.get("city", "")).strip()
    checkin = str(data.get("checkin", "")).strip()
    checkout = str(data.get("checkout", "")).strip()

    if not city or not checkin or not checkout:
        return jsonify({"error": "도시와 숙박 날짜를 입력해 주세요."}), 400

    try:
        start = date.fromisoformat(checkin)
        end = date.fromisoformat(checkout)
    except ValueError:
        return jsonify({"error": "올바른 날짜를 선택해 주세요."}), 400

    nights = (end - start).days

    if nights <= 0:
        return jsonify({"error": "체크아웃은 체크인 이후 날짜여야 합니다."}), 400

    # 테스트용 예시 가격입니다. 실제 숙소 가격이 아닙니다.
    results = [
        {"id": "hotel-a", "name": "숙소 예시 A", "price": 65000},
        {"id": "hotel-b", "name": "숙소 예시 B", "price": 82000},
        {"id": "hotel-c", "name": "숙소 예시 C", "price": 105000},
    ]

    return jsonify({
        "demo": True,
        "message": "테스트용 예시 가격입니다. 실제 예약 가격이 아닙니다.",
        "city": city,
        "checkin": checkin,
        "checkout": checkout,
        "nights": nights,
        "results": results,
    })


@app.route("/api/history", methods=["GET"])
def get_history():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT id, category, item_name, price, created_at
            FROM price_history
            ORDER BY id DESC
        """).fetchall()

    return jsonify([dict(row) for row in rows])


@app.route("/api/history", methods=["POST"])
def save_history():
    data = request.get_json(silent=True) or {}

    category = str(data.get("category", "")).strip()
    item_name = str(data.get("item_name", "")).strip()

    try:
        price = int(data.get("price"))
    except (TypeError, ValueError):
        return jsonify({"error": "가격이 올바르지 않습니다."}), 400

    if category not in ("항공권", "숙소"):
        return jsonify({"error": "올바른 항목 종류가 아닙니다."}), 400

    if not item_name or price <= 0:
        return jsonify({"error": "항목 이름과 올바른 가격이 필요합니다."}), 400

    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO price_history (category, item_name, price)
            VALUES (?, ?, ?)
        """, (category, item_name, price))
        record_id = cursor.lastrowid

    return jsonify({
        "message": "가격을 저장했어요!",
        "id": record_id,
    }), 201


@app.route("/api/history/<int:record_id>", methods=["DELETE"])
def delete_history(record_id):
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM price_history WHERE id = ?",
            (record_id,)
        )

    if cursor.rowcount == 0:
        return jsonify({"error": "기록을 찾을 수 없습니다."}), 404

    return jsonify({"message": "기록을 삭제했어요!"})


init_db()

if __name__ == "__main__":
    app.run(debug=True)
