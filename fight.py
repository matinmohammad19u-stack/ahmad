import random
import copy


def get_form(character_name, skills_db):
    # FIX: قبلاً crash می‌کرد اگه character در skills_db نبود
    if character_name not in skills_db:
        return "Base"
    forms = list(skills_db[character_name].keys())
    return forms[0] if forms else "Base"


def pick_skill(character_name, skills_db, form="Base"):
    # FIX: قبلاً این تابع فرم انتخابی بازیکن رو نمی‌گرفت و همیشه از
    # اولین فرم (Base) استفاده می‌کرد. یعنی /form هیچ تاثیری روی PVP نداشت!
    if character_name not in skills_db:
        return {"name": "Basic Attack", "damage": 50}

    char_forms = skills_db[character_name]
    if form not in char_forms:
        form = get_form(character_name, skills_db)  # fallback ایمن

    skills_list = char_forms.get(form, [])
    if not skills_list:
        return {"name": "Basic Attack", "damage": 50}
    return random.choice(skills_list)


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


def turn_order(p1, p2):
    s1 = p1["stats"].get("speed", 100)
    s2 = p2["stats"].get("speed", 100)
    if s1 > s2:
        return [p1, p2]
    if s2 > s1:
        return [p2, p1]
    return random.sample([p1, p2], 2)


# =========================
# ⚔️ BATTLE
# FIX: حالا final_hp1 / final_hp2 (برای sync کردن HP بعد از فایت در دیتابیس)
# و c1_skills_used (برای آپدیت mastery) هم برمی‌گردونه
# =========================
def battle(p1, p2, skills_db, p1_form="Base", p2_form="Base"):
    c1 = copy.deepcopy(p1)
    c2 = copy.deepcopy(p2)

    hp1 = c1["stats"]["hp"]
    hp2 = c2["stats"]["hp"]

    turn = 1
    log = []
    c1_skills_used = {}  # FIX: برای آپدیت mastery بعد از فایت

    log.append(f"⚔️ {c1['name']} VS {c2['name']} START!")
    log.append(f"❤️ {c1['name']}: {hp1} HP | {c2['name']}: {hp2} HP")
    log.append("━━━━━━━━━━━━━━━━━━━━━━")

    while hp1 > 0 and hp2 > 0 and turn <= 50:
        order = turn_order(c1, c2)

        for attacker in order:
            defender = c2 if attacker is c1 else c1
            # FIX: حالا فرم واقعی هر بازیکن (از /form) استفاده می‌شه
            attacker_form = p1_form if attacker is c1 else p2_form

            skill = pick_skill(attacker["name"], skills_db, attacker_form)
            damage, crit = calculate_damage(attacker, defender, skill)

            if attacker is c1:
                c1_skills_used[skill["name"]] = c1_skills_used.get(skill["name"], 0) + 1

            if defender is c1:
                hp1 -= damage
            else:
                hp2 -= damage

            crit_text = " 💥 CRIT!" if crit else ""
            log.append(
                f"Turn {turn}: {attacker['name']} used {skill['name']} "
                f"→ {damage} dmg{crit_text}"
            )

            if hp1 <= 0 or hp2 <= 0:
                break

        turn += 1

    winner = c1["name"] if hp1 > hp2 else c2["name"]
    earned_money = 100 + random.randint(0, 100)

    log.append("━━━━━━━━━━━━━━━━━━━━━━")
    log.append(f"🏆 Winner: {winner}!")
    log.append(f"💰 Reward: +{earned_money}")

    return log, winner, earned_money, max(0, hp1), max(0, hp2), c1_skills_used
