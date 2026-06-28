from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from database import db, cursor
from config import TOKEN
from character_select import assign_random_character


# =========================
# START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username or "no_username"

    cursor.execute("""
        INSERT OR IGNORE INTO players (user_id, username)
        VALUES (?, ?)
    """, (user.id, username))

    db.commit()

    await update.message.reply_text(
        "🏴‍☠️ به One Piece RPG خوش اومدی!\n"
        "برای گرفتن شخصیت دستور /character رو بزن."
    )


# =========================
# CHARACTER COMMAND
# =========================
async def character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    cursor.execute("""
        SELECT level, xp, money, character, hp, max_hp
        FROM players
        WHERE user_id=?
    """, (user.id,))

    data = cursor.fetchone()

    # اگر پلیر جدید بود
    if not data:
        level, xp, money, character_name, hp, max_hp = 1, 0, 0, None, 0, 0

        cursor.execute("""
            INSERT OR IGNORE INTO players (user_id, username)
            VALUES (?, ?)
        """, (user.id, user.username or "no_username"))
        db.commit()

    else:
        level, xp, money, character_name, hp, max_hp = data

    # اگر هنوز شخصیت نداره → بده
    if not character_name:
        name, stats = assign_random_character(user.id)

        character_name = name
        hp = stats["hp"]
        max_hp = stats["hp"]

        cursor.execute("""
        UPDATE players
        SET character = ?, hp = ?, max_hp = ?
        WHERE user_id = ?
        """, (name, hp, max_hp, user.id))

        db.commit()

    await update.message.reply_text(
        f"""👤 {user.first_name}

🎭 شخصیت: {character_name}
⭐ لول: {level}
✨ XP: {xp}
💰 پول: {money}

❤️ HP: {hp}/{max_hp}"""
    )


# =========================
# MAIN BOT
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("character", character))

print("Bot Online...")
app.run_polling()