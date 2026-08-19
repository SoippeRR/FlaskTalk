from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "btw-change-that"

DB_PATH = os.path.join(os.path.dirname(__file__), "flasktalk.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def login_required(view):
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    wrapped.__name__ = view.__name__
    return wrapped


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("chat"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            return render_template("register.html", error="Заполните все поля")

        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            conn.close()
            return render_template("register.html", error="Такой пользователь уже существует")

        password_hash = generate_password_hash(password)
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        session["user_id"] = user["id"]
        session["username"] = username
        return redirect(url_for("chat"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("chat"))

        return render_template("login.html", error="Неверный логин или пароль")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/chat")
@login_required
def chat():
    conn = get_db()
    users = conn.execute(
        "SELECT id, username FROM users WHERE id != ? ORDER BY username",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    return render_template("chat.html", users=users, username=session["username"])


@app.route("/api/users")
@login_required
def api_users():
    conn = get_db()
    users = conn.execute(
        "SELECT id, username FROM users WHERE id != ? ORDER BY username",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    return jsonify([{"id": u["id"], "username": u["username"]} for u in users])


@app.route("/api/messages/<int:other_id>")
@login_required
def api_messages(other_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT m.id, m.sender_id, m.receiver_id, m.text, m.created_at, u.username as sender_name
        FROM messages m
        JOIN users u ON u.id = m.sender_id
        WHERE (sender_id = ? AND receiver_id = ?)
           OR (sender_id = ? AND receiver_id = ?)
        ORDER BY m.id ASC
    """, (session["user_id"], other_id, other_id, session["user_id"])).fetchall()
    conn.close()

    return jsonify([{
        "id": r["id"],
        "sender_id": r["sender_id"],
        "sender_name": r["sender_name"],
        "text": r["text"],
        "created_at": r["created_at"]
    } for r in rows])


@app.route("/api/send", methods=["POST"])
@login_required
def api_send():
    data = request.get_json()
    receiver_id = data.get("receiver_id")
    text = data.get("text", "").strip()

    if not receiver_id or not text:
        return jsonify({"error": "Пустое сообщение"}), 400

    conn = get_db()
    conn.execute(
        "INSERT INTO messages (sender_id, receiver_id, text, created_at) VALUES (?, ?, ?, ?)",
        (session["user_id"], receiver_id, text, datetime.now().strftime("%H:%M"))
    )
    conn.commit()
    conn.close()

    return jsonify({"ok": True})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
