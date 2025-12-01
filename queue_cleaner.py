# queue_cleaner.py — removes dead, inactive, or invalid users from queue

import time
from database import (
    get_queue,
    get_user_state,
    get_partner,
    remove_from_queue,
    get_last_active,
)

INACTIVE_TIMEOUT = 30      # seconds — user inactive → removed
BROKEN_LINK_TIMEOUT = 10   # reserved for future


async def clean_queue(bot):
    """
    Runs every 5 seconds (scheduled in bot.py).
    Removes:
    - inactive users
    - users already chatting
    - users with invalid partner links
    """

    now = int(time.time())
    queue = get_queue()

    for user_id in queue:
        # -------------------------
        # 1. INACTIVE USER
        # -------------------------
        last = get_last_active(user_id)
        if last and (now - last) > INACTIVE_TIMEOUT:
            remove_from_queue(user_id)
            try:
                await bot.send_message(
                    user_id,
                    "⚠️ Вы были удалены из очереди из-за неактивности."
                )
            except:
                pass
            continue

        # -------------------------
        # 2. USER IS ALREADY CHATTING → shouldn't be in queue
        # -------------------------
        state = get_user_state(user_id)
        if state == "chatting":
            remove_from_queue(user_id)
            continue

        # -------------------------
        # 3. BROKEN PARTNER LINK (rare)
        # -------------------------
        partner = get_partner(user_id)
        if partner and partner not in queue and state != "chatting":
            remove_from_queue(user_id)
            continue
