# config.py — Telegram Stars version (FINAL)

import os
from dotenv import load_dotenv

load_dotenv()

# BOT TOKEN from .env
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Database
DB_PATH = "chatroulette.db"

# Matching
MATCH_CHECK_INTERVAL = 1
MAX_QUEUE_WAIT = 60

# Premium feature star costs (what user spends)
FEATURE_PRICES = {
    "gender_filter": 5,
    "region_filter": 3,
    "priority": 2,
    "instant_rematch": 1,
    "vip_week": 10,
}
