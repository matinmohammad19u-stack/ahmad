from database import db, cursor
import random
import asyncio

# =========================
# GET PLAYER FULL DATA
# =========================
def get_player(user_id):
    cursor.execute("""
        SELECT hp, max_hp, level, current_form, form_multiplier
        FROM players
        WHERE user_id = ?
    """, (user_id,))
    return cursor.fetchone()


# =========================
# UPDATE HP
# =========================
def update_hp(user_id, hp):
    cursor.execute("""
        UPDATE players
        SET hp = ?
        WHERE user_id = ?
    """, (hp, user_id))
    db.commit()


# =========================
# GET SKILL DAMAGE
# =========================
def calc_damage(base_damage, form_multiplier):
    crit = random.randint(1, 100)
    crit_mult = 2 if crit > 90 else 1
    damage = base_damage * form_multiplier * crit_mult
    return int(damage), crit_mult


# =========================
# SAVE FIGHT RESULT
# =========================
def save_fight(user_id, enemy, result, xp, money):
    cursor.execute("""
        INSERT INTO fight_history (user_id, enemy, result, reward_xp, reward_money)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, enemy, result, xp, money))
    db.commit()


# =========================
# PVP FIGHT
# =========================
def fight(user_id, enemy_name, player_skill_damage):
    player = get_player(user_id)

    if not player:
        return "❌ پلیر پیدا نشد"

    player_hp, player_max_hp, level, form, multiplier = player

    enemy_hp = 1000 + (level * 100)

    log = []
    log.append(f"⚔️ Battle Start: You vs {enemy_name}")
    log.append(f"❤️ HP: {player_hp} vs {enemy_hp}")

    turn = 1

    while player_hp > 0 and enemy_hp > 0:

        dmg, crit = calc_damage(player_skill_damage, multiplier)
        enemy_hp -= dmg
        log.append(f"🟦 Turn {turn}: You hit {dmg} dmg")

        if enemy_hp <= 0:
            break

        enemy_dmg = random.randint(80, 150)
        player_hp -= enemy_dmg
        log.append(f"🟥 Turn {turn}: Enemy hits {enemy_dmg} dmg")

        turn += 1

    if player_hp > 0:
        result = "WIN"
        xp = 50 + level * 10
        money = 100 + level * 20
        msg = "🏆 YOU WIN!"
    else:
        result = "LOSE"
        xp = 10
        money = 20
        msg = "💀 YOU LOSE!"

    save_fight(user_id, enemy_name, result, xp, money)
    update_hp(user_id, max(0, player_hp))

    log.append(msg)
    log.append(f"⭐ XP: {xp} 💰 Money: {money}")

    return "\n".join(log)
