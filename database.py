import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game.db")

db = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = db.cursor()

print(f"📂 Database connected -> {DB_PATH}")

# =========================
# TABLES
# FIX: قبلاً چندتا جدول (available_characters, fight_history, skill_mastery,
# inventory, ships) هیچ‌جا ساخته نمی‌شدن یا فقط توی یه فایل جداگونه که
# main.py هیچوقت importش نمی‌کرد ساخته می‌شدن. یعنی به محض اینکه دستوری
# بهشون نیاز داشت (مثلاً /character_select یا /profile یا /mastery)،
# ربات با "no such table" کرش می‌کرد. الان همه‌ی جدول‌ها همینجا، یه‌جا
# و همیشه موقع استارت ساخته می‌شن.
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    money INTEGER DEFAULT 100,
    points INTEGER DEFAULT 0,
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
    last_daily TEXT,
    daily_streak INTEGER DEFAULT 0,
    current_island TEXT DEFAULT 'East Blue'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS available_characters (
    name TEXT PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS fight_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    enemy TEXT,
    result TEXT,
    reward_xp INTEGER DEFAULT 0,
    reward_money INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS skill_mastery (
    user_id INTEGER,
    character TEXT,
    skill_name TEXT,
    mastery INTEGER DEFAULT 0,
    unlocked INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, character, skill_name)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    user_id INTEGER,
    item_name TEXT,
    item_type TEXT,
    quantity INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, item_name)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    ship_name TEXT,
    speed INTEGER,
    durability INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS boss_cooldowns (
    user_id INTEGER,
    boss_id TEXT,
    defeated_at REAL,
    PRIMARY KEY (user_id, boss_id)
)
""")

db.commit()

# =========================
# MIGRATIONS
# FIX: اگه یه game.db قدیمی از قبل وجود داشته باشه، CREATE TABLE IF NOT
# EXISTS ستون‌های جدید (points, daily_streak) رو بهش اضافه نمی‌کنه. این
# بخش با ALTER TABLE اونا رو اضافه می‌کنه؛ اگه از قبل وجود داشته باشن
# (دیتابیس تازه‌ساز)، خطاش رو نادیده می‌گیریم.
# =========================
_PLAYER_COLUMN_MIGRATIONS = [
    ("points", "INTEGER DEFAULT 0"),
    ("daily_streak", "INTEGER DEFAULT 0"),
    ("current_island", "TEXT DEFAULT 'East Blue'"),
]

for _col, _decl in _PLAYER_COLUMN_MIGRATIONS:
    try:
        cursor.execute(f"ALTER TABLE players ADD COLUMN {_col} {_decl}")
        db.commit()
    except sqlite3.OperationalError:
        pass  # ستون از قبل وجود داره

print("✅ Tables ready")

# =========================
# SEED available_characters
# FIX: قبلاً این کار توی character_select.py بود که main.py اصلاً importش
# نمی‌کرد؛ یعنی جدول همیشه خالی می‌ماند و /character_select همیشه
# "همه‌ی شخصیت‌ها گرفته شدن" نشون می‌داد. الان همینجا، مستقل از هر فایل
# دیگه‌ای، پر می‌شه.
# =========================
from characters import characters as _characters

cursor.execute("SELECT COUNT(*) FROM available_characters")
if cursor.fetchone()[0] == 0:
    for _name in _characters.keys():
        cursor.execute(
            "INSERT OR IGNORE INTO available_characters (name) VALUES (?)", (_name,)
        )
    db.commit()
    print(f"✅ {len(_characters)} شخصیت توی available_characters ست شد")
