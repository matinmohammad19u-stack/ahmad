from database import db, cursor
from skill import SKILL_DB  # FIX: فایل skill.py، متغیر SKILL_DB


def change_form(user_id: int, form_name: str) -> str:
    cursor.execute("""
        SELECT character, current_form FROM players WHERE user_id = ?
    """, (user_id,))
    data = cursor.fetchone()

    if not data:
        return "❌ پلیر پیدا نشد"

    character_name, current_form = data

    if not character_name:
        return "❌ هنوز شخصیت نداری"

    if character_name not in SKILL_DB:  # FIX: SKILLS_DB → SKILL_DB
        return "❌ شخصیت نامعتبره"

    available_forms = list(SKILL_DB[character_name].keys())  # FIX: SKILLS_DB → SKILL_DB

    if form_name not in available_forms:
        return f"❌ فرم‌های موجود: {', '.join(available_forms)}"

    cursor.execute("""
        UPDATE players SET current_form = ? WHERE user_id = ?
    """, (form_name, user_id))
    db.commit()

    return f"⚡ فرم {character_name} تغییر کرد به: {form_name}"
