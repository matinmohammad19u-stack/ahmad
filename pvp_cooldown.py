# pvp_cooldown.py
#
# با هر پلیرِ خاص، فقط یه‌بار در ساعت می‌شه فایت داد (نه یه کول‌داون
# سراسری روی خودِ فایت‌کردن). یعنی اگه با نفر A فایت دادی، فقط فایت بعدیت
# دوباره با همون A تا ۱ ساعت قفله؛ می‌تونی همون لحظه با نفر B فایت بدی.
# کول‌داون باس‌ها (raid/island_boss) کاملاً جداست و دست‌نخورده می‌مونه.

import time

from database import db, cursor

PVP_COOLDOWN_SECONDS = 60 * 60  # ۱ ساعت


def _normalize_pair(user_a: int, user_b: int):
    return (user_a, user_b) if user_a < user_b else (user_b, user_a)


def pvp_cooldown_remaining(user_a: int, user_b: int) -> int:
    a, b = _normalize_pair(user_a, user_b)
    cursor.execute(
        "SELECT last_fight_at FROM pvp_cooldowns WHERE user_a=? AND user_b=?",
        (a, b)
    )
    row = cursor.fetchone()
    if not row:
        return 0
    remaining = PVP_COOLDOWN_SECONDS - (time.time() - row[0])
    return max(0, int(remaining))


def record_pvp_fight(user_a: int, user_b: int):
    a, b = _normalize_pair(user_a, user_b)
    cursor.execute(
        "INSERT INTO pvp_cooldowns (user_a, user_b, last_fight_at) VALUES (?, ?, ?) "
        "ON CONFLICT(user_a, user_b) DO UPDATE SET last_fight_at=excluded.last_fight_at",
        (a, b, time.time())
    )
    db.commit()


def format_cooldown(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"
