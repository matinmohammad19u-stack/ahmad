# form_system.py
#
# بازنویسی کامل: قبلاً /form با تایپ اسم فرم کار می‌کرد (/form Gear 2) و
# اجازه می‌داد هر فرمی از SKILL_DB رو ست کنی، حتی فرم‌های Awakening/Awakened
# که باید فقط از طریق مستری ۱۰۰٪ + /awaken باز بشن (باگ امنیتی: هرکسی بدون
# awaken کردن می‌تونست از قدرت فرم Awakening استفاده کنه).
#
# الان: فرم فقط با دکمه انتخاب می‌شه (نه تایپ کردن)، و فرم‌های Awakening/
# Awakened از لیست انتخابی حذف شدن (اونا کاملاً جدا، توسط awakening.py
# مدیریت می‌شن). فقط شخصیت‌هایی که حداقل ۲ فرم غیر-Awakening دارن
# (مثل Luffy: Base/Gear 2/Gear 4/Gear 5, Zoro: Base/Asura/King of Hell)
# دکمه‌ی انتخاب فرم می‌گیرن.

from database import db, cursor
from skill import SKILL_DB


def _is_awakening_form(form_name: str) -> bool:
    return "awaken" in form_name.lower()


def get_switchable_forms(character_name: str):
    """فرم‌های قابل‌انتخاب با دکمه برای این شخصیت (بدون فرم‌های Awakening)."""
    if character_name not in SKILL_DB:
        return []
    return [f for f in SKILL_DB[character_name].keys() if not _is_awakening_form(f)]


def has_form_choice(character_name: str) -> bool:
    """True یعنی این شخصیت حداقل ۲ فرم غیر-Awakening داره → دکمه‌ی انتخاب فرم لازمه."""
    return len(get_switchable_forms(character_name)) >= 2


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

    if character_name not in SKILL_DB:
        return "❌ شخصیت نامعتبره"

    switchable = get_switchable_forms(character_name)

    if form_name not in switchable:
        if switchable:
            return f"❌ فرم‌های موجود: {', '.join(switchable)}"
        return "❌ این شخصیت فرم قابل‌تغییری نداره"

    cursor.execute("""
        UPDATE players SET current_form = ? WHERE user_id = ?
    """, (form_name, user_id))
    db.commit()

    return f"⚡ فرم {character_name} تغییر کرد به: {form_name}"
