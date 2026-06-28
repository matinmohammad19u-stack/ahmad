import random
from characters import characters
from database import db, cursor

cursor.execute("""
CREATE TABLE IF NOT EXISTS available_characters (
    name TEXT PRIMARY KEY
)
""")
db.commit()

cursor.execute("SELECT COUNT(*) FROM available_characters")
count = cursor.fetchone()[0]
if count == 0:
    for name in characters.keys():
        cursor.execute("INSERT OR IGNORE INTO available_characters (name) VALUES (?)", (name,))
    db.commit()


def assign_random_character(user_id: int):
    cursor.execute("SELECT character FROM players WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row and row[0]:
        name = row[0]
        return name, characters[name]["stats"]

    cursor.execute("SELECT name FROM available_characters")
    available = [r[0] for r in cursor.fetchall()]

    if not available:
        return None, None

    chosen_name = random.choice(available)
    chosen = characters[chosen_name]
    hp = chosen["stats"]["hp"]

    cursor.execute("INSERT OR IGNORE INTO players (user_id) VALUES (?)", (user_id,))
    cursor.execute("UPDATE players SET character=?, hp=?, max_hp=? WHERE user_id=?", (chosen_name, hp, hp, user_id))
    cursor.execute("DELETE FROM available_characters WHERE name=?", (chosen_name,))
    db.commit()

    return chosen_name, chosen["stats"]
