# features.py — premium feature logic (final stable version)

from database import add_to_queue, update_user_state
from premium_logic import has_vip, charge_stars
from config import FEATURE_PRICES


# ------------------------------------
# 1. Gender Filter
# ------------------------------------

def apply_gender_filter(user_id, target_gender):
    """
    If VIP → free.
    If not VIP → charges stars.
    Returns dict: {success: bool, gender: str}
    """

    if has_vip(user_id):
        return {"success": True, "gender": target_gender}

    if charge_stars(user_id, "gender_filter"):
        return {"success": True, "gender": target_gender}

    return {"success": False, "error": "not_enough_stars"}


# ------------------------------------
# 2. Region Filter
# ------------------------------------

def apply_region_filter(user_id, target_region):
    """
    Same logic as gender filter.
    """
    if has_vip(user_id):
        return {"success": True, "region": target_region}

    if charge_stars(user_id, "region_filter"):
        return {"success": True, "region": target_region}

    return {"success": False, "error": "not_enough_stars"}


# ------------------------------------
# 3. Priority Queue
# ------------------------------------

def enter_priority_queue(user_id):
    """
    VIP = priority 10 (top).
    Normal user = priority 5 (paid).
    """
    if has_vip(user_id):
        priority = 10
    else:
        if not charge_stars(user_id, "priority"):
            return {"success": False, "error": "not_enough_stars"}
        priority = 5

    add_to_queue(user_id, priority)
    update_user_state(user_id, "searching")

    return {"success": True, "priority": priority}


# ------------------------------------
# 4. Instant Rematch
# ------------------------------------

def instant_rematch(user_id):
    """
    Lets user instantly re-enter queue after disconnect.
    VIP = free.
    Normal = pay stars.
    """
    if has_vip(user_id):
        return {"success": True}

    if charge_stars(user_id, "instant_rematch"):
        return {"success": True}

    return {"success": False, "error": "not_enough_stars"}


# ------------------------------------
# 5. VIP Benefits (for UI / future)
# ------------------------------------

def vip_benefits(user_id):
    """
    Optional return for UI:
    """
    return {
        "priority_queue": True,
        "free_filters": True,
        "free_rematch": True,
        "badge": True
    }
