from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from database import db, cursor
import os
TOKEN = os.environ.get("TOKEN")
from character_select import assign_random_character
from characters import characters


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username or "no_username"
    cursor.execute("INSERT OR IGNORE INTO players (user_id, username) VALUES (?, ?)", (user.id, username))
    db.commit()
    await update.message.reply_text(
        "🏴‍☠️ به One Piece RPG خوش اومدی!\n"
        "برای گرفتن شخصیت دستور /character رو بزن.\n"
        "برای انتخاب شخصیت /character_select رو بزن."
    )


async def character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute("SELECT level, xp, money, character, hp, max_hp FROM players WHERE user_id=?", (user.id,))
    data = cursor.fetchone()
    if not data or not data[3]:
        await update.message.reply_text("❌ هنوز شخصیت نداری! دستور /character_select رو بزن.")
        return
    level, xp, money, character_name, hp, max_hp = data
    await update.message.reply_text(
        f"👤 {user.first_name}\n\n"
        f"🎭 شخصیت: {character_name}\n"
        f"⭐ لول: {level}\n"
        f"✨ XP: {xp}\n"
        f"💰 پول: {money}\n\n"
        f"❤️ HP: {hp}/{max_hp}"
    )


async def character_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # ببین قبلاً کاراکتر داره؟
    cursor.execute("SELECT character FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if row and row[0]:
        await update.message.reply_text(f"✅ تو قبلاً شخصیت {row[0]} رو گرفتی!")
        return

    # کاراکترهای موجود
    cursor.execute("SELECT name FROM available_characters")
    available = [r[0] for r in cursor.fetchall()]

    if not available:
        await update.message.reply_text("❌ همه شخصیت‌ها گرفته شدن!")
        return

    # دکمه‌ها
    keyboard = []
    for name in available:
        keyboard.append([InlineKeyboardButton(name, callback_data=f"pick_{name}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎭 یه شخصیت انتخاب کن:", reply_markup=reply_markup)


async def pick_character_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    # ببین قبلاً کاراکتر داره؟
    cursor.execute("SELECT character FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if row and row[0]:
        await query.edit_message_text(f"✅ تو قبلاً شخصیت {row[0]} رو گرفتی!")
        return

    chosen_name = query.data.replace("pick_", "")

    # ببین هنوز موجوده؟
    cursor.execute("SELECT name FROM available_characters WHERE name=?", (chosen_name,))
    if not cursor.fetchone():
        await query.edit_message_text("❌ این شخصیت قبلاً گرفته شده! دوباره /character_select بزن.")
        return

    chosen = characters[chosen_name]
    hp = chosen["stats"]["hp"]

    cursor.execute("INSERT OR IGNORE INTO players (user_id, username) VALUES (?, ?)", (user.id, user.username or "no_username"))
    cursor.execute("UPDATE players SET character=?, hp=?, max_hp=? WHERE user_id=?", (chosen_name, hp, hp, user.id))
    cursor.execute("DELETE FROM available_characters WHERE name=?", (chosen_name,))
    db.commit()

    await query.edit_message_text(
        f"🎉 تبریک {user.first_name}!\n\n"
        f"🎭 شخصیت تو: {chosen_name}\n"
        f"❤️ HP: {hp}"
    )


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("character", character))
app.add_handler(CommandHandler("character_select", character_select))
app.add_handler(CallbackQueryHandler(pick_character_callback, pattern="^pick_"))

print("Bot Online...")
app.run_polling()
