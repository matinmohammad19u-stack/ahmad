# clothes_shop.py
#
# فروشگاه لباس: هر لباس یه بونوس Defense می‌ده (برخلاف شمشیر که Attack
# می‌ده). برخلاف شمشیرها (که تا ۳ تا هم‌زمان می‌شه بست)، لباس فقط یه دونه
# هم‌زمان تجهیز می‌شه — یه ست کامل لباس می‌پوشی، نه چندتا روی هم.

CLOTHES_SHOP = {
    "Marine Recruit Uniform":   {"defense": 8,   "price": 250,   "description": "لباس ساده‌ی افسر تازه‌کارِ نیروی دریایی"},
    "Impel Down Prisoner Suit": {"defense": 5,   "price": 150,   "description": "لباس زندانی‌های ایمپل‌داون؛ تقریباً هیچ محافظتی نداره"},
    "Straw Hat":                {"defense": 12,  "price": 500,   "description": "کلاه حصیریِ لوفی، یادگاری شانکس؛ از نظر ارزش معنوی بی‌نظیره"},
    "Cotton Traveler's Coat":   {"defense": 15,  "price": 700,   "description": "پالتوی سبک برای سفرهای دریایی طولانی"},
    "Baroque Works Agent Suit": {"defense": 20,  "price": 1200,  "description": "لباس رسمی مأموران مخفی باروک ورکز"},
    "Alabasta Royal Robe":      {"defense": 25,  "price": 1800,  "description": "ردای سلطنتی خاندان نفرتاری"},
    "Skypiea White Beret Suit": {"defense": 28,  "price": 2200,  "description": "یونیفرم نیروهای سفیدپوش انل توی اسکای‌پیا"},
    "Wano Samurai Kimono":      {"defense": 35,  "price": 3000,  "description": "کیمونوی رزمی سامورایی‌های وانو"},
    "Fishman Karate Gi":        {"defense": 38,  "price": 3300,  "description": "گی رزمی مخصوص کاراته‌ی مردماهی"},
    "Tontatta Battle Armor":    {"defense": 32,  "price": 2800,  "description": "زره جنگی کوتوله‌های توناتا، سبک ولی محکم"},
    "Sun Pirates Vest":         {"defense": 40,  "price": 3800,  "description": "جلیقه‌ی دزدان دریایی خورشید، خدمه‌ی سابق جینبه"},
    "CP9 Assassin Suit":        {"defense": 45,  "price": 4500,  "description": "لباس رسمی مأموران ترور دولت جهانی"},
    "Kuja Warrior Armor":       {"defense": 48,  "price": 5000,  "description": "زره جنگجویان قبیله‌ی کوجا در آمازون لیلی"},
    "Beautiful Pirates Dress":  {"defense": 42,  "price": 4200,  "description": "لباس رسمی خدمه‌ی زیبای شارلوت لینلین"},
    "New Fishman Pirates Armor":{"defense": 46,  "price": 4700,  "description": "زره دزدان دریایی مردماهیِ جدید"},
    "Germa 66 Battle Suit":     {"defense": 60,  "price": 8000,  "description": "لباس رزمی خانواده‌ی وینسموک، قابلیت پرواز و نامرئی‌شدن داره"},
    "Marine Justice Coat":      {"defense": 55,  "price": 7000,  "description": "پالتوی رسمی افسران ارشد نیروی دریایی"},
    "Revolutionary Army Cloak": {"defense": 58,  "price": 7500,  "description": "شنل تیره‌ی اعضای ارتش انقلابی"},
    "Whitebeard Captain Coat":  {"defense": 70,  "price": 10000, "description": "پالتوی فرماندهیِ ادوارد نیوگیت"},
    "Shichibukai Coat":         {"defense": 75,  "price": 12000, "description": "پالتوی رسمی یکی از هفت جنگجوی دریا"},
    "Roger Pirates Coat":       {"defense": 80,  "price": 14000, "description": "پالتوی خدمه‌ی افسانه‌ای گول دی. راجر"},
    "Yonko Captain's Coat":     {"defense": 85,  "price": 16000, "description": "پالتوی فرماندهیِ یکی از چهار امپراطور دریا"},
    "Navy Admiral Coat":        {"defense": 90,  "price": 18000, "description": "پالتوی رسمی درجه‌ی دریاسالار نیروی دریایی"},
    "Fleet Admiral Coat":       {"defense": 95,  "price": 19500, "description": "پالتوی بالاترین درجه‌ی نیروی دریایی، فرمانده کل"},
    "World Government Robe":    {"defense": 100, "price": 20000, "description": "ردای اسرارآمیز پنج‌پیر، بالاترین قدرت پشت پرده‌ی دنیا"},
}
