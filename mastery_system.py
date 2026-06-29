from database import db, cursor

def get_mastery(user_id, skill_name):
    cursor.execute("""
        SELECT mastery, unlocked FROM skill_mastery
        WHERE user_id = ? AND skill_name = ?
    """, (user_id, skill_name))
    data = cursor.fetchone()
    return data if data else (0, 0)

def add_mastery(user_id, skill_name, amount=1):
    mastery, unlocked = get_mastery(user_id, skill_name)
    if mastery == 0 and unlocked == 0:
        cursor.execute("""
            INSERT INTO skill_mastery (user_id, skill_name, mastery, unlocked)
            VALUES (?, ?, ?, 0)
        """, (user_id, skill_name, amount))
    else:
        cursor.execute("""
            UPDATE skill_mastery SET mastery = mastery + ?
            WHERE user_id = ? AND skill_name = ?
        """, (amount, user_id, skill_name))
    db.commit()

def is_unlocked(user_id, skill_name):
    cursor.execute("""
        SELECT unlocked FROM skill_mastery WHERE user_id = ? AND skill_name = ?
    """, (user_id, skill_name))
    data = cursor.fetchone()
    return data and data[0] == 1

def unlock_skill(user_id, skill_name):
    cursor.execute("""
        UPDATE skill_mastery SET unlocked = 1 WHERE user_id = ? AND skill_name = ?
    """, (user_id, skill_name))
    db.commit()
