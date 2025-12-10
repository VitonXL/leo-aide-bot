import sqlite3
from datetime import datetime, timedelta

def init_db():
    with sqlite3.connect("users.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_premium INTEGER DEFAULT 0,
                premium_until TIMESTAMP,
                referral_count INTEGER DEFAULT 0,
                premium_converted INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                text TEXT,
                notify_at TIMESTAMP,
                sent INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                name TEXT,
                amount REAL,
                next_payment TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                referral_id INTEGER,
                referrer_id INTEGER,
                premium_converted INTEGER DEFAULT 0,
                PRIMARY KEY (referral_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS movie_usage (
                user_id INTEGER PRIMARY KEY,
                count INTEGER DEFAULT 0,
                last_reset DATE
            )
        """)
        conn.commit()

def add_user(user_id, username, first_name, last_name):
    with sqlite3.connect("users.db") as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
            (user_id, username, first_name, last_name)
        )

def get_user(user_id):
    with sqlite3.connect("users.db") as conn:
        return conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()

def add_reminder(user_id, text, notify_at):
    with sqlite3.connect("users.db") as conn:
        conn.execute(
            "INSERT INTO reminders (user_id, text, notify_at) VALUES (?, ?, ?)",
            (user_id, text, notify_at)
        )

def get_active_reminders():
    with sqlite3.connect("users.db") as conn:
        return conn.execute(
            "SELECT id, user_id, text, notify_at FROM reminders WHERE sent = 0 AND notify_at <= datetime('now', '+30 seconds')"
        ).fetchall()

def mark_reminder_sent(reminder_id):
    with sqlite3.connect("users.db") as conn:
        conn.execute("UPDATE reminders SET sent = 1 WHERE id = ?", (reminder_id,))

def add_subscription(user_id, name, amount, next_payment):
    with sqlite3.connect("users.db") as conn:
        conn.execute(
            "INSERT INTO subscriptions (user_id, name, amount, next_payment) VALUES (?, ?, ?, ?)",
            (user_id, name, amount, next_payment)
        )

def get_subscriptions(user_id):
    with sqlite3.connect("users.db") as conn:
        return conn.execute(
            "SELECT name, amount, next_payment FROM subscriptions WHERE user_id = ?", (user_id,)
        ).fetchall()

def set_premium(user_id, amount_ton):
    duration_days = 30
    premium_until = datetime.now() + timedelta(days=duration_days)
    with sqlite3.connect("users.db") as conn:
        conn.execute(
            "UPDATE users SET is_premium = 1, premium_until = ? WHERE user_id = ?",
            (premium_until, user_id)
        )

def get_premium_info(user_id):
    user = get_user(user_id)
    if not user or not user[10]:  # is_premium
        return None
    until = datetime.fromisoformat(user[11])
    days_left = (until - datetime.now()).days
    return {"until": until, "days_left": max(0, days_left)}

def is_premium(user_id):
    info = get_premium_info(user_id)
    return info is not None

def get_stats():
    with sqlite3.connect("users.db") as conn:
        total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        premium = conn.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1").fetchone()[0]
        earnings = conn.execute("SELECT SUM(premium_converted) * 50 FROM users").fetchone()[0] or 0
        soon_expire = conn.execute("""
            SELECT user_id FROM users 
            WHERE is_premium = 1 AND premium_until BETWEEN datetime('now') AND datetime('now', '+3 days')
        """).fetchall()
        return {
            "total_users": total,
            "total_premium": premium,
            "total_earnings": earnings / 100,  # условно
            "soon_expire_count": len(soon_expire),
            "soon_expire_list": [r[0] for r in soon_expire]
        }

def add_referral(referral_id, referrer_id):
    with sqlite3.connect("users.db") as conn:
        conn.execute(
            "INSERT OR IGNORE INTO referrals (referral_id, referrer_id) VALUES (?, ?)",
            (referral_id, referrer_id)
        )
        conn.execute(
            "UPDATE users SET referral_count = referral_count + 1 WHERE user_id = ?",
            (referrer_id,)
        )

def get_referrer(user_id):
    with sqlite3.connect("users.db") as conn:
        row = conn.execute(
            "SELECT referrer_id FROM referrals WHERE referral_id = ?", (user_id,)
        ).fetchone()
        return row[0] if row else None

def increment_premium_converted(referrer_id):
    with sqlite3.connect("users.db") as conn:
        conn.execute(
            "UPDATE users SET premium_converted = premium_converted + 1 WHERE user_id = ?",
            (referrer_id,)
        )
        conn.execute(
            "UPDATE referrals SET premium_converted = 1 WHERE referrer_id = ? AND referral_id IN (SELECT user_id FROM users WHERE is_premium = 1)",
            (referrer_id,)
        )

def extend_premium_for_referrer(referrer_id):
    with sqlite3.connect("users.db") as conn:
        conn.execute(
            "UPDATE users SET premium_until = datetime(premium_until, '+3 days') WHERE user_id = ?",
            (referrer_id,)
        )

def get_movie_usage(user_id):
    with sqlite3.connect("users.db") as conn:
        row = conn.execute(
            "SELECT count, last_reset FROM movie_usage WHERE user_id = ?", (user_id,)
        ).fetchone()
        if not row:
            return 0
        last_reset = datetime.fromisoformat(row[1])
        if (datetime.now() - last_reset).days >= 1:
            conn.execute("UPDATE movie_usage SET count = 0, last_reset = ? WHERE user_id = ?", (datetime.now().date(), user_id))
            conn.commit()
            return 0
        return row[0]

def increment_movie_usage(user_id):
    with sqlite3.connect("users.db") as conn:
        conn.execute(
            "INSERT OR IGNORE INTO movie_usage (user_id, count, last_reset) VALUES (?, 0, ?)",
            (user_id, datetime.now().date())
        )
        conn.execute(
            "UPDATE movie_usage SET count = count + 1, last_reset = ? WHERE user_id = ? AND (last_reset != ? OR last_reset IS NULL)",
            (datetime.now().date(), user_id, datetime.now().date())
        )
        conn.execute(
            "UPDATE movie_usage SET count = count + 1 WHERE user_id = ? AND last_reset = ?",
            (user_id, datetime.now().date())
