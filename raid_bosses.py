# raid_bosses.py
#
# متادیتای هر Raid Boss در یه جا. هر باس به یه جزیره‌ی واقعی توی
# islands.py وصله (Big Mom → Whole Cake Island، Kaido → Wano، Blackbeard →
# Marineford). لولِ required_level همون جزیره دو کار می‌کنه:
#   1) کمی به قدرت باس اضافه می‌کنه (به‌همراه لول خود پلیر)
#   2) رریتیِ آیتمی که موقع کشتنش دراپ می‌شه رو تعیین می‌کنه (هرچقدر
#      لول جزیره بیشتر، آیتم قوی‌تر) — طبق خواسته.
#
# اسکیل‌های هر باس، اسکیل‌های واقعی و دست‌ساز خودشه (از skill.py، قوی‌ترین
# فرمش) نه یه چیز ژنریک؛ یعنی واقعاً ابیلیتی مخصوص خودشو داره.

from skill import SKILL_DB
from islands import islands

RAID_BOSSES = {
    "bigmom": {
        "display": "👑 Big Mom (Charlotte Linlin)",
        "character": "Charlotte Linlin",
        "island": "Whole Cake Island",
        "base_hp": 5200,
        "base_attack": 230,
        "base_defense": 170,
        "base_speed": 90,
    },
    "kaido": {
        "display": "🐉 Kaido",
        "character": "Kaido",
        "island": "Wano",
        "base_hp": 6000,
        "base_attack": 250,
        "base_defense": 200,
        "base_speed": 110,
    },
    "blackbeard": {
        "display": "🖤 Blackbeard (Marshall D. Teach)",
        "character": "Marshall D. Teach",
        "island": "Marineford",
        "base_hp": 4500,
        "base_attack": 220,
        "base_defense": 150,
        "base_speed": 100,
    },
}

COOLDOWN_SECONDS = 30 * 60  # ۳۰ دقیقه کول‌داون بعد از کشتن یه باس (قبلاً ۵ دقیقه بود)
RARE_DROP_CHANCE = 0.05     # ۵٪ - "احتمال خیلی کم" برای دراپ آیتم مخصوص باس


def get_boss_stats(boss_id: str, player_level: int) -> dict:
    """استت واقعی باس برای این فایت، با کمی مقیاس‌بندی روی لول پلیر."""
    b = RAID_BOSSES[boss_id]
    return {
        "hp": b["base_hp"] + player_level * 15,
        "attack": b["base_attack"] + player_level // 2,
        "defense": b["base_defense"] + player_level // 3,
        "speed": b["base_speed"],
    }


def get_boss_form(boss_id: str) -> str:
    """قوی‌ترین فرمِ باس (آخرین کلید توی SKILL_DB) → همون فرمیه که باس
    توی فایت باهاش می‌جنگه، پس اسکیل‌های واقعی و خاص خودشو داره."""
    char = RAID_BOSSES[boss_id]["character"]
    forms = list(SKILL_DB.get(char, {"Base": None}).keys())
    return forms[-1] if forms else "Base"


def get_island_level(boss_id: str) -> int:
    island_name = RAID_BOSSES[boss_id]["island"]
    return islands[island_name]["required_level"]


def get_rarity_multiplier(boss_id: str) -> float:
    """هرچقدر لول جزیره‌ی باس بیشتر باشه، رریتیِ (قدرتِ) آیتمِ دراپیش بیشتره."""
    return round(1 + get_island_level(boss_id) / 100, 2)


def get_drop_item_name(boss_id: str) -> str:
    return f"یادگار {RAID_BOSSES[boss_id]['display']}"
