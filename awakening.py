# awakening.py
#
# FIX: main.py از اول "from awakening import check_awakening" داشت ولی این
# فایل اصلاً وجود نداشت → ImportError همون لحظه‌ی استارت ربات (قبل از اینکه
# حتی به polling برسه). این فایل سیستم Awakening رو کامل پیاده می‌کنه.
#
# منطق: Awakening کاملاً جداست از سیستم "فرم"‌ی که با دکمه انتخاب می‌شه
# (form_system.py). وقتی یکی از اسکیل‌های شخصیت به Mastery 100/100 برسه،
# پلیر می‌تونه یه‌بار Awakening رو با /awaken فعال کنه. این کار همیشگیه
# (غیرقابل برگشت) و اگه شخصیت یه فرم Awakening/Awakened توی SKILL_DB داشته
# باشه، خودش خودکار به عنوان current_form فعال می‌شه.

from database import db, cursor

AWAKENING_MASTERY_REQUIRED = 100


def _find_awakening_form(character_name: str):
    from skill import SKILL_DB
    forms = SKILL_DB.get(character_name, {})
    for form_name in forms:
        if "awaken" in form_name.lower():
            return form_name
    return None


def check_awakening(user_id: int, max_mastery: int) -> str:
    """
    اگه بیشترین Mastery ثبت‌شده‌ی پلیر به حد نصاب رسیده باشه، Awakening رو
    فعال می‌کنه (پرچم دیتابیس + خودکار سوییچ به فرم Awakening اگه شخصیت
    داشته باشه). در غیر این صورت پیام "هنوز آماده نیستی" برمی‌گردونه.
    """
    if max_mastery < AWAKENING_MASTERY_REQUIRED:
        missing = AWAKENING_MASTERY_REQUIRED - max_mastery
        return (
            "❌ هنوز آماده‌ی Awakening نیستی!\n"
            f"باید حداقل یه اسکیل رو به Mastery {AWAKENING_MASTERY_REQUIRED}/100 برسونی "
            f"({missing} تا مونده). با /fight یا /boss مستری بگیر."
        )

    cursor.execute("SELECT character FROM players WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    char_name = row[0] if row else None

    cursor.execute("UPDATE players SET awakening=1 WHERE user_id=?", (user_id,))

    awakening_form = _find_awakening_form(char_name) if char_name else None
    if awakening_form:
        cursor.execute(
            "UPDATE players SET current_form=? WHERE user_id=?",
            (awakening_form, user_id)
        )

    db.commit()

    if awakening_form:
        return (
            "🔥 Awakening فعال شد!\n"
            f"⚡ فرم {awakening_form} برات خودکار فعال شد."
        )
    return "🔥 Awakening فعال شد!"
