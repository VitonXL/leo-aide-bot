import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            joined_at TIMESTAMP NOT NULL,
            is_premium BOOLEAN DEFAULT FALSE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Таблицы инициализированы")
    return db

def get_user(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def get_user_count():
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]

def get_premium_count():
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1")
    return cursor.fetchone()[0]

def get_today_joined_count():
    cursor = db.cursor()
    today = date.today().isoformat()
    cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(joined_at) = ?", (today,))
    return cursor.fetchone()[0]
    
def add_user(user_id):
    cursor = db.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    db.commit()

def set_premium(user_id, is_premium=True):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET is_premium = ? WHERE user_id = ?", (int(is_premium), user_id))
    db.commit()

def set_admin(user_id, is_admin=True):
    cursor = db.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        db.commit()
    except sqlite3.OperationalError:
        pass
    cursor.execute("UPDATE users SET is_admin = ? WHERE user_id = ?", (int(is_admin), user_id))
    db.commit()

def add_city(user_id, city):
    user = get_user(user_id)
    if user:
        cities = user[3].split(",") if user[3] else []
        if len(cities) >= (5 if user[2] else 1) and city not in cities:
            return False
        if city not in cities:
            cities.append(city)
            cursor = db.cursor()
            cursor.execute("UPDATE users SET cities = ? WHERE user_id = ?", (",".join(cities), user_id))
            db.commit()
    return True

def get_cities(user_id):
    user = get_user(user_id)
    return user[3].split(",") if user and user[3] else []

def reset_ai_requests():
    cursor = db.cursor()
    cursor.execute("UPDATE users SET ai_requests = 10")
    db.commit()
    print("🔁 AI-запросы сброшены")

def use_ai_request(user_id):
    user = get_user(user_id)
    if user and user[4] > 0:
        cursor = db.cursor()
        cursor.execute("UPDATE users SET ai_requests = ai_requests - 1 WHERE user_id = ?", (user_id,))
        db.commit()
        return True
    return False

def get_ai_requests_left(user_id):
    user = get_user(user_id)
    return user[4] if user else 0
