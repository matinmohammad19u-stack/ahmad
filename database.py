import sqlite3

db = sqlite3.connect("game.db", check_same_thread=False)
cursor = db.cursor()

# =========================
# PLAYERS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    user_id         INTEGER PRIMARY KEY,
    username        TEXT,
    level           INTEGER DEFAULT 1,
    xp              INTEGER DEFAULT 0,
    money           INTEGER DEFAULT 100,

    -- شخصیت
    character       TEXT DEFAULT NULL,
    hp              INTEGER DEFAULT 0,
    max_hp          INTEGER DEFAULT 0,

    -- فرم
    current_form    TEXT DEFAULT 'Base',
    form_multiplier REAL DEFAULT 1.0,

    -- اویکنینگ
    awakening       INTEGER DEFAULT 0,

    -- سلاح و کشتی
    equipped_weapon TEXT DEFAULT NULL,
    current_ship    TEXT DEFAULT NULL,

    -- ارتقاهای اضافه (FIX: قبلاً ذخیره نمی‌شد)
    extra_attack    INTEGER DEFAULT 0,
    extra_defense   INTEGER DEFAULT 0,
    extra_speed     INTEGER DEFAULT 0,

    -- FIX: قبلاً وضعیت /daily توی حافظه (bot_data) نگه داشته می‌شد که با
    -- هر ری‌استارت بات پاک می‌شد و همه می‌تونستن جایزه رو دوباره بگیرن
    last_daily      TEXT DEFAULT NULL
)
""")

# Migration: اگه دیتابیس قدیمی داری ستون‌های جدید اضافه بشن
for _col_def in [
    "ALTER TABLE players ADD COLUMN extra_attack INTEGER DEFAULT 0",
    "ALTER TABLE players ADD COLUMN extra_defense INTEGER DEFAULT 0",
    "ALTER TABLE players ADD COLUMN extra_speed INTEGER DEFAULT 0",
    "ALTER TABLE players ADD COLUMN last_daily TEXT DEFAULT NULL",
]:
    try:
        cursor.execute(_col_def)
    except Exception:
        pass  # ستون از قبل وجود داره

# =========================
# INVENTORY
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    item_name   TEXT,
    item_type   TEXT,
    quantity    INTEGER DEFAULT 1,
    UNIQUE(user_id, item_name)
)
""")

# =========================
# SHIPS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS ships (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    ship_name   TEXT,
    speed       INTEGER DEFAULT 1,
    durability  INTEGER DEFAULT 1
)
""")

# =========================
# FIGHT HISTORY
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS fight_history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER,
    enemy        TEXT,
    result       TEXT,
    reward_xp    INTEGER DEFAULT 0,
    reward_money INTEGER DEFAULT 0,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# =========================
# SKILL MASTERY
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS skill_mastery (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    character   TEXT,
    skill_name  TEXT,
    mastery     INTEGER DEFAULT 0,
    unlocked    INTEGER DEFAULT 0,
    UNIQUE(user_id, character, skill_name)
)
""")

# =========================
# AVAILABLE CHARACTERS (FIX: قبلاً فقط توی character_select.py بود که import نمی‌شد)
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS available_characters (
    name TEXT PRIMARY KEY
)
""")

db.commit()

# پر کردن available_characters اگه خالیه
try:
    from characters import characters as _chars
    cursor.execute("SELECT COUNT(*) FROM available_characters")
    if cursor.fetchone()[0] == 0:
        for _name in _chars.keys():
            cursor.execute("INSERT OR IGNORE INTO available_characters (name) VALUES (?)", (_name,))
        db.commit()
except Exception as e:
    print(f"Warning: Could not initialize available_characters: {e}")

print("✅ Database initialized!")
