# setgender.py — user profile settings (gender + region)

from database import update_gender, update_region

async def ask_gender(update, context):
    kb = [
        ["👨 Мужчина", "👩 Женщина"],
        ["❌ Пропустить"]
    ]
    await update.message.reply_text(
        "Выберите ваш пол:",
        reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True, resize_keyboard=True)
    )
    return 1


async def save_gender(update, context):
    text = update.message.text

    if text == "👨 Мужчина":
        update_gender(update.effective_user.id, "male")
    elif text == "👩 Женщина":
        update_gender(update.effective_user.id, "female")
    else:
        update_gender(update.effective_user.id, None)

    await update.message.reply_text("Пол сохранён!")
    return ConversationHandler.END
    