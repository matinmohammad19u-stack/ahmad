import random
import copy

cooldowns = {}


def get_form(character_name, skills_db):
    forms = list(skills_db[character_name].keys())
    return forms[0]


def pick_skill(character_name, skills_db):
    form = get_form(character_name, skills_db)
    return random.choice(skills_db[character_name][form])


def calculate_damage(attacker, defender, skill):
    base = skill["damage"]
    atk = attacker["stats"]["attack"]
    dfs = defender["stats"]["defense"]

    dmg = base + (atk * 0.8) - (dfs * 0.5)
    dmg *= random.uniform(0.9, 1.1)

    crit = random.random() < 0.1
    if crit:
        dmg *= 1.5

    return max(0, int(dmg)), crit


def turn_order(p1, p2):
    if p1["stats"]["speed"] > p2["stats"]["speed"]:
        return [p1, p2]
    if p2["stats"]["speed"] > p1["stats"]["speed"]:
        return [p2, p1]
    return random.sample([p1, p2], 2)


# =========================
# ⚔️ BATTLE
# =========================
def battle(p1, p2, skills_db):

    c1 = copy.deepcopy(p1)
    c2 = copy.deepcopy(p2)

    hp1 = c1["stats"]["hp"]
    hp2 = c2["stats"]["hp"]

    turn = 1
    log = []

    log.append(f"⚔️ {c1['name']} VS {c2['name']} START!")

    while hp1 > 0 and hp2 > 0:

        order = turn_order(c1, c2)

        for attacker in order:

            defender = c2 if attacker == c1 else c1

            skill = pick_skill(attacker["name"], skills_db)

            damage, crit = calculate_damage(attacker, defender, skill)

            if defender == c1:
                hp1 -= damage
            else:
                hp2 -= damage

            log.append(
                f"Turn {turn}: {attacker['name']} used {skill['name']} "
                f"-> {damage} dmg" + (" 💥 CRIT!" if crit else "")
            )

            if hp1 <= 0 or hp2 <= 0:
                break

        turn += 1

    winner = c1["name"] if hp1 > 0 else c2["name"]

    earned_money = 100 + random.randint(0, 60)

    log.append(f"🏆 Winner: {winner}")
    log.append(f"🎉 Reward: +{earned_money} 💰")

    return log, winner, earned_money
