import random
import sqlite3
from characters import characters

db = sqlite3.connect("game.db", check_same_thread=False)
cursor = db.cursor()


def assign_random_character(user_id: int):
    chosen_name = random.choice(list(characters.keys()))
    chosen = characters[chosen_name]

    hp = chosen["stats"]["hp"]

    # اگر کاربر وجود نداشت اول بساز
    cursor.execute("""
    INSERT OR IGNORE INTO players (user_id)
    VALUES (?)
    """, (user_id,))

    # آپدیت شخصیت
    cursor.execute("""
    UPDATE players
    SET character = ?, hp = ?, max_hp = ?
    WHERE user_id = ?
    """, (chosen_name, hp, hp, user_id))

    db.commit()

    return chosen_name, chosen["stats"]