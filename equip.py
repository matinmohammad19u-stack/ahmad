import sqlite3

db = sqlite3.connect("game.db", check_same_thread=False)
cursor = db.cursor()

# =========================
# EQUIP WEAPON (شمشیر)
# =========================
def equip_weapon(user_id, weapon_name):
    # چک کن آیتم رو داره یا نه
    cursor.execute("""
        SELECT item_name FROM inventory
        WHERE user_id = ? AND item_name = ?
    """, (user_id, weapon_name))

    item = cursor.fetchone()

    if not item:
        return "❌ این آیتم رو نداری"

    # ذخیره کردن سلاح مجهز شده
    cursor.execute("""
        UPDATE players
        SET equipped_weapon = ?
        WHERE user_id = ?
    """, (weapon_name, user_id))

    db.commit()

    return f"⚔️ {weapon_name} مجهز شد!"


# =========================
# GET EQUIPPED WEAPON
# =========================
def get_equipped_weapon(user_id):
    cursor.execute("""
        SELECT equipped_weapon
        FROM players
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    if not result:
        return None

    return result[0]


# =========================
# GET BONUS DAMAGE
# =========================
def get_weapon_damage(user_id, swords_dict):
    weapon = get_equipped_weapon(user_id)

    if not weapon:
        return 0

    if weapon in swords_dict:
        return swords_dict[weapon]["attack"]

    return 0