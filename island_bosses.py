# island_bosses.py
#
# قبلاً لیست باس‌های هر جزیره (توی islands.py) فقط تزئینی بود؛ هیچ‌جا
# واقعاً فایت‌پذیر نبودن. این فایل از همون لیست، یه کاتالوگ کامل و
# فایت‌پذیر برای هر ۵۱ باس می‌سازه:
#   - اگه باس یه کاراکتر واقعی توی skill.py باشه (مثلاً Akainu، Doflamingo،
#     Rob Lucci، King، Queen، Jack، ...) از همون اسکیل‌های دست‌ساز و
#     لوردار خودش استفاده می‌کنه.
#   - وگرنه (باس‌های کوچیک‌تر مثل Alvida/Buggy/Kuro/...)، ۳ تا اسکیل
#     منحصربه‌فرد ولی *ثابت* (seed از اسم خودش، پس بین ری‌استارت‌ها عوض
#     نمی‌شه) براش تولید می‌شه.
#
# Big Mom / Kaido / Blackbeard از این کاتالوگ حذف شدن چون قبلاً به عنوان
# Raid Boss (سیستم قوی‌تر و جدا، با /raid) پیاده شدن؛ اینجا فقط یه پیام
# راهنما نشونشون می‌دیم که "با /raid بزنش".

import random

from islands import islands
from skill import SKILL_DB

# اسم نمایشی (توی islands.py) → اسم واقعی توی SKILL_DB (برای استفاده از
# اسکیل‌های واقعی به‌جای تولید خودکار)
NAME_ALIASES = {
    "Crocodile (Final)": "Crocodile",
    "Kaido Final": "Kaido",
    "Cracker": "Charlotte Cracker",
    "Saturn": "Saint Jaygarcia Saturn",
    "Mars": "Saint Marcus Mars",
    "Warcury": "Saint Topman Warcury",
    "Ju Peter": "Saint Shepherd Ju Peter",
    "Nusjuro": "Saint Ethanbaron V. Nusjuro",
}

# این ۳ تا با /raid زده می‌شن، نه اینجا (تا محتوا تکراری نشه)
RAID_REDIRECT = {"Big Mom", "Kaido", "Blackbeard"}

COOLDOWN_SECONDS = 5 * 60   # همون ۵ دقیقه، طبق خواسته
RARE_DROP_CHANCE = 0.05     # همون ۵٪ شانس دراپ خیلی کم

_SKILL_VERBS = [
    "ضربه‌ی رعدآسا", "یورش خونین", "پنجه‌ی آتشین", "طوفان مشت", "کوبش سنگین",
    "حمله‌ی سایه", "شوک بنیان‌کن", "خیزش اهریمنی", "ضربه‌ی صاعقه",
    "برخورد کیهانی", "زخم عمیق", "موج فشار", "چرخش مرگبار", "ضربه‌ی نهایی",
    "گردباد خشم", "امواج شوک", "حمله‌ی روحی", "طلسم تاریکی", "خنجر مخفی",
    "یورش گروهی",
]


def _slug(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_")


def _is_final_variant(display_name: str) -> bool:
    return "Final" in display_name


def _build_catalog():
    catalog = {}
    for island_name, info in islands.items():
        level = info["required_level"]
        for part_num, part in info["parts"].items():
            for boss_name in part["bosses"]:
                if boss_name in RAID_REDIRECT:
                    continue
                boss_id = f"{_slug(island_name)}_{part_num}_{_slug(boss_name)}"
                catalog[boss_id] = {
                    "display": boss_name,
                    "island": island_name,
                    "island_level": level,
                    "part_num": part_num,
                    "part_name": part["name"],
                }
    return catalog


ISLAND_BOSSES = _build_catalog()


def get_bosses_for_island(island_name: str) -> dict:
    return {bid: b for bid, b in ISLAND_BOSSES.items() if b["island"] == island_name}


def get_boss_stats(boss_id: str, player_level: int) -> dict:
    """استت باس، مقیاس‌بندی‌شده روی لولِ جزیره‌ش + کمی روی لول پلیر."""
    b = ISLAND_BOSSES[boss_id]
    lvl = b["island_level"]
    mult = 1.6 if _is_final_variant(b["display"]) else 1.0
    rng = random.Random(boss_id + "_stats")  # seed ثابت → پایدار بین اجراها

    def v(base):
        return int(base * mult * rng.uniform(0.85, 1.2))

    return {
        "hp": max(80, v(350 + lvl * 6 + player_level * 4)),
        "attack": max(20, v(45 + lvl // 2)),
        "defense": max(10, v(25 + lvl // 3)),
        "speed": max(40, int(60 + lvl // 6)),
    }


def _generate_skills(display_name: str, power: int):
    rng = random.Random(display_name)  # seed ثابت روی اسم باس
    picks = rng.sample(_SKILL_VERBS, 3)
    skills = []
    for i, verb in enumerate(picks):
        dmg = int(power * (0.3 + i * 0.15) * rng.uniform(0.9, 1.1))
        skills.append({"name": f"{verb} {display_name}", "damage": max(10, dmg)})
    return skills


def get_boss_skills_and_form(boss_id: str):
    """
    خروجی: (skills_list, form_name, character_name_used)
    character_name_used همون اسمیه که باید توی state["fighters"]["p2"]["name"]
    ست شه؛ اگه این اسم توی SKILL_DB واقعی باشه، یعنی از موتور fight.py
    می‌شه مستقیم SKILL_DB رو پاس داد؛ وگرنه باید یه skills_db موقت
    (فقط برای این فایت) با یه ورودی مصنوعی ساخته شه.
    """
    b = ISLAND_BOSSES[boss_id]
    display = b["display"]
    real_name = NAME_ALIASES.get(display, display)

    if real_name in SKILL_DB:
        forms = SKILL_DB[real_name]
        strongest_form = list(forms.keys())[-1]
        return forms[strongest_form], strongest_form, real_name

    power = 45 + b["island_level"] // 2
    if _is_final_variant(display):
        power = int(power * 1.5)
    return _generate_skills(display, power), "Base", display


def get_rarity_multiplier(boss_id: str) -> float:
    """هرچقدر لولِ جزیره‌ی باس بیشتر، رریتیِ آیتم دراپی‌ش بیشتره."""
    return round(1 + ISLAND_BOSSES[boss_id]["island_level"] / 100, 2)


def get_drop_item_name(boss_id: str) -> str:
    return f"یادگار {ISLAND_BOSSES[boss_id]['display']}"


def total_boss_count() -> int:
    return len(ISLAND_BOSSES) + len(RAID_REDIRECT)
