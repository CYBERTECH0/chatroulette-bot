# premium_logic.py — Telegram Stars Edition (FINAL)

import time
import sqlite3
from config import DB_PATH, FEATURE_PRICES

def _connect():
    return sqlite3.connect(DB_PATH)

# -------------------------------
# STAR BALANCE
# -------------------------------

def get_stars(user_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT stars FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def add_stars(user_id, amount):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET stars = stars + ? WHERE id=?", (amount, user_id))
    conn.commit()
    conn.close()
    log_transaction(user_id, amount, "stars_added")

# -------------------------------
# SPENDING (just in case)
# -------------------------------

def charge_stars(user_id, feature_name):
    price = FEATURE_PRICES.get(feature_name)
    if price is None:
        return False
    current = get_stars(user_id)
    if current < price:
        return False

    conn = _connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET stars = stars - ? WHERE id=?", (price, user_id))
    conn.commit()
    conn.close()

    log_transaction(user_id, -price, f"buy_{feature_name}")
    return True

# -------------------------------
# VIP LOGIC
# -------------------------------

def has_vip(user_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT vip_until FROM premium WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    return row[0] > int(time.time())

def grant_vip(user_id, days=7):
    now = int(time.time())
    vip_until = now + days * 86400
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO premium (user_id, vip_until)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET vip_until = excluded.vip_until
    """, (user_id, vip_until))
    conn.commit()
    conn.close()
    log_transaction(user_id, 0, f"vip_granted_{days}_days")

# -------------------------------
# UNLOCKS (VIP-only features)
# -------------------------------

def unlock_gender_filter(user_id):
    log_transaction(user_id, 0, "unlock_gender_filter")

def unlock_region_filter(user_id):
    log_transaction(user_id, 0, "unlock_region_filter")

def unlock_priority(user_id):
    log_transaction(user_id, 0, "unlock_priority")

def unlock_rematch(user_id):
    log_transaction(user_id, 0, "unlock_rematch")

def unlock_vip(user_id):
    log_transaction(user_id, 0, "unlock_vip_menu")

# -------------------------------
# TRANSACTIONS LOG
# -------------------------------

def log_transaction(user_id, amount, feature):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transactions (user_id, amount, feature, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, amount, feature, int(time.time())))
    conn.commit()
    conn.close()
