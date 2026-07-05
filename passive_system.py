# passive_system.py
#
# هر شخصیت یه Passive داره: یه ابیلیتی خودکار که هیچوقت دمیج نمی‌ده، فقط
# یکی از استت‌های خودشو (Attack/Defense/Speed) دائمی بالا می‌بره. برخلاف
# اسکیل‌ها، پسیو نیازی به انتخاب/دکمه نداره؛ همیشه فعاله، از همون لحظه‌ای
# که فایت (PVP، Boss یا Raid) شروع می‌شه.

PASSIVES = {
    "Monkey D. Luffy":              {"name": "Rubber Body",              "stat": "defense", "pct": 15},
    "Roronoa Zoro":                 {"name": "Ashura's Resolve",         "stat": "attack",  "pct": 15},
    "Vinsmoke Sanji":               {"name": "Diable Jambe Heat",        "stat": "speed",   "pct": 15},
    "Charlotte Katakuri":           {"name": "Future Sight",             "stat": "defense", "pct": 20},
    "Marco":                        {"name": "Phoenix Regeneration",     "stat": "defense", "pct": 18},
    "Yamato":                       {"name": "Ryuo Discipline",          "stat": "attack",  "pct": 12},
    "Kozuki Oden":                  {"name": "Roasted Endurance",        "stat": "defense", "pct": 15},
    "Silvers Rayleigh":             {"name": "Dark King's Haki",         "stat": "attack",  "pct": 18},
    "Dracule Mihawk":                {"name": "World's Strongest Blade",  "stat": "attack",  "pct": 20},
    "Monkey D. Garp":               {"name": "Marine Hero's Fist",       "stat": "attack",  "pct": 15},
    "Akainu":                       {"name": "Magma Body",               "stat": "attack",  "pct": 15},
    "Aokiji":                       {"name": "Absolute Zero",            "stat": "defense", "pct": 15},
    "Kizaru":                       {"name": "Light Speed Kick",         "stat": "speed",   "pct": 20},
    "Fujitora":                     {"name": "Gravity Control",          "stat": "defense", "pct": 15},
    "Greenbull":                    {"name": "Endless Stamina",          "stat": "defense", "pct": 12},
    "Shanks":                       {"name": "Conqueror's Presence",     "stat": "attack",  "pct": 15},
    "Marshall D. Teach":            {"name": "Dark Dark Absorption",     "stat": "defense", "pct": 18},
    "Gol D. Roger":                 {"name": "Pirate King's Will",       "stat": "attack",  "pct": 20},
    "Saint Jaygarcia Saturn":       {"name": "Awakened Zoan Might",      "stat": "attack",  "pct": 18},
    "Saint Ethanbaron V. Nusjuro":  {"name": "Warrior God's Guard",      "stat": "defense", "pct": 15},
    "Saint Topman Warcury":         {"name": "Divine Reflexes",          "stat": "speed",   "pct": 15},
    "Saint Shepherd Ju Peter":      {"name": "Holy Resilience",          "stat": "defense", "pct": 15},
    "Saint Marcus Mars":            {"name": "Celestial Authority",      "stat": "attack",  "pct": 15},
    "Kaido":                        {"name": "Strongest Creature's Body", "stat": "defense", "pct": 20},
    "Charlotte Linlin":             {"name": "Soul Devourer",            "stat": "attack",  "pct": 18},
    "Edward Newgate":                {"name": "Tremor Fist",              "stat": "attack",  "pct": 20},
    "Boa Hancock":                  {"name": "Love-Love Beauty",         "stat": "speed",   "pct": 12},
    "Portgas D. Ace":               {"name": "Flame Emperor",            "stat": "attack",  "pct": 15},
    "Sabo":                         {"name": "Revolutionary Flame",      "stat": "attack",  "pct": 15},
    "Trafalgar D. Water Law":       {"name": "Room Surgery",             "stat": "defense", "pct": 15},
    "Eustass Kid":                  {"name": "Magnetic Repulsion",       "stat": "attack",  "pct": 15},
    "Killer":                       {"name": "Blade Storm",              "stat": "speed",   "pct": 15},
    "Jinbe":                        {"name": "Fishman Karate Guard",     "stat": "defense", "pct": 15},
    "Crocodile":                    {"name": "Desert Absorption",        "stat": "defense", "pct": 15},
    "Doflamingo":                   {"name": "String Puppetry",          "stat": "attack",  "pct": 15},
    "Issho":                        {"name": "Meteor Sight",             "stat": "defense", "pct": 15},
    "Charlotte Smoothie":           {"name": "Juice Extraction",         "stat": "attack",  "pct": 12},
    "Charlotte Cracker":            {"name": "Biscuit Army",             "stat": "defense", "pct": 18},
    "Charlotte Perospero":          {"name": "Candy Trap",               "stat": "speed",   "pct": 12},
    "King":                         {"name": "Fire-Free Pteranodon",     "stat": "speed",   "pct": 15},
    "Queen":                        {"name": "Plague Machine",           "stat": "attack",  "pct": 15},
    "Jack":                         {"name": "Mammoth Rampage",          "stat": "attack",  "pct": 18},
    "Smoker":                       {"name": "Smoke Logia Guard",        "stat": "defense", "pct": 15},
    "Coby":                         {"name": "Rokushiki Growth",         "stat": "speed",   "pct": 12},
    "Rob Lucci":                    {"name": "Predator Instinct",        "stat": "attack",  "pct": 18},
    "Kaku":                         {"name": "Giraffe Agility",          "stat": "speed",   "pct": 15},
    "Basil Hawkins":                {"name": "Fate Manipulation",        "stat": "defense", "pct": 15},
    "Scratchmen Apoo":              {"name": "Discordant Rhythm",        "stat": "speed",   "pct": 12},
    "Urouge":                       {"name": "Berserk Endurance",        "stat": "defense", "pct": 18},
    "X Drake":                      {"name": "Ancient Dragon Guard",     "stat": "defense", "pct": 15},
    "Cavendish":                    {"name": "Hakuba Elegance",          "stat": "speed",   "pct": 15},
    "Monkey D. Dragon":             {"name": "Revolutionary Storm",      "stat": "attack",  "pct": 18},
    "Kozuki Toki":                  {"name": "Time-Time Guard",          "stat": "defense", "pct": 15},
    "Scopper Gaban":                {"name": "Veteran's Instinct",       "stat": "speed",   "pct": 12},
    "Vista":                        {"name": "Flower Sword Mastery",     "stat": "attack",  "pct": 15},
}

_DEFAULT_PASSIVE = {"name": "Pirate's Grit", "stat": "defense", "pct": 8}


def get_passive(character_name: str) -> dict:
    return PASSIVES.get(character_name, _DEFAULT_PASSIVE)


def apply_passive(character_name: str, stats: dict) -> dict:
    """یه کپی از stats برمی‌گردونه که پسیوِ شخصیت روش اعمال شده باشه."""
    passive = get_passive(character_name)
    boosted = dict(stats)
    stat = passive["stat"]
    boosted[stat] = int(boosted.get(stat, 0) * (1 + passive["pct"] / 100))
    return boosted


def describe_passive(character_name: str) -> str:
    p = get_passive(character_name)
    stat_fa = {"attack": "Attack", "defense": "Defense", "speed": "Speed"}[p["stat"]]
    return f"🌟 پسیو: {p['name']} (+{p['pct']}% {stat_fa} همیشگی)"
