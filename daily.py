import datetime

from database import db, cursor

BASE_MONEY = 300            # پایه‌ی پول جایزه
MONEY_PER_LEVEL = 20         # پول اضافه به‌ازای هر لول بازیکن
BASE_XP = 100                 # پایه‌ی XP جایزه
XP_PER_LEVEL = 5
STREAK_BONUS_PER_DAY = 50    # پول اضافه به‌ازای هر روز استریک
STREAK_CAP = 14               # حداکثر روزی که توی محاسبه‌ی جایزه حساب می‌شه


def _now_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def _parse_date(date_str):
    """تاریخ ذخیره‌شده توی last_daily رو به datetime.date تبدیل می‌کنه.
    اگه مقدار خالی/خراب بود، None برمی‌گردونه به‌جای کرش کردن (دفاعی،
    مثلاً اگه یه روز فرمت دستی دیتابیس عوض شده باشه)."""
    if not date_str:
        return None
    try:
        return datetime.date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None


def _time_until_reset(now: datetime.datetime) -> str:
    """چقدر مونده تا نیمه‌شب UTC بعدی (یعنی جایزه‌ی بعدی)."""
    tomorrow = datetime.datetime.combine(
        now.date() + datetime.timedelta(days=1), datetime.time.min,
        tzinfo=datetime.timezone.utc
    )
    remaining = tomorrow - now
    total_minutes = max(0, int(remaining.total_seconds() // 60))
    hours, minutes = divmod(total_minutes, 60)
    if hours:
        return f"{hours} ساعت و {minutes} دقیقه"
    return f"{minutes} دقیقه"


def claim_daily(user_id: int) -> str:
    """جایزه‌ی روزانه رو برای user_id حساب می‌کنه، اگه قبلاً امروز نگرفته
    باشه می‌ده و دیتابیس رو آپدیت می‌کنه. متن پیامی که باید برای کاربر
    فرستاده بشه رو برمی‌گردونه (خود تابع هیچ پیامی نمی‌فرسته)."""
    cursor.execute(
        """
        SELECT character, level, max_hp, money, last_daily, daily_streak
        FROM players WHERE user_id=?
        """,
        (user_id,)
    )
    row = cursor.fetchone()
    if not row:
        return "❌ اول /start بزن."

    char_name, level, max_hp, money, last_daily_str, streak = row
    streak = streak or 0

    if not char_name:
        return "❌ اول /character_select بزن."

    # FIX: اگه max_hp هنوز صفره (مثلاً شخصیت انتخاب شده ولی به هر دلیلی hp
    # ثبت نشده)، شفاف بهش می‌گیم به‌جای اینکه بی‌صدا 0/0 هیل بشه
    if not max_hp:
        max_hp = 1

    now = _now_utc()
    today = now.date()
    last_date = _parse_date(last_daily_str)

    if last_date == today:
        wait_text = _time_until_reset(now)
        return (
            "⏳ امروز جایزه‌ی روزانه‌ت رو قبلاً گرفتی!\n"
            f"🕒 {wait_text} دیگه تا جایزه‌ی بعدی مونده."
        )

    if last_date == today - datetime.timedelta(days=1):
        # دیروز هم claim کرده بود → استریک ادامه پیدا می‌کنه
        streak = min(streak + 1, STREAK_CAP)
    else:
        # یا اولین باره claim می‌کنه، یا حداقل یه روز رو جا انداخته → ریست
        streak = 1

    money_reward = BASE_MONEY + MONEY_PER_LEVEL * level + STREAK_BONUS_PER_DAY * (streak - 1)
    xp_reward = BASE_XP + XP_PER_LEVEL * level

    cursor.execute(
        """
        UPDATE players
        SET money = money + ?,
            xp = xp + ?,
            hp = max_hp,
            last_daily = ?,
            daily_streak = ?
        WHERE user_id = ?
        """,
        (money_reward, xp_reward, today.isoformat(), streak, user_id)
    )
    db.commit()

    streak_line = (
        f"🔥 استریک: {streak} روز پشت‌سرهم" if streak > 1 else "🔥 استریک: روز ۱"
    )
    new_money = money + money_reward

    return (
        "🎁 جایزه‌ی روزانه گرفته شد!\n\n"
        f"💰 +{money_reward} پول\n"
        f"⭐ +{xp_reward} XP\n"
        f"❤️ HP کامل شد! ({max_hp}/{max_hp})\n"
        f"{streak_line}\n\n"
        f"💰 پول فعلی: {new_money}"
    )
