import random
import copy


def get_form(character_name, skills_db):
    # FIX: قبلاً crash می‌کرد اگه character در skills_db نبود
    if character_name not in skills_db:
        return "Base"
    forms = list(skills_db[character_name].keys())
    return forms[0] if forms else "Base"


def get_skills(character_name, skills_db, form="Base"):
    """
    لیست اسکیل‌های قابل انتخاب یه کاراکتر توی یه فرم خاص.
    همیشه حداقل یه اسکیل (Basic Attack) برمی‌گردونه تا دکمه‌های فایت
    هیچوقت خالی نمونن و کرش نکنیم.
    """
    if character_name not in skills_db:
        return [{"name": "Basic Attack", "damage": 50}]

    char_forms = skills_db[character_name]
    if form not in char_forms:
        form = get_form(character_name, skills_db)  # fallback ایمن

    skills_list = char_forms.get(form, [])
    if not skills_list:
        return [{"name": "Basic Attack", "damage": 50}]
    return skills_list


def calculate_damage(attacker, defender, skill):
    base = skill["damage"]
    atk = attacker["stats"].get("attack", 100)
    dfs = defender["stats"].get("defense", 50)

    dmg = base + (atk * 0.8) - (dfs * 0.5)
    dmg *= random.uniform(0.9, 1.1)

    crit = random.random() < 0.1
    if crit:
        dmg *= 1.5

    return max(1, int(dmg)), crit


def decide_first(p1, p2):
    """بر اساس Speed تعیین می‌کنه کی اول حمله می‌کنه. تساوی → قرعه‌کشی."""
    s1 = p1["stats"].get("speed", 100)
    s2 = p2["stats"].get("speed", 100)
    if s1 > s2:
        return "p1"
    if s2 > s1:
        return "p2"
    return random.choice(["p1", "p2"])


# =========================
# ⚔️ BUTTON BATTLE STATE MACHINE
# قبلاً battle() یه تابع sync بود که کل فایت رو خودکار (با اسکیل‌های رندوم)
# تا آخر شبیه‌سازی می‌کرد و فقط لاگ متنی برمی‌گردوند؛ پلیر هیچ انتخابی
# نداشت. الان فایت به صورت state machine پیاده شده: هر بار یه نفر دکمه‌ی
# یه اسکیل رو می‌زنه، apply_action() همون یه ضربه رو پردازش می‌کنه و
# نوبت می‌ره طرف بعدی. main.py مسئول نگه‌داشتن state بین پیام‌های تلگرامه.
# =========================

MAX_ROUNDS = 40  # FIX: سقف امن برای جلوگیری از فایت بی‌نهایت (مثلاً دفس‌های خیلی بالا)


def create_battle(p1, p2, skills_db, p1_form="Base", p2_form="Base"):
    """
    p1 / p2: {"name": char_name, "stats": {"hp":, "attack":, "defense":, "speed":}}
    خروجی: دیکشنری state کامل مبارزه.
    """
    c1 = copy.deepcopy(p1)
    c2 = copy.deepcopy(p2)

    # FIX: اگه HP صفر یا منفی از دیتابیس بیاد (نباید پیش بیاد چون main.py
    # چکش می‌کنه، ولی برای امنیت بیشتر این تابع هم خودش رو محافظت می‌کنه)
    hp1 = max(1, c1["stats"].get("hp", 1))
    hp2 = max(1, c2["stats"].get("hp", 1))

    state = {
        "fighters": {
            "p1": {
                "name": c1["name"],
                "stats": c1["stats"],
                "hp": hp1,
                "max_hp": hp1,
                "form": p1_form,
                "skills": get_skills(c1["name"], skills_db, p1_form),
                "skills_used": {},
            },
            "p2": {
                "name": c2["name"],
                "stats": c2["stats"],
                "hp": hp2,
                "max_hp": hp2,
                "form": p2_form,
                "skills": get_skills(c2["name"], skills_db, p2_form),
                "skills_used": {},
            },
        },
        "turn": None,
        "round": 1,
        "actions": 0,
        "log": [],
        "finished": False,
        "winner": None,
        "earned_money": None,
    }

    state["turn"] = decide_first(state["fighters"]["p1"], state["fighters"]["p2"])

    f1 = state["fighters"]["p1"]
    f2 = state["fighters"]["p2"]
    first_name = state["fighters"][state["turn"]]["name"]
    state["log"].append(f"⚔️ {f1['name']} VS {f2['name']} شروع شد!")
    state["log"].append(f"❤️ {f1['name']}: {f1['hp']} HP | {f2['name']}: {f2['hp']} HP")
    state["log"].append(f"💨 {first_name} سریع‌تره و اول حمله می‌کنه!")

    return state


