from database import db, cursor


def get_mastery(user_id, character, skill_name):
    # FIX: اضافه کردن character به WHERE
    cursor.execute("""
        SELECT mastery, unlocked FROM skill_mastery
        WHERE user_id = ? AND character = ? AND skill_name = ?
    """, (user_id, character, skill_name))
    data = cursor.fetchone()
    return data if data else (0, 0)


def add_mastery(user_id, character, skill_name, amount=1):
    # FIX: اضافه کردن character به INSERT و UPDATE
    mastery, unlocked = get_mastery(user_id, character, skill_name)
    new_mastery = min(100, mastery + amount)  # FIX: clamp به 100
    new_unlocked = 1 if new_mastery >= 100 else unlocked

    cursor.execute("""
        INSERT INTO skill_mastery (user_id, character, skill_name, mastery, unlocked)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, character, skill_name)
        DO UPDATE SET mastery = ?, unlocked = ?
    """, (user_id, character, skill_name, new_mastery, new_unlocked,
          new_mastery, new_unlocked))
    db.commit()


def is_unlocked(user_id, character, skill_name):
    # FIX: اضافه کردن character
    cursor.execute("""
        SELECT unlocked FROM skill_mastery
        WHERE user_id = ? AND character = ? AND skill_name = ?
    """, (user_id, character, skill_name))
    data = cursor.fetchone()
    return bool(data and data[0] == 1)


def unlock_skill(user_id, character, skill_name):
    # FIX: اضافه کردن character
    cursor.execute("""
        UPDATE skill_mastery SET unlocked = 1
        WHERE user_id = ? AND character = ? AND skill_name = ?
    """, (user_id, character, skill_name))
    db.commit()
