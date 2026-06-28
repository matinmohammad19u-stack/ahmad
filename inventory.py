import sqlite3

db = sqlite3.connect("game.db", check_same_thread=False)
cursor = db.cursor()

# =========================
# GET INVENTORY
# =========================
def get_inventory(user_id):
    cursor.execute("""
        SELECT item_name, item_type, quantity
        FROM inventory
        WHERE user_id = ?
    """, (user_id,))

    items = cursor.fetchall()

    if not items:
        return "🎒 Inventory خالیه"

    result = "🎒 Inventory:\n"
    for item_name, item_type, quantity in items:
        result += f"- {item_name} ({item_type}) x{quantity}\n"

    return result


# =========================
# ADD ITEM
# =========================
def add_item(user_id, item_name, item_type, quantity=1):
    cursor.execute("""
        SELECT quantity FROM inventory
        WHERE user_id = ? AND item_name = ?
    """, (user_id, item_name))

    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE inventory
            SET quantity = quantity + ?
            WHERE user_id = ? AND item_name = ?
        """, (quantity, user_id, item_name))
    else:
        cursor.execute("""
            INSERT INTO inventory (user_id, item_name, item_type, quantity)
            VALUES (?, ?, ?, ?)
        """, (user_id, item_name, item_type, quantity))

    db.commit()


# =========================
# REMOVE ITEM
# =========================
def remove_item(user_id, item_name, quantity=1):
    cursor.execute("""
        SELECT quantity FROM inventory
        WHERE user_id = ? AND item_name = ?
    """, (user_id, item_name))

    item = cursor.fetchone()

    if not item:
        return "❌ آیتم پیدا نشد"

    if item[0] < quantity:
        return "❌ تعداد کافی نیست"

    cursor.execute("""
        UPDATE inventory
        SET quantity = quantity - ?
        WHERE user_id = ? AND item_name = ?
    """, (quantity, user_id, item_name))

    # اگر صفر شد حذفش کن
    cursor.execute("""
        DELETE FROM inventory
        WHERE user_id = ? AND item_name = ? AND quantity <= 0
    """, (user_id, item_name))

    db.commit()

    return "✅ آیتم حذف شد"