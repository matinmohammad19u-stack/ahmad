import os
import shutil
import sqlite3

# =========================
# FIX (پایداری دیتابیس): قبلاً مسیر فایل دیتابیس همیشه "game.db" (نسبی به
# پوشه‌ی اجرا) بود. توی خیلی از سرویس‌های هاست (Railway/Render/Replit و...)
# اگه پوشه‌ی اجرا روی یه دیسک غیرپایدار باشه، با هر آپدیت/دیپلوی این فایل
# از بین می‌ره و همه‌ی اطلاعات بازیکن‌ها (پول، لول، شخصیت، آیتم‌ها...) پاک
# می‌شه. الان مسیر از روی متغیر محیطی DB_PATH قابل تنظیمه تا بشه روی یه
# دیسک/والیوم دائمی نگه‌ش داشت؛ اگه ست نشده بود، همون رفتار قبلی (game.db
# کنار همین فایل) حفظ می‌شه که برای اجرای لوکال کافیه.
# =========================
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "game.db"))

# FIX: یه بک‌آپ ساده از دیتابیس قبل از هر تغییری می‌گیریم (فقط اگه فایل از
# قبل وجود داشته باشه). اگه یه دیپلوی/مایگریشن خراب چیزی رو خراب کنه، حداقل
# یه نسخه‌ی قبلش (game.db.bak) موجوده.
if os.path.exists(DB_PATH):
    try:
        shutil.copy2(DB_PATH, DB_PATH + ".bak")
    except Exception as _e:
        print(f"Warning: نتونستم بک‌آپ بگیرم: {_e}")

db = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = db.cursor()

# FIX: WAL کمک می‌کنه اگه بات وسط نوشتن (مثلاً وقت آپدیت/ری‌استارت ناگهانی)
# kill بشه، فایل دیتابیس کرپت/خراب نشه.
cursor.execute("PRAGMA journal_mode=WAL")
cursor.execute("PRAGMA synchronous=NORMAL")

print(f"📂 مسیر دیتابیس: {DB_PATH}")

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
    # FIX: برای پیاده‌سازی استریک جایزه‌ی روزانه (/daily) به این ستون نیاز بود
    "ALTER TABLE players ADD COLUMN daily_streak INTEGER DEFAULT 0",
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
