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
    لیست اسکیل‌های حمله‌ی قابل انتخاب یه کاراکتر توی یه فرم خاص (بدون
    جاخالی/دفاع؛ اونا جدا و پویا توی get_actions اضافه می‌شن).
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

# =========================
# 🌀 جاخالی / 🛡 دفاع
# این دو تا یه "اسکیل" واقعی نیستن، اکشن‌های ویژه‌ان که به جای حمله زدن،
# یه شیلد روی خود بازیکن می‌ذارن که رو ضربه‌ی بعدیِ حریف اثر می‌کنه:
#   - جاخالی (۵ بار در کل مبارزه): ضربه‌ی بعدی حریف کامل رد می‌شه (۰ دمیج).
#   - دفاع (۳ بار در کل مبارزه): تأثیرش بسته به چندمین باری که استفاده
#     می‌شه فرق می‌کنه → بار ۱: دمیج ۰ (کامل خنثی) | بار ۲: دمیج نصف |
#     بار ۳: دمیج یک‌چهارم.
# استفاده از این دو تا هم مثل زدن یه اسکیل، نوبت رو می‌ده طرف مقابل.
# =========================
DODGE_MAX_USES = 5
DEFENSE_MAX_USES = 8
DODGE_TYPE = "dodge"
DEFENSE_TYPE = "defense"
ATTACK_TYPE = "attack"

_DEFENSE_TIER_LABEL = {
    1: "کامل خنثی می‌کنه (۰ دمیج)",
    2: "نصف می‌کنه",
    3: "یک‌چهارم می‌کنه",
}


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

    def _new_fighter(c, hp, form):
        return {
            "name": c["name"],
            "stats": c["stats"],
            "hp": hp,
            "max_hp": hp,
            "form": form,
            "skills": get_skills(c["name"], skills_db, form),
            "skills_used": {},
            # شارژهای جاخالی/دفاع
            "dodge_left": DODGE_MAX_USES,
            "defense_left": DEFENSE_MAX_USES,
            "defense_used": 0,          # چندمین بار دفاع زده شده (برای تعیین تیر)
            "pending_dodge": False,     # ضربه‌ی بعدی حریف روی این آدم رد می‌شه
            "pending_defense_tier": 0,  # 0 = فعال نیست، 1/2/3 = تیر فعلی دفاع
        }

    state = {
        "fighters": {
            "p1": _new_fighter(c1, hp1, p1_form),
            "p2": _new_fighter(c2, hp2, p2_form),
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
    state["log"].append(
        f"🌀 هر بازیکن {DODGE_MAX_USES} جاخالی و 🛡 {DEFENSE_MAX_USES} دفاع برای کل مبارزه داره."
    )
    state["log"].append(f"💨 {first_name} سریع‌تره و اول حمله می‌کنه!")

    return state


def get_actions(state, side):
    """
    لیست کامل اکشن‌های قابل انتخاب برای 'p1' یا 'p2' (برای ساخت دکمه‌ها):
    اسکیل‌های حمله + (اگه شارژ مونده باشه) جاخالی و دفاع.
    ترتیب همیشه ثابته: [اسکیل‌های حمله..., جاخالی؟, دفاع؟] تا ایندکس‌های
    دکمه‌ای که قبلاً ساخته شده معتبر بمونن.
    """
    fighter = state["fighters"][side]
    actions = list(fighter["skills"])

    if fighter["dodge_left"] > 0:
        actions.append({
            "name": f"جاخالی ({fighter['dodge_left']}/{DODGE_MAX_USES})",
            "damage": 0,
            "type": DODGE_TYPE,
        })

    if fighter["defense_left"] > 0:
        actions.append({
            "name": f"دفاع ({fighter['defense_left']}/{DEFENSE_MAX_USES})",
            "damage": 0,
            "type": DEFENSE_TYPE,
        })

    return actions


def apply_action(state, side, skill_index):
    """
    یه اکشن واحد رو پردازش می‌کنه: حمله، جاخالی یا دفاع. side باید برابر
    state['turn'] باشه. خروجی: دیکشنری result با جزئیات اکشن + وضعیت
    پایان مبارزه.
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

    actions = get_actions(state, side)
    # FIX: ایندکس نامعتبر (مثلاً دکمه‌ی قدیمی/دستکاری‌شده) → fallback ایمن
    # به جای IndexError/کرش کل مبارزه
    if not isinstance(skill_index, int) or skill_index < 0 or skill_index >= len(actions):
        skill_index = 0
    action = actions[skill_index]
    action_type = action.get("type", ATTACK_TYPE)

    result = {
        "attacker": side,
        "defender": other,
        "action_type": action_type,
        "skill_name": action["name"],
        "damage": 0,
        "crit": False,
        "mitigated": None,  # None | "dodge" | "defense_full" | "defense_half" | "defense_quarter"
        "attacker_hp": attacker["hp"],
        "defender_hp": defender["hp"],
        "finished": False,
        "winner": None,
        "timeout": False,
        "earned_money": None,
    }

    if action_type == DODGE_TYPE:
        # ---------- جاخالی: ضربه‌ی بعدیِ حریف روی این آدم کامل رد می‌شه ----------
        attacker["dodge_left"] = max(0, attacker["dodge_left"] - 1)
        attacker["pending_dodge"] = True
        state["log"].append(
            f"🌀 {attacker['name']} جاخالی داد! ضربه‌ی بعدی {defender['name']} روش اثر نمی‌کنه."
        )

    elif action_type == DEFENSE_TYPE:
        # ---------- دفاع: تیرش بسته به چندمین بار مصرفه ----------
        tier = attacker["defense_used"] + 1  # 1, 2, 3
        attacker["defense_used"] += 1
        attacker["defense_left"] = max(0, attacker["defense_left"] - 1)
        attacker["pending_defense_tier"] = tier
        state["log"].append(
            f"🛡 {attacker['name']} دفاع گرفت! ضربه‌ی بعدی {defender['name']} رو "
            f"{_DEFENSE_TIER_LABEL[min(tier, 3)]}."
        )

    else:
        # ---------- حمله‌ی عادی ----------
        skill = action
        attacker_view = {"name": attacker["name"], "stats": dict(attacker["stats"], hp=attacker["hp"])}
        defender_view = {"name": defender["name"], "stats": dict(defender["stats"], hp=defender["hp"])}

        dmg, crit = calculate_damage(attacker_view, defender_view, skill)

        mitigated = None
        if defender["pending_dodge"]:
            dmg = 0
            mitigated = "dodge"
            defender["pending_dodge"] = False
        elif defender["pending_defense_tier"] > 0:
            tier = defender["pending_defense_tier"]
            if tier == 1:
                dmg = 0
                mitigated = "defense_full"
            elif tier == 2:
                dmg = dmg // 2
                mitigated = "defense_half"
            else:
                dmg = dmg // 4
                mitigated = "defense_quarter"
            defender["pending_defense_tier"] = 0

        defender["hp"] = max(0, defender["hp"] - dmg)
        attacker["skills_used"][skill["name"]] = attacker["skills_used"].get(skill["name"], 0) + 1

        crit_text = " 💥 CRIT!" if crit and dmg > 0 else ""
        state["log"].append(
            f"{attacker['name']} از {skill['name']} استفاده کرد → {dmg} دمیج{crit_text}"
        )

        result["damage"] = dmg
        result["crit"] = crit
        result["mitigated"] = mitigated
        result["attacker_hp"] = attacker["hp"]
        result["defender_hp"] = defender["hp"]

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

    # نوبت می‌ره طرف مقابل (چه حمله بوده، چه جاخالی، چه دفاع)
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
