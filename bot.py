# bot.py — Telegram Stars VIP System (FINAL CLEAN A-MODEL)

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN
from database import (
    init_db,
    create_user,
    add_to_queue,
    get_partner,
    get_user_state,
    update_gender,
    update_last_active,
)

from matchmaking import prepare_for_search, matchmaker, disconnect_users
from premium_logic import has_vip, grant_vip
from queue_cleaner import clean_queue


# ---------------------------------------------------------
# START
# ---------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    create_user(user)
    update_last_active(user)

    await update.message.reply_text(
        "🎭 Добро пожаловать в ChatRoulette!\n\n"
        "/gender — выбрать пол\n"
        "/search — поиск собеседника\n"
        "/premium — премиум меню (VIP)"
    )


# ---------------------------------------------------------
# SEARCH
# ---------------------------------------------------------

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    update_last_active(user)

    prepare_for_search(user)
    add_to_queue(user)

    await update.message.reply_text("🔎 Поиск собеседника...")


# ---------------------------------------------------------
# NEXT
# ---------------------------------------------------------

async def next_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id

    await disconnect_users(context.bot, user)
    prepare_for_search(user)
    add_to_queue(user)

    await update.message.reply_text("🔄 Ищем следующего...")


# ---------------------------------------------------------
# STOP
# ---------------------------------------------------------

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    await disconnect_users(context.bot, user)


# ---------------------------------------------------------
# PREMIUM MENU
# ---------------------------------------------------------

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    vip = has_vip(user)

    kb = []

    if not vip:
        kb.extend([
            [InlineKeyboardButton("💎 VIP 7 дней — 50⭐", callback_data="buy_vip_7")],
            [InlineKeyboardButton("💠 VIP 30 дней — 150⭐", callback_data="buy_vip_30")],
            [InlineKeyboardButton("🔥 VIP 90 дней — 350⭐", callback_data="buy_vip_90")],
            [InlineKeyboardButton("👑 VIP Навсегда — 1200⭐", callback_data="buy_vip_life")],
        ])
    else:
        kb.append([InlineKeyboardButton("🟢 VIP активен", callback_data="vip_active")])

    kb.extend([
        [InlineKeyboardButton("⭐ Гендер-фильтр (VIP)", callback_data="gf")],
        [InlineKeyboardButton("🌍 Регион-фильтр (VIP)", callback_data="rf")],
        [InlineKeyboardButton("⚡ Приоритет (VIP)", callback_data="pr")],
        [InlineKeyboardButton("⏩ Рематч (VIP)", callback_data="rm")],
    ])

    await update.message.reply_text(
        f"💼 Премиум меню\n\n"
        f"VIP статус: {'🟢 Активен' if vip else '🔴 Нет'}",
        reply_markup=InlineKeyboardMarkup(kb),
    )


# ---------------------------------------------------------
# CALLBACKS
# ---------------------------------------------------------

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    user = q.from_user.id

    await q.answer()
    vip = has_vip(user)

    # Buy VIP options
    if data == "buy_vip_7":
        await send_vip_invoice(user, context, 50, "vip_7", "VIP 7 дней")
        await q.edit_message_text("💎 Открываю оплату...")
        return

    if data == "buy_vip_30":
        await send_vip_invoice(user, context, 150, "vip_30", "VIP 30 дней")
        await q.edit_message_text("💎 Открываю оплату...")
        return

    if data == "buy_vip_90":
        await send_vip_invoice(user, context, 350, "vip_90", "VIP 90 дней")
        await q.edit_message_text("💎 Открываю оплату...")
        return

    if data == "buy_vip_life":
        await send_vip_invoice(user, context, 1200, "vip_life", "VIP Навсегда")
        await q.edit_message_text("💎 Открываю оплату...")
        return

    if data == "vip_active":
        await q.answer("VIP уже активен.", show_alert=True)
        return

    # Gender change
    if data == "set_gender_male":
        update_gender(user, "male")
        await q.edit_message_text("Ваш пол: 👨 Мужчина")
        return

    if data == "set_gender_female":
        update_gender(user, "female")
        await q.edit_message_text("Ваш пол: 👩 Женщина")
        return

    # VIP features
    if data in ["gf", "rf", "pr", "rm"]:
        if vip:
            msg = {
                "gf": "⭐ Гендер-фильтр активирован.",
                "rf": "🌍 Регион-фильтр активирован.",
                "pr": "⚡ Приоритет включён.",
                "rm": "⏩ Рематч активирован.",
            }[data]
            await q.edit_message_text(msg)
        else:
            await q.edit_message_text("❌ Доступно только VIP.")
        return


# ---------------------------------------------------------
# Send Invoice
# ---------------------------------------------------------

async def send_vip_invoice(user_id, context, stars, payload, label):
    amount = stars  # XTR subunits

    prices = [LabeledPrice(label=label, amount=amount)]

    await context.bot.send_invoice(
        chat_id=user_id,
        title=label,
        description="VIP доступ ChatRoulette",
        payload=payload,
        provider_token="",   # required for Telegram Stars
        currency="XTR",
        prices=prices,
    )


# ---------------------------------------------------------
# Payment Handlers
# ---------------------------------------------------------

async def precheckout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)


async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    user = update.effective_user.id

    if payment.currency != "XTR":
        return

    payload = payment.invoice_payload

    if payload == "vip_7":
        grant_vip(user, 7)
    elif payload == "vip_30":
        grant_vip(user, 30)
    elif payload == "vip_90":
        grant_vip(user, 90)
    elif payload == "vip_life":
        grant_vip(user, 9999)

    await update.message.reply_text("💎 VIP активирован!")


# ---------------------------------------------------------
# Chat Relay
# ---------------------------------------------------------

async def chat_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.id
    if get_user_state(user) != "chatting":
        return

    partner = get_partner(user)
    if partner:
        await context.bot.send_message(partner, update.message.text)


# ---------------------------------------------------------
# Background Loops
# ---------------------------------------------------------

async def start_background(app):
    asyncio.create_task(match_loop(app))
    asyncio.create_task(clean_loop(app))


async def match_loop(app):
    while True:
        await matchmaker(app.bot)
        await asyncio.sleep(1)


async def clean_loop(app):
    while True:
        await clean_queue(app.bot)
        await asyncio.sleep(5)


# ---------------------------------------------------------
# Gender Menu
# ---------------------------------------------------------

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("♂️ Мужчина", callback_data="set_gender_male")],
        [InlineKeyboardButton("♀️ Женщина", callback_data="set_gender_female")],
    ]
    await update.message.reply_text("Выберите ваш пол:", reply_markup=InlineKeyboardMarkup(kb))


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():
    init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(start_background).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gender", gender))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("next", next_user))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("premium", premium))

    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(PreCheckoutQueryHandler(precheckout_handler))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_forward))

    print("ChatRoulette running…")
    app.run_polling()


if __name__ == "__main__":
    main()
