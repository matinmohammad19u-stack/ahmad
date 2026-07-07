# clothes_system.py
#
# برخلاف شمشیر (تا ۳ تا هم‌زمان)، لباس فقط یه دونه هم‌زمان تجهیز می‌شه —
# با /wear می‌پوشیش، با /unwear درش میاری. بونوس Defense می‌ده (نه Attack).

from database import db, cursor
from clothes_shop import CLOTHES_SHOP


def clothing_bonus_for(item_name: str) -> int:
    if not item_name or item_name not in CLOTHES_SHOP:
        return 0
    return CLOTHES_SHOP[item_name]["defense"]


def wear_clothing(user_id: int, item_name: str) -> str:
    cursor.execute(
        "SELECT quantity FROM inventory WHERE user_id=? AND item_name=?",
        (user_id, item_name)
    )
    row = cursor.fetchone()
    if not row or row[0] <= 0:
        return "❌ این لباس توی کیفت نیست!"

    if item_name not in CLOTHES_SHOP:
        return "❌ این آیتم قابل‌پوشیدن نیست!"

    cursor.execute("SELECT equipped_clothing FROM players WHERE user_id=?", (user_id,))
    prow = cursor.fetchone()
    if not prow:
        return "❌ اول /character_select بزن."
    current = prow[0]

    if current == item_name:
        return f"❌ {item_name} از قبل تنته!"

    cursor.execute(
        "UPDATE players SET equipped_clothing=? WHERE user_id=?",
        (item_name, user_id)
    )
    db.commit()

    bonus = clothing_bonus_for(item_name)
    swap_note = f" (قبلی: {current})" if current else ""
    return f"✅ {item_name} رو پوشیدی! DEF+{bonus}{swap_note}"


def unwear_clothing(user_id: int) -> str:
    cursor.execute("SELECT equipped_clothing FROM players WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row or not row[0]:
        return "❌ الان هیچ لباسی تنت نیست!"
    current = row[0]
    cursor.execute("UPDATE players SET equipped_clothing=NULL WHERE user_id=?", (user_id,))
    db.commit()
    return f"✅ {current} رو در آوردی!"
