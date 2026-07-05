# points_system.py
#
# سیستم جدید Stat Points:
#   - هر لول که بالا میری، ۱۰۰ پوینت می‌گیری (POINTS_PER_LEVEL).
#   - چون هر برد PVP/Boss = +5 لول و هر برد Raid = +15 لول، این پوینت‌ها
#     مستقیماً همونجا که لول اضافه می‌شه محاسبه و به دیتابیس اضافه می‌شن
#     (نیازی به تابع جدا برای "هر لول" نیست چون لول فقط از همون چند جا
#     بالا می‌ره).
#   - پوینت‌ها کاملاً جدا از پول (💰) هستن؛ می‌شه هرطور خواستی بینشون
#     (Attack / Defense / Speed / HP) خرج کنی، برخلاف /upgrade که با پول کار می‌کنه.

from database import db, cursor

POINTS_PER_LEVEL = 100

# هر خرید یه "واحد" از این تعریف‌ها رو می‌خره
POINT_UPGRADES = {
    "attack":  {"cost": 50, "gain": 10, "label": "⚔️ Attack",  "column": "extra_attack"},
    "defense": {"cost": 50, "gain": 10, "label": "🛡️ Defense", "column": "extra_defense"},
    "speed":   {"cost": 50, "gain": 10, "label": "💨 Speed",   "column": "extra_speed"},
    "hp":      {"cost": 50, "gain": 50, "label": "❤️ HP",      "column": "max_hp"},
}


def get_points(user_id: int) -> int:
    cursor.execute("SELECT points FROM players WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0


def spend_points(user_id: int, stat: str) -> str:
    """یه واحد از stat انتخاب‌شده رو با پوینت می‌خره."""
    if stat not in POINT_UPGRADES:
        return "❌ این ویژگی وجود نداره"

    upgrade = POINT_UPGRADES[stat]
    cost = upgrade["cost"]
    gain = upgrade["gain"]
    column = upgrade["column"]

    cursor.execute("SELECT points FROM players WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        return "❌ اول /character_select بزن."

    points = row[0] or 0
    if points < cost:
        return f"❌ پوینت کافی نداری! (نیاز: {cost} | فعلاً: {points})"

    if column == "max_hp":
        # FIX: وقتی max_hp بالا می‌ره، hp فعلی هم به همون اندازه بالا می‌ره
        # تا خرید HP باعث یه سقف بی‌فایده (که hp فعلی به‌ش نمی‌رسه) نشه.
        cursor.execute(
            "UPDATE players SET points = points - ?, max_hp = max_hp + ?, hp = hp + ? WHERE user_id=?",
            (cost, gain, gain, user_id)
        )
    else:
        cursor.execute(
            f"UPDATE players SET points = points - ?, {column} = {column} + ? WHERE user_id=?",
            (cost, gain, user_id)
        )
    db.commit()

    return f"✅ {upgrade['label']} +{gain} شد! (-{cost} پوینت)"
