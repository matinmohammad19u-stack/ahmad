from database import db, cursor


def get_available_skills(user_id, character_name, skills_db, form="Base"):
    if character_name not in skills_db:
        return []

    form_skills = skills_db[character_name].get(form, [])
    result = []

    for sk in form_skills:
        cursor.execute("""
            SELECT mastery, unlocked
            FROM skill_mastery
            WHERE user_id=? AND character=? AND skill_name=?
        """, (user_id, character_name, sk["name"]))

        data = cursor.fetchone()
        mastery, unlocked = data if data else (0, 0)

        result.append({
            "name": sk["name"],
            "damage": sk["damage"],
            "mastery": mastery,
            "unlocked": bool(unlocked)
        })

    return result


def add_mastery(user_id, character, skill_name, amount=10):
    cursor.execute("""
        SELECT mastery, unlocked
        FROM skill_mastery
        WHERE user_id=? AND character=? AND skill_name=?
    """, (user_id, character, skill_name))

    data = cursor.fetchone()

    if data is None:
        cursor.execute("""
            INSERT INTO skill_mastery
            (user_id, character, skill_name, mastery, unlocked)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, character, skill_name, amount, 0))
    else:
        mastery, unlocked = data
        mastery += amount

        if mastery >= 100:
            unlocked = 1

        cursor.execute("""
            UPDATE skill_mastery
            SET mastery=?, unlocked=?
            WHERE user_id=? AND character=? AND skill_name=?
        """, (mastery, unlocked, user_id, character, skill_name))

    db.commit()
