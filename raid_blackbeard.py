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

def blackbeard(user_id):
    player = get_player(user_id)
    if not player:
        return "❌ پلیر پیدا نشد"

    character, p_hp, max_hp, level, xp, money = player

    bb_hp = 1600 + level * 300
    bb_attack = 120 + level * 25
    bb_defense = 60 + level * 15

    log = ["☠️ RAID BOSS: BLACKBEARD STARTED!"]

    while p_hp > 0 and bb_hp > 0:

        damage, crit = compute_damage(
            base_damage=90 + level * 20,
            mastery=level * 3,
            form_multiplier=1.5,
            crit_chance=12,
            enemy_defense=bb_defense
        )
        bb_hp -= damage
        log.append(f"{'🔥 CRIT! ' if crit else '⚔️ '}شما {damage} به Blackbeard زدی")

        if bb_hp <= 0:
            break

        attack_type = random.randint(1, 100)
        bb_damage = bb_attack

        if attack_type > 80:
            bb_damage *= 2
            log.append("🌑 BLACKBEARD DARK DARK MODE!")

        if attack_type < 15:
            nullify = True
            log.append("💀 Blackbeard قدرتت رو نالیفای کرد! دمیج نصف شد")
            damage = damage // 2

        if attack_type > 90:
            quake = random.randint(50, 150)
            p_hp -= quake
            log.append(f"🌊 TREMOR TREMOR! {quake} دمیج اضافه!")

        bb_damage = max(1, bb_damage - (level * 2))
        p_hp -= bb_damage
        log.append(f"💀 Blackbeard {bb_damage} دمیج زد")

    if p_hp > 0:
        xp_gain = 300 + level * 50
        money_gain = 200 + level * 40
        update_player(user_id, max_hp, xp_gain, money_gain)
        loot = random.choice(["Dark Fragment", "Tremor Core", "Yami Yami Shard", "Blackbeard Essence"])
        log += ["\n🏆 YOU DEFEATED BLACKBEARD!", f"✨ XP +{xp_gain}", f"💰 Money +{money_gain}", f"🎁 Loot: {loot}"]
    else:
        update_player(user_id, max_hp, 25, 25)
        log += ["\n☠️ YOU LOST AGAINST BLACKBEARD!", "❤️ HP restored"]

    return "\n".join(log)
