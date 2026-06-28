import sqlite3

db = sqlite3.connect("game.db")
cursor = db.cursor()

# =========================
# CHARACTER SYSTEM FIX
# =========================

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

# فقط برای هماهنگی با سیستم فرم‌ها
try:
    cursor.execute("ALTER TABLE players ADD COLUMN current_form_index INTEGER DEFAULT 0")
except:
    pass

db.commit()
db.close()

print("✅ Characters DB fixed successfully!")