from database import db, cursor

def change_form(user_id: int, form_name: str, characters: dict):
    cursor.execute("""
        SELECT character, current_form FROM players WHERE user_id = ?
    """, (user_id,))
    data = cursor.fetchone()

    if not data:
        return "❌ پلیر پیدا نشد"

    character_name, current_form = data

    if not character_name:
        return "❌ هنوز شخصیت نداری"

    char_data = characters.get(character_name)
    if not char_data:
        return "❌ شخصیت نامعتبره"

    if form_name not in char_data["forms"]:
        return "❌ این فرم برای این شخصیت وجود ندارد"

    cursor.execute("""
        UPDATE players SET current_form = ? WHERE user_id = ?
    """, (form_name, user_id))
    db.commit()

    return f"⚡ فرم {character_name} تغییر کرد به {form_name}"
