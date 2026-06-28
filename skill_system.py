import sqlite3
from skills import skills  # همون skills دیتات

db = sqlite3.connect("game.db", check_same_thread=False)
cursor = db.cursor()


# =========================
# INIT TABLE (اگر نبود)
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS skill_mastery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    character TEXT,
    skill_name TEXT,
    mastery INTEGER DEFAULT 0,
    unlocked INTEGER DEFAULT 0
)
""")

db.commit()


# =========================
# GET AVAILABLE SKILLS
# =========================
def get_available_skills(user_id, character_name, form="Base"):
    if character_name not in skills:
        return []

    form_skills = skills[character_name].get(form, [])

    result = []

    for sk in form_skills:
        cursor.execute("""
            SELECT mastery, unlocked FROM skill_mastery
            WHERE user_id=? AND character=? AND skill_name=?
        """, (user_id, character_name, sk["name"]))

        data = cursor.fetchone()

        if not data:
            mastery = 0
            unlocked = 0
        else:
            mastery, unlocked = data

        result.append({
            "name": sk["name"],
            "damage": sk["damage"],
            "mastery": mastery,
            "unlocked": bool(unlocked)
        })

    return result


# =========================
# ADD MASTERY (در فایت استفاده میشه)
# =========================
def add_mastery(user_id, character, skill_name, amount=10):
    cursor.execute("""
        SELECT mastery, unlocked FROM skill_mastery
        WHERE user_id=? AND character=? AND skill_name=?
    """, (user_id, character, skill_name))

    data = cursor.fetchone()

    if not data:
        cursor.execute("""
            INSERT INTO skill_mastery (user_id, character, skill_name, mastery, unlocked)
            VALUES (?, ?, ?, ?, 0)
        """, (user_id, character, skill_name, amount))
    else:
        mastery, unlocked = data
        mastery += amount

        # unlock condition
        if mastery >= 100:
            unlocked = 1

        cursor.execute("""
            UPDATE skill_mastery
            SET mastery=?, unlocked=?
            WHERE user_id=? AND character=? AND skill_name=?
        """, (mastery, unlocked, user_id, character, skill_name))

    db.commit()