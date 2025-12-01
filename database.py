# database.py — SQLite database layer for ChatRoulette

import sqlite3
from time import time
from config import DB_PATH


# ---------------------------------------------------------
# INTERNAL CONNECTION
# ---------------------------------------------------------

def _connect():
    return sqlite3.connect(DB_PATH)


# ---------------------------------------------------------
# INIT DATABASE STRUCTURE
# ---------------------------------------------------------

def init_db():
    conn = _connect()
    cur = conn.cursor()

    # USERS TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            gender TEXT,
            region TEXT,
            state TEXT,
            partner_id INTEGER,
            stars INTEGER DEFAULT 0,
            vip INTEGER DEFAULT 0,
            last_active INTEGER
        )
    """)

    # MATCHMAKING QUEUE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            user_id INTEGER PRIMARY KEY,
            priority INTEGER DEFAULT 0,
            timestamp INTEGER
        )
    """)

    # VIP INFO
    cur.execute("""
        CREATE TABLE IF NOT EXISTS premium (
            user_id INTEGER PRIMARY KEY,
            vip_until INTEGER
        )
    """)

    # SESSIONS (optional analytics)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1 INTEGER,
            user2 INTEGER,
            started_at INTEGER
        )
    """)

    # TRANSACTION LOG
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            feature TEXT,
            timestamp INTEGER
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# USER MANAGEMENT
# ---------------------------------------------------------

def create_user(user_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users (id, state, last_active) VALUES (?, 'idle', ?)",
        (user_id, int(time()))
    )
    conn.commit()
    conn.close()


def update_last_active(user_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET last_active=? WHERE id=?",
        (int(time()), user_id)
    )
    conn.commit()
    conn.close()


def get_last_active(user_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT last_active FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0


def update_user_state(user_id, state):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET state=?, last_active=? WHERE id=?",
        (state, int(time()), user_id)
    )
    conn.commit()
    conn.close()


def get_user_state(user_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT state FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


# ---------------------------------------------------------
# PARTNER SYSTEM
# ---------------------------------------------------------

def set_partner(user_id, partner_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET partner_id=? WHERE id=?", (partner_id, user_id))
    conn.commit()
    conn.close()


def clear_partner(user_id):
    set_partner(user_id, None)


def get_partner(user_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT partner_id FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


# ---------------------------------------------------------
# GENDER & REGION FIELDS
# ---------------------------------------------------------

def update_gender(user_id, gender):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET gender=? WHERE id=?", (gender, user_id))
    conn.commit()
    conn.close()


def update_region(user_id, region):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET region=? WHERE id=?", (region, user_id))
    conn.commit()
    conn.close()


def get_user_gender(user_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT gender FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


# ---------------------------------------------------------
# MATCHMAKING QUEUE
# ---------------------------------------------------------

def add_to_queue(user_id, priority=0):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO queue (user_id, priority, timestamp) VALUES (?, ?, ?)",
        (user_id, priority, int(time()))
    )
    conn.commit()
    conn.close()


def remove_from_queue(user_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM queue WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


def get_queue():
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id FROM queue
        ORDER BY priority DESC, timestamp ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]


# ---------------------------------------------------------
# SESSION LOG
# ---------------------------------------------------------

def create_session(user1, user2):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (user1, user2, started_at) VALUES (?, ?, ?)",
        (user1, user2, int(time()))
    )
    conn.commit()
    conn.close()
