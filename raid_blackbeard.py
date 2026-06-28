from database import db, cursor
from compute_damage import compute_damage
import random

def get_player(user_id):
    cursor.execute("""
        SELECT character, hp, max_hp, level, xp, money
        FROM players WHERE user_id = ?
    """, (user_id,))
    return cursor.fetchone()

def update_player(user_id, hp, xp_gain, money_gain):
    cursor.execute("""
        UPDATE players SET hp = ?, xp = xp + ?, money = money + ?
        WHERE user_id = ?
    """, (hp, xp_gain, money_gain, user_id))
    db.commit()

def bigmom(user_id):
    player = get_player(user_id)
    if not player:
        return "❌ پلیر پیدا نشد"

    character, p_hp, max_hp, level, xp, money = player

    bm_hp = 1400 + level * 280
    bm_attack = 110 + level * 22
    bm_defense = 70 + level * 18

    log = ["👑 RAID BOSS: BIG MOM STARTED!"]

    while p_hp > 0 and bm_hp > 0:

        damage, crit = compute_damage(
            base_damage=85 + level * 18,
            mastery=level * 3,
            form_multiplier=1.4,
            crit_chance=12,
            enemy_defense=bm_defense
        )
        bm_hp -= damage
        log.append(f"{'🔥 CRIT! ' if crit else '⚔️ '}شما {damage} به Big Mom زدی")

        if bm_hp <= 0:
            break

        attack_type = random.randint(1, 100)
        bm_damage = bm_attack

        if attack_type > 80:
            bm_damage *= 2
            log.append("👻 BIG MOM SOUL MODE!")

        if attack_type < 15:
            heal = 100 + level * 20
            bm_hp += heal
            log.append(f"💖 Big Mom healed {heal} HP!")

        bm_damage = max(1, bm_damage - (level * 2))
        p_hp -= bm_damage
        log.append(f"💀 Big Mom {bm_damage} دمیج زد")

    if p_hp > 0:
        xp_gain = 280 + level * 45
        money_gain = 180 + level * 35
        update_player(user_id, max_hp, xp_gain, money_gain)
        loot = random.choice(["Soul Fragment", "Homie Core", "Mythic Armor", "Big Mom Essence"])
        log += ["\n🏆 YOU DEFEATED BIG MOM!", f"✨ XP +{xp_gain}", f"💰 Money +{money_gain}", f"🎁 Loot: {loot}"]
    else:
        update_player(user_id, max_hp, 25, 25)
        log += ["\n☠️ YOU LOST AGAINST BIG MOM!", "❤️ HP restored"]

    return "\n".join(log)
