import sqlite3
import os

# =========================
# Railway-safe SQLite (بدون Volume)
# =========================

DB_PATH = os.environ.get("DB_PATH", "game.db")

db = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = db.cursor()

print(f"📂 Database connected: {DB_PATH}")

# =========================
# PLAYERS
# =========================
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

# =========================
# INVENTORY
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    item_name TEXT,
    item_type TEXT,
    quantity INTEGER DEFAULT 1,
    UNIQUE(user_id, item_name)
)
""")

# =========================
# SHIPS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS ships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    ship_name TEXT,
    speed INTEGER DEFAULT 1,
    durability INTEGER DEFAULT 1
)
""")

# =========================
# FIGHT HISTORY
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS fight_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    enemy TEXT,
    result TEXT,
    reward_xp INTEGER DEFAULT 0,
    reward_money INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# =========================
# SKILL MASTERY
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS skill_mastery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    character TEXT,
    skill_name TEXT,
    mastery INTEGER DEFAULT 0,
    unlocked INTEGER DEFAULT 0,
    UNIQUE(user_id, character, skill_name)
)
""")

# =========================
# AVAILABLE CHARACTERS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS available_characters (
    name TEXT PRIMARY KEY
)
""")

db.commit()

print("✅ Database initialized!")
