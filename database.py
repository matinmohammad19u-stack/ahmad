import sqlite3
import os

# =========================
# FIX: قبلاً game.db همیشه کنار خود کد ذخیره می‌شد. توی Railway (و هر
# پلتفرم مشابهی) فایل‌سیستم سرویس هر بار که دیپلوی می‌زنی از صفر ساخته
# می‌شه، پس game.db هم هر دیپلوی پاک می‌شد و کل گیم (لول/پول/شخصیت/...)
# ریست می‌شد.
#
# الان مسیر دیتابیس اینطوری تعیین می‌شه:
#   ۱. اگه متغیر محیطی DB_PATH ست شده باشه، همون استفاده می‌شه.
#   ۲. وگرنه اگه یه Volume به سرویس وصل کرده باشی، Railway خودش خودکار
#      متغیر RAILWAY_VOLUME_MOUNT_PATH رو ست می‌کنه؛ کد از همونجا
#      استفاده می‌کنه (که بین دیپلوی‌ها پاک نمی‌شه).
#   ۳. وگرنه (مثلاً روی سیستم خودت) مثل قبل کنار کد ذخیره می‌شه.
#
# ⚠️ نکته‌ی مهم: این تغییر به تنهایی کافی نیست! باید توی خود Railway هم
# یه Volume به سرویس ربات وصل کنی، وگرنه بازم حالت شماره‌ی ۳ اجرا می‌شه
# و دیتا با هر دیپلوی پاک می‌مونه. مراحل:
#   1) پروژه‌ت رو توی Railway باز کن → روی سرویس ربات کلیک کن
#   2) دکمه‌ی "+ New" (یا راست‌کلیک روی کنواس) → "Volume"
#   3) به همین سرویس وصلش کن و یه مسیر بده، مثلاً: /data
#   4) سرویس رو Redeploy کن. همین! نیازی به تعریف دستی DB_PATH نیست،
#      کد خودش RAILWAY_VOLUME_MOUNT_PATH رو پیدا می‌کنه.
#   اگه با خطای Permission denied روی Volume مواجه شدی، یه Variable به
#   اسم RAILWAY_RUN_UID با مقدار 0 به سرویس اضافه کن
#   (https://docs.railway.com/reference/volumes#permissions)
# =========================
_custom_path = os.environ.get("DB_PATH")
_volume_dir = os.environ.get("RAILWAY_VOLUME_MOUNT_PATH")

if _custom_path:
    DB_PATH = _custom_path
elif _volume_dir:
    DB_PATH = os.path.join(_volume_dir, "game.db")
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game.db")

_db_dir = os.path.dirname(DB_PATH)
if _db_dir:
    os.makedirs(_db_dir, exist_ok=True)

db = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = db.cursor()

print(f"📂 Database connected -> {DB_PATH}")
if _custom_path or _volume_dir:
    print("✅ مسیر دائمیه؛ دیتا با دیپلوی جدید پاک نمی‌شه.")
else:
    print("⚠️ هیچ Volume‌ای وصل نیست! دیتابیس کنار کده و با هر دیپلوی ریست می‌شه.")
    print("   (برای رفع این مشکل، یه Volume توی Railway به این سرویس وصل کن.)")

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
