from database import db, cursor

def get_player(user_id):
    cursor.execute("""
        SELECT character, level FROM players WHERE user_id = ?
    """, (user_id,))
    return cursor.fetchone()

def set_awakening(user_id, status: int):
    cursor.execute("""
        UPDATE players SET awakening = ? WHERE user_id = ?
    """, (status, user_id))
    db.commit()

def check_awakening(user_id, mastery: int):
    player = get_player(user_id)
    if not player:
        return "❌ پلیر پیدا نشد"

    character, level = player

    if mastery < 100:
        return f"❌ هنوز اویکنینگ باز نشده (نیاز: 100)"

    set_awakening(user_id, 1)
    return f"🔥 {character} Awakening فعال شد!"
