# matchmaking.py — premium-aware + gender-aware match engine (FINAL)

import asyncio
import random

from database import (
    get_queue,
    remove_from_queue,
    set_partner,
    clear_partner,
    update_user_state,
    get_partner,
    add_to_queue,
    get_user_gender
)

from psych_core.psych_pipeline import run_psychology, after_match_psych
from psych_core.engagement_model import register_action


# ---------------------------------------------------------
# Prepare user
# ---------------------------------------------------------

def prepare_for_search(user_id):
    remove_from_queue(user_id)        # avoid duplicates
    clear_partner(user_id)
    update_user_state(user_id, "searching")
    register_action(user_id, "search")


# ---------------------------------------------------------
# Gender compatibility
# ---------------------------------------------------------

def compatible(u1, u2):
    """
    Basic gender filter logic.
    Expand later with region, VIP, custom filters.
    """

    g1 = get_user_gender(u1)
    g2 = get_user_gender(u2)

    # If nobody selected gender -> fine
    if not g1 or not g2:
        return True

    # If both selected gender -> forbids same-gender (unless you want to allow)
    if g1 == g2:
        return False

    return True


# ---------------------------------------------------------
# Main matchmaker
# ---------------------------------------------------------

async def matchmaker(bot):
    queue = get_queue()
    if len(queue) < 2:
        return

    u1 = queue[0]
    partner = None

    # Find someone compatible
    for u2 in queue[1:]:
        if compatible(u1, u2):
            partner = u2
            break

    if not partner:
        return  # no match possible yet

    u2 = partner

    # PRE-PSYCHOLOGY
    await asyncio.gather(
        run_psychology(bot, u1),
        run_psychology(bot, u2)
    )

    # realism
    await asyncio.sleep(random.uniform(0.03, 0.08))

    # safety re-check
    queue = get_queue()
    if u1 not in queue or u2 not in queue:
        return

    # remove from queue
    remove_from_queue(u1)
    remove_from_queue(u2)

    # connect users
    set_partner(u1, u2)
    set_partner(u2, u1)

    update_user_state(u1, "chatting")
    update_user_state(u2, "chatting")

    register_action(u1, "match")
    register_action(u2, "match")

    # POST-MATCH "alive" lines
    await asyncio.gather(
        after_match_psych(bot, u1),
        after_match_psych(bot, u2)
    )


# ---------------------------------------------------------
# Disconnect logic
# ---------------------------------------------------------

async def disconnect_users(bot, user_id):
    partner = get_partner(user_id)

    register_action(user_id, "disconnect")

    if not partner or partner == user_id:
        update_user_state(user_id, "idle")
        await bot.send_message(user_id, "❌ Вы отключились.")
        return

    # notify both
    await bot.send_message(user_id, "❌ Вы отключились.")
    await bot.send_message(partner, "⚠️ Собеседник отключился.")

    # reset
    clear_partner(user_id)
    clear_partner(partner)

    update_user_state(user_id, "idle")
    update_user_state(partner, "idle")

    register_action(partner, "partner_disconnect")
