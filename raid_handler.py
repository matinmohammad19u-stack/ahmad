from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import db, cursor
from raid_bigmom import bigmom
from raid_kaido import kaido
from raid_blackbeard import blackbeard


# =========================
# RAID MENU
# =========================
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


# =========================
# RAID CALLBACK
# =========================
async def raid_callback(update, context):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    raids = {
        "raid_bigmom": bigmom,
        "raid_kaido": kaido,
        "raid_blackbeard": blackbeard,
    }

    func = raids.get(query.data)
    if not func:
        await query.edit_message_text("❌ خطا")
        return

    # اجرای raid و گرفتن نتیجه
    result, won = func(user.id)

    # اگر برد → +15 لول
    if won:
        cursor.execute("""
            UPDATE players SET level=level+15, xp=0
            WHERE user_id=?
        """, (user.id,))
        db.commit()
        result += "\n\n🎉 +15 لول!"

    await query.edit_message_text(result[:4000])