def get_actions(state, side):
    """لیست اسکیل‌های قابل انتخاب برای 'p1' یا 'p2' (برای ساخت دکمه‌ها)."""
    return state["fighters"][side]["skills"]


def apply_action(state, side, skill_index):
    """
    یه ضربه‌ی واحد رو پردازش می‌کنه. side باید برابر state['turn'] باشه.
    خروجی: دیکشنری result با جزئیات ضربه + وضعیت پایان مبارزه.
    """
    if side not in ("p1", "p2"):
        raise ValueError("invalid side")
    if state["finished"]:
        raise ValueError("battle already finished")
    if side != state["turn"]:
        raise ValueError("not this side's turn")

    other = "p2" if side == "p1" else "p1"
    attacker = state["fighters"][side]
    defender = state["fighters"][other]

    skills = attacker["skills"]
    # FIX: ایندکس نامعتبر (مثلاً دکمه‌ی قدیمی/دستکاری‌شده) → fallback ایمن
    # به جای IndexError/کرش کل مبارزه
    if not isinstance(skill_index, int) or skill_index < 0 or skill_index >= len(skills):
        skill_index = 0
    skill = skills[skill_index]

    attacker_view = {"name": attacker["name"], "stats": dict(attacker["stats"], hp=attacker["hp"])}
    defender_view = {"name": defender["name"], "stats": dict(defender["stats"], hp=defender["hp"])}

    dmg, crit = calculate_damage(attacker_view, defender_view, skill)
    defender["hp"] = max(0, defender["hp"] - dmg)

    attacker["skills_used"][skill["name"]] = attacker["skills_used"].get(skill["name"], 0) + 1

    crit_text = " 💥 CRIT!" if crit else ""
    state["log"].append(
        f"{attacker['name']} از {skill['name']} استفاده کرد → {dmg} دمیج{crit_text}"
    )

    result = {
        "attacker": side,
        "defender": other,
        "skill_name": skill["name"],
        "damage": dmg,
        "crit": crit,
        "attacker_hp": attacker["hp"],
        "defender_hp": defender["hp"],
        "finished": False,
        "winner": None,
        "timeout": False,
        "earned_money": None,
    }

    if defender["hp"] <= 0:
        earned_money = 100 + random.randint(0, 100)
        state["finished"] = True
        state["winner"] = side
        state["earned_money"] = earned_money
        result["finished"] = True
        result["winner"] = side
        result["earned_money"] = earned_money
        state["log"].append(f"🏆 برنده: {attacker['name']}!")
        return result

    # نوبت می‌ره طرف مقابل
    state["turn"] = other
    state["actions"] += 1
    if state["actions"] % 2 == 0:
        state["round"] += 1

    if state["round"] > MAX_ROUNDS:
        # FIX: قبلاً سقف turn (در نسخه‌ی auto) یعنی فایت متوقف می‌شد ولی
        # برد/باخت همیشه یه طرفه حساب می‌شد. الان بر اساس HP باقیمونده‌ی
        # واقعی هر دو طرف، برنده‌ی منصفانه تعیین می‌شه.
        hp1 = state["fighters"]["p1"]["hp"]
        hp2 = state["fighters"]["p2"]["hp"]
        if hp1 == hp2:
            winner_side = random.choice(["p1", "p2"])
        else:
            winner_side = "p1" if hp1 > hp2 else "p2"
        earned_money = 100 + random.randint(0, 100)

        state["finished"] = True
        state["winner"] = winner_side
        state["earned_money"] = earned_money
        result["finished"] = True
        result["winner"] = winner_side
        result["timeout"] = True
        result["earned_money"] = earned_money
        state["log"].append("⏱️ سقف راندها رسید! بر اساس HP باقیمونده برنده مشخص شد.")

    return result
