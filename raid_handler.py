from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import cursor
from raid_bigmom import bigmom
from raid_kaido import kaido
from raid_blackbeard import blackbeard

online_users = {}

async def raid(update, context):
    user = update.effective_user
    cursor.execute("SELECT character, hp FROM players WHERE user_id=?", (user.id,))
    data = cursor.fetchone()
    if not data or not data[0]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    if data[1] <= 0:
        await update.message.reply_text("❌ HP نداری!")
        return
    keyboard = [
        [InlineKeyboardButton("👑 Big Mom", callback_data="raid_bigmom")],
        [InlineKeyboardButton("🐉 Kaido", callback_data="raid_kaido")],
        [InlineKeyboardButton("☠️ Blackbeard", callback_data="raid_blackbeard")],
    ]
    await update.message.reply_text("⚔️ Raid Boss:", reply_markup=InlineKeyboardMarkup(keyboard))

async def raid_callback(update, context):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    raids = {"raid_bigmom": bigmom, "raid_kaido": kaido, "raid_blackbeard": blackbeard}
    func = raids.get(query.data)
    result = func(user.id) if func else "❌ خطا"
    await query.edit_message_text(result[:4000])
