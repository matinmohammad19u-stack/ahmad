# race_system.py
#
# سیستم نژاد: ۱۵ نژاد پایه‌ی دنیای وان‌پیس + همه‌ی ترکیب‌های دورگه‌ی
# ممکن بینشون (هر دو نژاد پایه با هم = یه دورگه، مثل انسان×غول). یعنی
# C(15,2) = 105 دورگه + 15 پایه = 120 نژاد در کل.
#
# هر نژاد یه باف/دیباف خودکار روی Attack/Defense/Speed/HP داره (بر اساس
# ویژگی‌های شناخته‌شده‌ی همون نژاد توی داستان: غول‌ها قوی و کند، لانگ‌لگ‌ها
# سریع، مینک‌ها چابک و قدرتمند، و ...). نژادِ هر پلیر موقع /character_select
# کاملاً رندوم قرعه‌کشی می‌شه (مثل خودِ شخصیت).
#
# نژادهای دورگه جمع کامل (نه میانگین) دو نژاد پایه‌شون رو می‌گیرن — یعنی
# دورگه‌ها قوی‌تر از هر دو تک‌نژادِ والدشون هستن (طبق درخواست).

BASE_RACES = {
    "انسان":        {"en": "Human",              "attack": 0,   "defense": 0,   "speed": 0,   "hp": 0},
    "غول":          {"en": "Giant",               "attack": 25,  "defense": 15,  "speed": -15, "hp": 40},
    "کوتوله":       {"en": "Dwarf (Tontatta)",    "attack": -10, "defense": -5,  "speed": 30,  "hp": -15},
    "مردماهی":      {"en": "Fishman",             "attack": 20,  "defense": 10,  "speed": 5,   "hp": 15},
    "پری‌دریایی":   {"en": "Merfolk",              "attack": 5,   "defense": 0,   "speed": 20,  "hp": 5},
    "اسکای‌پین":    {"en": "Skypiean",             "attack": 0,   "defense": 5,   "speed": 15,  "hp": 0},
    "شاندیان":      {"en": "Shandian",            "attack": 15,  "defense": 5,   "speed": 10,  "hp": 5},
    "بیرکایی":      {"en": "Birkan",               "attack": 10,  "defense": 15,  "speed": 0,   "hp": 10},
    "لانگ‌آرم":     {"en": "Long Arm",             "attack": 20,  "defense": 0,   "speed": -5,  "hp": 0},
    "لانگ‌لگ":      {"en": "Long Leg",             "attack": 0,   "defense": -5,  "speed": 25,  "hp": 0},
    "اسنیک‌نک":     {"en": "Snakeneck",            "attack": 0,   "defense": 15,  "speed": 10,  "hp": 0},
    "مینک":         {"en": "Mink",                "attack": 15,  "defense": 5,   "speed": 20,  "hp": 5},
    "سه‌چشم":       {"en": "Three-Eye",           "attack": 5,   "defense": 20,  "speed": 0,   "hp": 10},
    "باکانیر":      {"en": "Buccaneer",           "attack": 25,  "defense": 10,  "speed": -5,  "hp": 20},
    "لورانیان":     {"en": "Lunarian",            "attack": 20,  "defense": 20,  "speed": 5,   "hp": 10},
}

_STATS = ("attack", "defense", "speed", "hp")


def _build_all_races():
    """۱۵ نژاد خالص + همه‌ی C(15,2)=105 دورگه (جمع کامل دو والد، پس دورگه‌ها
    قوی‌تر از هر دو تک‌نژادِ والدشون هستن) = ۱۲۰ نژاد."""
    all_races = {}
    names = list(BASE_RACES.keys())

    for name in names:
        all_races[name] = dict(BASE_RACES[name])

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            hybrid_name = f"{a} × {b}"
            ra, rb = BASE_RACES[a], BASE_RACES[b]
            hybrid = {"en": f"{ra['en']} × {rb['en']}"}
            for stat in _STATS:
                hybrid[stat] = ra[stat] + rb[stat]
            all_races[hybrid_name] = hybrid

    return all_races


ALL_RACES = _build_all_races()  # 120 نژاد (۱۵ پایه + ۱۰۵ دورگه)


def get_race_modifier(race_name: str) -> dict:
    return ALL_RACES.get(race_name, {"attack": 0, "defense": 0, "speed": 0, "hp": 0})


def apply_race(race_name: str, stats: dict) -> dict:
    """
    یه کپی از stats برمی‌گردونه که باف/دیباف Attack/Defense/Speed نژاد روش
    اعمال شده باشه. FIX: باف HP نژاد عمداً اینجا اعمال نمی‌شه — چون این
    تابع هر فایت صدا زده می‌شه و stats["hp"] همون HP فعلیِ (احتمالاً
    آسیب‌دیده‌ی) پلیره، نه HP کامل؛ اضافه‌کردن باف HP هربار باعث می‌شد HP
    هر فایت مصنوعی بالا بره. باف HP نژاد یه‌بار و برای همیشه، موقع گرفتن
    نژاد (توی character_select)، مستقیم روی max_hp اعمال می‌شه — پایین‌تر،
    apply_race_to_max_hp().
    """
    if not race_name:
        return dict(stats)
    mod = get_race_modifier(race_name)
    boosted = dict(stats)
    for stat in ("attack", "defense", "speed"):
        boosted[stat] = max(1, boosted.get(stat, 0) + mod.get(stat, 0))
    return boosted


def apply_race_to_max_hp(race_name: str, max_hp: int) -> int:
    mod = get_race_modifier(race_name)
    return max(1, max_hp + mod.get("hp", 0))


def describe_race(race_name: str) -> str:
    if not race_name:
        return "🧬 نژاد: نامشخص"
    mod = get_race_modifier(race_name)
    parts = []
    for stat, label in (("attack", "ATK"), ("defense", "DEF"), ("speed", "SPD"), ("hp", "HP")):
        v = mod.get(stat, 0)
        if v != 0:
            parts.append(f"{label}{'+' if v > 0 else ''}{v}")
    bonus_text = " | ".join(parts) if parts else "بدون باف/دیباف"
    return f"🧬 نژاد: {race_name} ({bonus_text})"


def random_race() -> str:
    import random
    return random.choice(list(ALL_RACES.keys()))
