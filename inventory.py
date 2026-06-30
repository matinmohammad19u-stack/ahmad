from database import db, cursor
from swords_shop import SWORDS_SHOP


def equip_weapon(user_id: int, item_name: str) -> str:
    """تجهیز سلاح از inventory"""
    cursor.execute(
        "SELECT quantity FROM inventory WHERE user_id=? AND item_name=?",
        (user_id, item_name)
    )
    row = cursor.fetchone()
    if not row:
        return "❌ این آیتم توی کیفت نیست!"

    if item_name not in SWORDS_SHOP:
        return "❌ این آیتم قابل تجهیز نیست!"

    cursor.execute("SELECT character FROM players WHERE user_id=?", (user_id,))
    char_row = cursor.fetchone()
    char_name = char_row[0] if char_row else None

    sword_attack = SWORDS_SHOP[item_name]["attack"]
    bonus = int(sword_attack * 1.5) if char_name == "Roronoa Zoro" else sword_attack

    cursor.execute("UPDATE players SET equipped_weapon=? WHERE user_id=?", (item_name, user_id))
    db.commit()

    zoro_note = " (⚡ Zoro Bonus x1.5!)" if char_name == "Roronoa Zoro" else ""
    return f"✅ {item_name} تجهیز شد! ⚔️ ATK+{bonus}{zoro_note}"


def unequip_weapon(user_id: int) -> str:
    """برداشتن سلاح"""
    cursor.execute("UPDATE players SET equipped_weapon=NULL WHERE user_id=?", (user_id,))
    db.commit()
    return "✅ سلاح برداشته شد."


def get_equipped(user_id: int):
    """گرفتن سلاح فعلی"""
    cursor.execute("SELECT equipped_weapon FROM players WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else None
