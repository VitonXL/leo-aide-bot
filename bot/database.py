# bot/database.py
import sqlite3
import os
import json
from datetime import datetime, timedelta

DB_PATH = "bot.db"

class Database:
    def __init__(self):
        self.init_db()

    def init_db(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    is_admin INTEGER DEFAULT 0,
                    premium_until TEXT,
                    daily_weather_count INTEGER DEFAULT 0,
                    daily_movies_count INTEGER DEFAULT 0,
                    daily_scan_count INTEGER DEFAULT 0,
                    daily_currency_count INTEGER DEFAULT 0,
                    last_reset TEXT,
                    theme TEXT DEFAULT 'light'
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS referrals (
                    user_id INTEGER PRIMARY KEY,
                    referrer_id INTEGER,
                    count INTEGER DEFAULT 0
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    text TEXT,
                    time TEXT
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    renewal_date TEXT
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    user_id INTEGER,
                    action TEXT
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS payment_logs (
                    tx_hash TEXT PRIMARY KEY,
                    processed_at TEXT
                )
            ''')

    def get_user(self, user_id):
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if not row:
                is_admin = 1 if user_id == 1799560429 else 0
                conn.execute('''
                    INSERT INTO users (user_id, is_admin) VALUES (?, ?)
                ''', (user_id, is_admin))
                conn.commit()
                return self.get_user(user_id)
            return dict(row)

    def is_premium(self, user_id):
        user = self.get_user(user_id)
        if user["is_admin"]:
            return True
        if user["premium_until"]:
            return datetime.now() < datetime.fromisoformat(user["premium_until"])
        return False

    def grant_premium(self, user_id, days):
        until = (datetime.now() + timedelta(days=days)).isoformat()
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                UPDATE users SET premium_until = ? WHERE user_id = ?
            ''', (until, user_id))
            conn.commit()

    def reset_daily_counters(self, user_id):
        user = self.get_user(user_id)
        last = user["last_reset"]
        today = datetime.now().strftime("%Y-%m-%d")

        if last != today:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('''
                    UPDATE users SET
                        daily_weather_count = 0,
                        daily_movies_count = 0,
                        daily_scan_count = 0,
                        daily_currency_count = 0,
                        last_reset = ?
                    WHERE user_id = ?
                ''', (today, user_id))
                conn.commit()

    def update_user(self, user_id, **kwargs):
        with sqlite3.connect(DB_PATH) as conn:
            set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [user_id]
            conn.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
            conn.commit()

    def get_referral_count(self, user_id):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT count FROM referrals WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return row[0] if row else 0

    def get_all_users(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM users")
            return [dict(row) for row in cursor.fetchall()]

    def cache_rates(self, rates):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO cache (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', ('exchange_rates', json.dumps(rates), datetime.now().isoformat()))
            conn.commit()

    def get_cached_rates(self):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT value FROM cache WHERE key = 'exchange_rates'")
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None

    def log_action(self, user_id, action):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                INSERT INTO logs (timestamp, user_id, action)
                VALUES (?, ?, ?)
            ''', (datetime.now().isoformat(), user_id, action))
            conn.commit()

    def mark_payment_as_processed(self, tx_hash):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                INSERT OR IGNORE INTO payment_logs (tx_hash, processed_at)
                VALUES (?, ?)
            ''', (tx_hash, datetime.now().isoformat()))
            conn.commit()

    def is_payment_processed(self, tx_hash):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT 1 FROM payment_logs WHERE tx_hash = ?", (tx_hash,))
            return cursor.fetchone() is not None

    def add_reminder(self, user_id, text, time):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                INSERT INTO reminders (user_id, text, time)
                VALUES (?, ?, ?)
            ''', (user_id, text, time))
            conn.commit()

    def get_reminders(self, user_id):
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM reminders WHERE user_id = ?", (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def add_subscription(self, user_id, name, renewal_date):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                INSERT INTO subscriptions (user_id, name, renewal_date)
                VALUES (?, ?, ?)
            ''', (user_id, name, renewal_date))
            conn.commit()

    def get_subscriptions(self, user_id):
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM subscriptions WHERE user_id = ?", (user_id,))
            return [dict(row) for row in cursor.fetchall()]

db = Database()
