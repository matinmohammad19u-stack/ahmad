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
#
# + لول‌گیت: فرم اول (Base) همیشه از لول ۰ آزاده. از فرم دوم به بعد،
# لولِ لازم = ۱۰۰ × جایگاه فرم (فرم دوم=۲۰۰، فرم سوم=۳۰۰، فرم چهارم=۴۰۰،...)
# — دقیقاً طبق خواسته: هر فرم ۱۰۰ لول بیشتر از قبلی می‌خواد.

from database import db, cursor
from skill import SKILL_DB

FORM_LEVEL_STEP = 100  # هر فرم نسبت به قبلی ۱۰۰ لول بیشتر می‌خواد


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


def get_form_requirement(character_name: str, form_name: str) -> int:
    """
    لولِ لازم برای این فرم: فرم اول (Base) = ۰. از فرم دوم به بعد،
    ۱۰۰ × جایگاهش (فرم دوم=۲۰۰, فرم سوم=۳۰۰, فرم چهارم=۴۰۰, ...).
    """
    switchable = get_switchable_forms(character_name)
    if form_name not in switchable:
        return 0
    position = switchable.index(form_name) + 1  # 1-based
    if position == 1:
        return 0
    return FORM_LEVEL_STEP * position


def get_forms_with_requirements(character_name: str):
    """لیست (form_name, required_level) به ترتیب همون فرم‌های قابل‌انتخاب."""
    return [
        (f, get_form_requirement(character_name, f))
        for f in get_switchable_forms(character_name)
    ]


def change_form(user_id: int, form_name: str) -> str:
    cursor.execute("""
        SELECT character, current_form, level FROM players WHERE user_id = ?
    """, (user_id,))
    data = cursor.fetchone()

    if not data:
        return "❌ پلیر پیدا نشد"

    character_name, current_form, level = data

    if not character_name:
        return "❌ هنوز شخصیت نداری"

    if character_name not in SKILL_DB:
        return "❌ شخصیت نامعتبره"

    switchable = get_switchable_forms(character_name)

    if form_name not in switchable:
        if switchable:
            return f"❌ فرم‌های موجود: {', '.join(switchable)}"
        return "❌ این شخصیت فرم قابل‌تغییری نداره"

    required_level = get_form_requirement(character_name, form_name)
    if level < required_level:
        missing = required_level - level
        return (
            f"🔒 برای فرم {form_name} باید لول {required_level} باشی "
            f"(الان لول {level}، {missing} لول دیگه مونده)."
        )

    cursor.execute("""
        UPDATE players SET current_form = ? WHERE user_id = ?
    """, (form_name, user_id))
    db.commit()

    return f"⚡ فرم {character_name} تغییر کرد به: {form_name}"
