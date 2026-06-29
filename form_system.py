from database import db, cursor
from skills import SKILLS_DB  # یا هر اسمی که داری

def change_form(user_id: int, form_name: str):
    cursor.execute("""
        SELECT character, current_form FROM players WHERE user_id = ?
    """, (user_id,))
    data = cursor.fetchone()

    if not data:
        return "❌ پلیر پیدا نشد"

    character_name, current_form = data

    if not character_name:
        return "❌ هنوز شخصیت نداری"

    if character_name not in SKILLS_DB:
        return "❌ شخصیت نامعتبره"

    available_forms = list(SKILLS_DB[character_name].keys())

    if form_name not in available_forms:
        return f"❌ فرم‌های موجود: {', '.join(available_forms)}"

    cursor.execute("""
        UPDATE players SET current_form = ? WHERE user_id = ?
    """, (form_name, user_id))
    db.commit()

    return f"⚡ فرم {character_name} تغییر کرد به {form_name}"
