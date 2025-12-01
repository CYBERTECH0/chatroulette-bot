# payment_engine.py — Telegram Stars payments + premium handling

import time
from premium_logic import (
    grant_vip,
    log_transaction
)
from config import (
    GENDER_FILTER_COST,
    REGION_FILTER_COST,
    PRIORITY_QUEUE_COST,
    INSTANT_REMATCH_COST,
    VIP_COST_WEEK
)


# ------------------------------
# FEATURE PRICE MAP
# ------------------------------

FEATURE_PRICES = {
    "gender_filter": GENDER_FILTER_COST,
    "region_filter": REGION_FILTER_COST,
    "priority": PRIORITY_QUEUE_COST,
    "instant_rematch": INSTANT_REMATCH_COST,
    "vip_week": VIP_COST_WEEK
}


# ------------------------------
# 1. Validate payment from Telegram
# ------------------------------

def verify_star_payment(amount_sent, feature_name):
    """
    Makes sure the user sent the correct amount of Stars.
    Prevents cheating.
    """
    if feature_name not in FEATURE_PRICES:
        return False

    required = FEATURE_PRICES[feature_name]
    return amount_sent >= required


# ------------------------------
# 2. Process payment
# ------------------------------

def process_payment(user_id, amount, feature_name):
    """
    Called right after Telegram confirms payment.
    It updates VIP, grants features, and logs the transaction.
    """

    # Validate
    if not verify_star_payment(amount, feature_name):
        return {"success": False, "error": "Invalid payment"}

    # VIP purchase
    if feature_name == "vip_week":
        grant_vip(user_id, days=7)

    # Log in DB
    log_transaction(user_id, amount, feature_name)

    return {"success": True, "feature": feature_name}


# ------------------------------
# 3. Inline button payload builder
# ------------------------------

def get_payment_description(feature_name):
    """
    Returns a clean description for payment dialogs.
    """
    if feature_name == "gender_filter":
        return "Unlock Gender Filter (Stars)"
    if feature_name == "region_filter":
        return "Unlock Region Filter (Stars)"
    if feature_name == "priority":
        return "Priority Queue (Stars)"
    if feature_name == "instant_rematch":
        return "Instant Rematch (Stars)"
    if feature_name == "vip_week":
        return "VIP (7 Days)"
    return "Purchase"
