import sqlite3

db = sqlite3.connect("game.db", check_same_thread=False)
cursor = db.cursor()


# =========================
# GET MASTERY
# =========================
def get_mastery(user_id, skill_name):
    cursor.execute("""
        SELECT mastery, unlocked
        FROM skill_mastery
        WHERE user_id = ? AND skill_name = ?
    """, (user_id, skill_name))

    data = cursor.fetchone()

    if not data:
        return 0, 0

    return data


# =========================
# ADD MASTERY
# =========================
def add_mastery(user_id, skill_name, amount=1):
    mastery, unlocked = get_mastery(user_id, skill_name)

    if mastery == 0 and unlocked == 0:
        cursor.execute("""
            INSERT INTO skill_mastery (user_id, skill_name, mastery, unlocked)
            VALUES (?, ?, ?, ?)
        """, (user_id, skill_name, amount, 0))
    else:
        cursor.execute("""
            UPDATE skill_mastery
            SET mastery = mastery + ?
            WHERE user_id = ? AND skill_name = ?
        """, (amount, user_id, skill_name))

    db.commit()


# =========================
# CHECK UNLOCK
# =========================
def is_unlocked(user_id, skill_name):
    cursor.execute("""
        SELECT unlocked FROM skill_mastery
        WHERE user_id = ? AND skill_name = ?
    """, (user_id, skill_name))

    data = cursor.fetchone()

    return data and data[0] == 1


# =========================
# UNLOCK SKILL
# =========================
def unlock_skill(user_id, skill_name):
    cursor.execute("""
        UPDATE skill_mastery
        SET unlocked = 1
        WHERE user_id = ? AND skill_name = ?
    """, (user_id, skill_name))

    db.commit()