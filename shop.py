import sqlite3

db = sqlite3.connect("game.db", check_same_thread=False)
cursor = db.cursor()

# =========================
# SHOP ITEMS (ثابت بازی)
# =========================
SHOP_ITEMS = {
    "Small Potion": {"price": 50, "type": "heal", "heal": 50},
    "Medium Potion": {"price": 120, "type": "heal", "heal": 120},
    "Large Potion": {"price": 250, "type": "heal", "heal": 300},

    "Training Boost": {"price": 300, "type": "boost", "xp_multiplier": 2},

    "Basic Ship": {"price": 500, "type": "ship", "speed": 1, "durability": 1},
    "Speed Ship": {"price": 1200, "type": "ship", "speed": 2, "durability": 1},
    "War Ship": {"price": 2500, "type": "ship", "speed": 3, "durability": 3},
}

# =========================
# GET PLAYER MONEY
# =========================
def get_money(user_id):
    cursor.execute("SELECT money FROM players WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0

# =========================
# BUY ITEM
# =========================
def buy_item(user_id, item_name):
    if item_name not in SHOP_ITEMS:
        return "❌ این آیتم وجود ندارد"

    item = SHOP_ITEMS[item_name]
    price = item["price"]

    money = get_money(user_id)

    if money < price:
        return "❌ پول کافی نداری"

    # کم کردن پول
    cursor.execute("""
        UPDATE players
        SET money = money - ?
        WHERE user_id = ?
    """, (price, user_id))

    # آیتم‌های مختلف
    if item["type"] == "ship":
        cursor.execute("""
            INSERT INTO ships (user_id, ship_name, speed, durability)
            VALUES (?, ?, ?, ?)
        """, (user_id, item_name, item["speed"], item["durability"]))

        cursor.execute("""
            UPDATE players
            SET current_ship = ?
            WHERE user_id = ?
        """, (item_name, user_id))

    else:
        cursor.execute("""
            INSERT INTO inventory (user_id, item_name, item_type, quantity)
            VALUES (?, ?, ?, 1)
        """, (user_id, item_name, item["type"]))

    db.commit()

    return f"✅ {item_name} خریداری شد!"