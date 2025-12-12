# bot/database.py

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date, timedelta

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
            is_premium BOOLEAN DEFAULT FALSE,
            premium_expire TIMESTAMP,
            referred_by BIGINT,
            timezone TEXT DEFAULT 'UTC',
            lang TEXT DEFAULT 'ru'
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            text TEXT NOT NULL,
            time TIMESTAMP NOT NULL,
            active BOOLEAN DEFAULT TRUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            name TEXT NOT NULL,
            price NUMERIC,
            due_date DATE NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            city TEXT NOT NULL,
            is_favorite BOOLEAN DEFAULT FALSE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id SERIAL PRIMARY KEY,
            referrer_id BIGINT NOT NULL,
            referred_id BIGINT UNIQUE NOT NULL,
            level INTEGER DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            order_id INTEGER PRIMARY KEY,
            user_id BIGINT NOT NULL,
            status TEXT DEFAULT 'waiting',
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS giga_queries (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            query TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT NOW()
        )
    """)
    # В init_db() после других таблиц:
cursor.execute("""
    CREATE TABLE IF NOT EXISTS broadcasts (
        id SERIAL PRIMARY KEY,
        message TEXT NOT NULL,
        target TEXT NOT NULL, -- 'all', 'premium', 'free'
        status TEXT DEFAULT 'scheduled', -- 'scheduled', 'sent', 'cancelled'
        send_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        sent_count INTEGER DEFAULT 0
    )
""")

    conn.commit()
    conn.close()


# --- Пользователи ---
def add_user(user_id, username, first_name, last_name, referred_by=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, username, first_name, last_name, joined_at, referred_by)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id, username, first_name, last_name, datetime.now(), referred_by))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def set_premium(user_id, days=30):
    conn = get_db()
    cursor = conn.cursor()
    expire = datetime.now() + timedelta(days=days)
    cursor.execute("""
        UPDATE users SET is_premium = TRUE, premium_expire = %s WHERE user_id = %s
    """, (expire, user_id))
    conn.commit()
    conn.close()

def check_premium(user_id):
    user = get_user(user_id)
    if not user or not user['is_premium']:
        return False
    if user['premium_expire'] and user['premium_expire'] < datetime.now():
        remove_premium(user_id)
        return False
    return True

def remove_premium(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET is_premium = FALSE, premium_expire = NULL WHERE user_id = %s
    """, (user_id,))
    conn.commit()
    conn.close()


# --- Статистика ---
def get_user_count():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]

def get_premium_count():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_premium = TRUE AND premium_expire > %s", (datetime.now(),))
    return cursor.fetchone()[0]

def get_today_joined_count():
    conn = get_db()
    cursor = conn.cursor()
    today = date.today()
    cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(joined_at) = %s", (today,))
    return cursor.fetchone()[0]

def log_action(user_id, action, details=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO actions (user_id, action, details, timestamp)
        VALUES (%s, %s, %s, %s)
    """, (user_id, action, details, datetime.now()))
    conn.commit()
    conn.close()


# --- Реферальная система ---
def get_referrals(user_id, level=None):
    """Получить список рефералов (всех уровней)"""
    conn = get_db()
    cursor = conn.cursor()
    if level:
        cursor.execute("""
            SELECT r.*, u.first_name, u.username
            FROM referrals r
            JOIN users u ON r.referred_id = u.user_id
            WHERE r.referrer_id = %s AND r.level = %s
        """, (user_id, level))
    else:
        cursor.execute("""
            SELECT r.*, u.first_name, u.username
            FROM referrals r
            JOIN users u ON r.referred_id = u.user_id
            WHERE r.referrer_id = %s
        """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_referral(referrer_id, referred_id, level=1):
    """Добавить реферала (с уровнем)"""
    conn = get_db()
    cursor = conn.cursor()

    # Проверим, не приглашён ли уже
    cursor.execute("SELECT * FROM referrals WHERE referred_id = %s", (referred_id,))
    if cursor.fetchone():
        conn.close()
        return False

    cursor.execute("""
        INSERT INTO referrals (referrer_id, referred_id, level)
        VALUES (%s, %s, %s)
    """, (referrer_id, referred_id, level))
    conn.commit()

    # Назначаем премиум приглашённому (только на 1 уровне)
    if level == 1:
        set_premium(referred_id, days=7)
        log_action(referred_id, "referral_joined", f"by {referrer_id}")
        set_premium(referrer_id, days=7)
        log_action(referrer_id, "referral_reward", f"level=1, user={referred_id}")

    conn.close()
    return True

def build_referral_tree(user_id, max_level=3):
    """Построить дерево рефералов (до 3 уровней)"""
    tree = {1: [], 2: [], 3: []}
    conn = get_db()
    cursor = conn.cursor()

    # Уровень 1: прямые рефералы
    cursor.execute("""
        SELECT referred_id FROM referrals WHERE referrer_id = %s AND level = 1
    """, (user_id,))
    tree[1] = [r[0] for r in cursor.fetchall()]

    # Уровень 2: рефералы моих рефералов
    if tree[1]:
        cursor.execute("""
            SELECT r.referred_id FROM referrals r
            WHERE r.referrer_id = ANY(%s) AND r.level = 1
        """, (tree[1],))
        tree[2] = [r[0] for r in cursor.fetchall()]

    # Уровень 3: рефералы рефералов моих рефералов
    if tree[2]:
        cursor.execute("""
            SELECT r.referred_id FROM referrals r
            WHERE r.referrer_id = ANY(%s) AND r.level = 1
        """, (tree[2],))
        tree[3] = [r[0] for r in cursor.fetchall()]

    conn.close()
    return tree


# --- GigaChat: лимит запросов ---
def get_today_giga_queries(user_id):
    """Сколько запросов GigaChat сегодня сделал пользователь"""
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().date()
    cursor.execute("""
        SELECT COUNT(*) FROM giga_queries
        WHERE user_id = %s AND DATE(timestamp) = %s
    """, (user_id, today))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def log_giga_query(user_id, query):
    """Залогировать запрос к GigaChat"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO giga_queries (user_id, query) VALUES (%s, %s)
    """, (user_id, query))
    conn.commit()
    conn.close()


# --- Платежи ---
def add_payment(order_id, user_id):
    """Добавить платёж в ожидании"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO payments (order_id, user_id, status)
        VALUES (%s, %s, 'waiting')
        ON CONFLICT (order_id) DO NOTHING
    """, (order_id, user_id))
    conn.commit()
    conn.close()

def confirm_payment(order_id):
    """Подтвердить оплату"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE payments SET status = 'paid' WHERE order_id = %s AND status = 'waiting'
    """, (order_id,))
    cursor.execute("""
        SELECT user_id FROM payments WHERE order_id = %s
    """, (order_id,))
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result['user_id'] if result else None
