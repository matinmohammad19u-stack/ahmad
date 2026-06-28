import sqlite3

db = sqlite3.connect("game.db", check_same_thread=False)
cursor = db.cursor()


# =========================
# GET PLAYER
# =========================
def get_player(user_id):
    cursor.execute("""
        SELECT character, level
        FROM players
        WHERE user_id = ?
    """, (user_id,))
    return cursor.fetchone()


# =========================
# UPDATE AWAKENING STATE
# =========================
def set_awakening(user_id, status: int):
    cursor.execute("""
        UPDATE players
        SET awakening = ?
        WHERE user_id = ?
    """, (status, user_id))

    db.commit()


# =========================
# CHECK AWAKENING
# =========================
def check_awakening(user_id, mastery: int):
    player = get_player(user_id)

    if not player:
        return "❌ پلیر پیدا نشد"

    character, level = player

    # شرط اویکنینگ
    required_mastery = 100

    if mastery < required_mastery:
        return f"❌ هنوز اویکنینگ باز نشده (نیاز: {required_mastery})"

    # فعال کردن اویکنینگ
    set_awakening(user_id, 1)

    return f"🔥 {character} Awakening فعال شد!"