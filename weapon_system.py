# weapon_system.py
#
# قبلاً فقط یه شمشیر هم‌زمان قابل‌تجهیز بود (equipped_weapon، تک‌ستونی).
# الان تا ۳ تا شمشیر هم‌زمان می‌شه تجهیز کرد (equipped_weapons، به‌صورت
# رشته‌ی جداشده با کاما توی دیتابیس) — که خودش دقیقاً یادآور سبک
# «سانتوریو» (سه‌شمشیر) زوروئه! بونوس Zoro (x1.5) روی تک‌تکِ شمشیرهاش
# جدا حساب می‌شه.

from database import db, cursor
from swords_shop import SWORDS_SHOP

MAX_EQUIPPED_SWORDS = 3


def get_equipped_list(equipped_weapons_str: str) -> list:
    if not equipped_weapons_str:
        return []
    return [w for w in equipped_weapons_str.split(",") if w]


def format_equipped_list(weapons: list) -> str:
    return ",".join(weapons)


def sword_bonus_for(item_name: str, character_name: str) -> int:
    if item_name not in SWORDS_SHOP:
        return 0
    bonus = SWORDS_SHOP[item_name]["attack"]
    if character_name == "Roronoa Zoro":
        bonus = int(bonus * 1.5)
    return bonus


def total_sword_bonus(equipped_weapons_str: str, character_name: str) -> int:
    """مجموع بونوس Attack همه‌ی شمشیرهای تجهیزشده (تا ۳ تا)."""
    return sum(
        sword_bonus_for(w, character_name)
        for w in get_equipped_list(equipped_weapons_str)
    )


def equip_sword(user_id: int, item_name: str) -> str:
    cursor.execute(
        "SELECT quantity FROM inventory WHERE user_id=? AND item_name=?",
        (user_id, item_name)
    )
    row = cursor.fetchone()
    if not row or row[0] <= 0:
        return "❌ این آیتم توی کیفت نیست!"

    if item_name not in SWORDS_SHOP:
        return "❌ این آیتم قابل تجهیز نیست!"

    cursor.execute("SELECT character, equipped_weapons FROM players WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        return "❌ اول /character_select بزن."
    char_name, equipped_str = row
    equipped = get_equipped_list(equipped_str)

    if item_name in equipped:
        return f"❌ {item_name} از قبل تجهیز شده!"

    if len(equipped) >= MAX_EQUIPPED_SWORDS:
        return (
            f"❌ حداکثر {MAX_EQUIPPED_SWORDS} تا شمشیر هم‌زمان می‌تونی ببندی! "
            f"شمشیرهای فعلی: {', '.join(equipped)}\n"
            f"اول یکی رو با /unequip [نام شمشیر] باز کن."
        )

    equipped.append(item_name)
    cursor.execute(
        "UPDATE players SET equipped_weapons=? WHERE user_id=?",
        (format_equipped_list(equipped), user_id)
    )
    db.commit()

    bonus = sword_bonus_for(item_name, char_name)
    zoro_note = " (⚡ Zoro Bonus x1.5!)" if char_name == "Roronoa Zoro" else ""
    total = total_sword_bonus(format_equipped_list(equipped), char_name)
    return (
        f"✅ {item_name} تجهیز شد! ATK+{bonus}{zoro_note}\n"
        f"🗡️ شمشیرهای فعلی ({len(equipped)}/{MAX_EQUIPPED_SWORDS}): {', '.join(equipped)}\n"
        f"⚔️ مجموع بونوس Attack شمشیرها: +{total}"
    )


def unequip_sword(user_id: int, item_name: str) -> str:
    cursor.execute("SELECT character, equipped_weapons FROM players WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        return "❌ اول /character_select بزن."
    char_name, equipped_str = row
    equipped = get_equipped_list(equipped_str)

    if item_name not in equipped:
        return f"❌ {item_name} تجهیز نشده که بخوای بازش کنی!"

    equipped.remove(item_name)
    cursor.execute(
        "UPDATE players SET equipped_weapons=? WHERE user_id=?",
        (format_equipped_list(equipped), user_id)
    )
    db.commit()
    remaining = f"شمشیرهای فعلی: {', '.join(equipped)}" if equipped else "الان هیچ شمشیری تجهیز نکردی."
    return f"✅ {item_name} باز شد!\n{remaining}"
