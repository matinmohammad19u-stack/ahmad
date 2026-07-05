# swords_shop.py
#
# آپدیت: قبلاً چندتا شمشیر ساختگی (Rusty Cutlass, Iron Saber, Cabaton,
# World's Edge, ...) توی لیست بودن. الان کامل با شمشیرهای *واقعی* دنیای
# وان‌پیس جایگزین شدن — هر چهار درجه‌ی Meito (Wazamono / Ryo Wazamono /
# O Wazamono / Saijo O Wazamono) به‌همراه بقیه‌ی شمشیرهای معروف و
# غیر-Meito داستان. قیمت/دمیج بر اساس درجه‌ی هرکدوم مقیاس‌بندی شده؛
# صاحب اصلیِ هرکدوم هم توی توضیحش اومده.
# main.py خودش صفحه‌بندی (۸ تا در هر صفحه) رو مدیریت می‌کنه، پس هر تعداد
# شمشیر اینجا باشه مشکلی پیش نمی‌آد.

SWORDS_SHOP = {
    # --- Grade Swords (Wazamono) — پایین‌ترین درجه‌ی Meito ---
    "Shigure":              {"attack": 118,  "price": 900,    "description": "شمشیر اصلی تاشیگی؛ پایین‌ترین درجه‌ی Meito ولی همچنان قابل‌اعتماد"},
    "Sandai Kitetsu":       {"attack": 220,  "price": 1300,   "description": "شمشیر نفرین‌شده‌ی زورو؛ نسل سوم خانواده‌ی کیتتسو، بی‌دلیل بیشتر از حد لازم می‌بره"},

    # --- Skillful Grade (Ryo Wazamono) — یکی از ۵۰ تا ---
    "Yamaoroshi":           {"attack": 340,  "price": 2000,   "description": "یکی از شمشیرهای تاشیگی؛ درجه‌ی Skillful Grade"},
    "Kashu":                {"attack": 350,  "price": 2200,   "description": "شمشیر دیگه‌ی تاشیگی، قبلاً مال میستر ۱۱ بود"},
    "Yubashiri":            {"attack": 360,  "price": 2600,   "description": "شمشیر قبلی زورو، ساخت شیموتسکی؛ ظریف و برنده (بعداً نابود شد)"},

    # --- Great Grade (O Wazamono) — یکی از ۲۱ تا ---
    "Wado Ichimonji":       {"attack": 450,  "price": 4000,   "description": "امانتیِ کویینا به زورو؛ یکی از ۲۱ Great Grade Sword دنیا"},
    "Nidai Kitetsu":        {"attack": 480,  "price": 4300,   "description": "نسل دوم خانواده‌ی نفرین‌شده‌ی کیتتسو؛ Great Grade"},
    "Shusui":               {"attack": 550,  "price": 5500,   "description": "شمشیر سیاه افسانه‌ای ریوما، بعدها به زورو رسید؛ Great Grade"},
    "Ame no Habakiri":      {"attack": 580,  "price": 6000,   "description": "شمشیر کوزوکی اودن؛ گفته می‌شه می‌تونه آسمون رو ببره"},
    "Enma":                 {"attack": 620,  "price": 6800,   "description": "شمشیر دیگه‌ی اودن؛ هاوکی صاحبش رو می‌مکه، فعلاً قرضی دست زوروست"},

    # --- Supreme Grade (Saijo O Wazamono) — یکی از ۱۲ تا، بالاترین درجه ---
    "Shodai Kitetsu":       {"attack": 780,  "price": 12000,  "description": "نسل اول خانواده‌ی نفرین‌شده‌ی کیتتسو؛ یکی از ۱۲ Supreme Grade دنیا"},
    "Murakumogiri":         {"attack": 850,  "price": 14000,  "description": "نگیناتای غول‌آسای اودن، بعدها دست وایت‌بیرد؛ Supreme Grade"},
    "Yoru":                 {"attack": 1000, "price": 20000,  "description": "بزرگ‌ترین شمشیر دنیا، سلاح میهاوک؛ بالاترین Meito موجود"},

    # --- بقیه‌ی Meito‌های معروف (درجه‌ی نامعلوم یا اعلام‌نشده) ---
    "Gryphon":              {"attack": 500,  "price": 5000,   "description": "شمشیر شانکس؛ ظاهرش ساده ولی قدرتش افسانه‌ایه"},
    "Funkfreed":            {"attack": 520,  "price": 5300,   "description": "شمشیر سنگوکو که با میوه‌ی شیطانی به فیل تبدیل می‌شه"},
    "Kikoku":               {"attack": 600,  "price": 6500,   "description": "شمشیر روحی بروک، صدای ترسناکی داره"},
    "Soul Solid":           {"attack": 330,  "price": 2400,   "description": "شمشیر اولیه‌ی بروک، قبل از اینکه Kikoku رو بگیره"},
    "Durandal":             {"attack": 400,  "price": 3500,   "description": "شمشیر کاوندیش؛ وقتی از غلاف درمیاد یه درخشش خاص داره"},
    "Pretzel":              {"attack": 630,  "price": 7000,   "description": "شمشیر غول‌پیکر شارلوت کراکر، بزرگ‌تر از یه انسان معمولی"},
    "Shirauo":              {"attack": 580,  "price": 6200,   "description": "شمشیر شارلوت آماند از خانواده‌ی بیگ‌مام"},
    "Raiu":                 {"attack": 560,  "price": 6000,   "description": "شمشیر شیریو، آدم‌کش سابق تیم بلک‌بیرد"},
    "Napoleon":             {"attack": 700,  "price": 9000,   "description": "عصای طوطی‌شکل دوفلامینگو که به شمشیر تبدیل می‌شه"},
    "Konpira":              {"attack": 360,  "price": 3000,   "description": "یکی از Meito‌های شناخته‌شده؛ جزئیات صاحبش کمتر روشنه"},
    "Shichiseiken":         {"attack": 370,  "price": 3100,   "description": "یکی از Meito‌های شناخته‌شده؛ جزئیات صاحبش کمتر روشنه"},

    # --- شمشیرهای معروف ولی غیر-Meito داستان ---
    "Terry Sword":          {"attack": 440,  "price": 3800,   "description": "شمشیر غول‌آسای دوری، به اندازه‌ی خودش بزرگه"},
    "Eisen Whip":           {"attack": 340,  "price": 2700,   "description": "شمشیر اهرمی اوهم، از جنس Iron Cloud و مثل تازیانه خم می‌شه"},
    "Same-kiri Bocho":      {"attack": 410,  "price": 3600,   "description": "ساطور غول‌آسای باستیل، شکل زانباتو داره"},
    "Kiribachi":            {"attack": 390,  "price": 3300,   "description": "زانباتوی اره‌ای آرلانگ"},
}
