import sqlite3

db = sqlite3.connect("game.db")
cursor = db.cursor()

# اضافه کردن ستون‌های جدید (اگر قبلاً نبوده)
try:
    cursor.execute("ALTER TABLE players ADD COLUMN character TEXT")
except:
    pass

try:
    cursor.execute("ALTER TABLE players ADD COLUMN hp INTEGER DEFAULT 100")
except:
    pass

try:
    cursor.execute("ALTER TABLE players ADD COLUMN max_hp INTEGER DEFAULT 100")
except:
    pass

try:
    cursor.execute("ALTER TABLE players ADD COLUMN current_form TEXT DEFAULT 'Base'")
except:
    pass

try:
    cursor.execute("ALTER TABLE players ADD COLUMN current_part INTEGER DEFAULT 1")
except:
    pass

db.commit()
db.close()

print("Database fixed!")