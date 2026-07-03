import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game.db")

db = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = db.cursor()

print(f"📂 Database connected -> {DB_PATH}")

# ===== TABLES =====

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    money INTEGER DEFAULT 100,
    character TEXT,
    hp INTEGER DEFAULT 0,
    max_hp INTEGER DEFAULT 0,
    current_form TEXT DEFAULT 'Base',
    form_multiplier REAL DEFAULT 1.0,
    awakening INTEGER DEFAULT 0,
    equipped_weapon TEXT,
    current_ship TEXT,
    extra_attack INTEGER DEFAULT 0,
    extra_defense INTEGER DEFAULT 0,
    extra_speed INTEGER DEFAULT 0,
    last_daily TEXT
)
""")

db.commit()
print("✅ Tables created")
