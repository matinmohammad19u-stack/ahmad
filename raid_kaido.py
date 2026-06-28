import sqlite3

from compute_damage import compute_damage

db = sqlite3.connect("game.db", check_same_thread=False)
cursor = db.cursor()


def get_player(user_id):
    cursor.execute("""
        SELECT character, hp, max_hp, level, xp, money
        FROM players
        WHERE user_id = ?
    """, (user_id,))
    return cursor.fetchone()


def update_player(user_id, hp, xp_gain, money_gain):
    cursor.execute("""
        UPDATE players
        SET hp = ?,
            xp = xp + ?,
            money = money + ?
        WHERE user_id = ?
    """, (hp, xp_gain, money_gain, user_id))

    db.commit()


# =========================
# KAIDO BOSS
# =========================
def kaido(user_id):
    player = get_player(user_id)

    if not player:
        return "❌ پلیر پیدا نشد"

    character, p_hp, max_hp, level, xp, money = player

    kaido_hp = 1500 + level * 300
    kaido_attack = 120 + level * 25
    kaido_defense = 60 + level * 15

    log = []
    log.append("🐉 RAID BOSS: KAIDO STARTED!")

    # =========================
    # FIGHT LOOP
    # =========================
    while p_hp > 0 and kaido_hp > 0:

        # PLAYER ATTACK
        damage, crit = compute_damage(
            base_damage=90 + level * 20,
            mastery=level * 4,
            form_multiplier=1.5,
            crit_chance=15,
            enemy_defense=kaido_defense
        )

        kaido_hp -= damage

        if crit:
            log.append(f"🔥 CRIT! شما {damage} به Kaido زدی")
        else:
            log.append(f"⚔️ شما {damage} به Kaido زدی")

        if kaido_hp <= 0:
            break

        # KAIDO ATTACK (خیلی سنگین)
        import random

        rage = random.randint(1, 100)

        kaido_damage = kaido_attack

        # 🔥 Rage mode (گاهی دمیج دو برابر)
        if rage > 85:
            kaido_damage *= 2
            log.append("🐉 KAIDO RAGE MODE!")

        kaido_damage = max(1, kaido_damage - (level * 2))
        p_hp -= kaido_damage

        log.append(f"💀 Kaido {kaido_damage} دمیج زد")

    # =========================
    # RESULT
    # =========================
    if p_hp > 0:
        xp_gain = 300 + level * 50
        money_gain = 200 + level * 40

        update_player(user_id, max_hp, xp_gain, money_gain)

        loot_pool = [
            "Dragon Scale",
            "Mythic Weapon",
            "Advanced Haki Scroll",
            "Kaido Fragment (Rare)"
        ]

        import random
        loot = random.choice(loot_pool)

        log.append("\n🏆 YOU DEFEATED KAIDO!")
        log.append(f"✨ XP +{xp_gain}")
        log.append(f"💰 Money +{money_gain}")
        log.append(f"🎁 Loot: {loot}")

        return "\n".join(log)

    else:
        update_player(user_id, max_hp, 30, 30)

        log.append("\n☠️ YOU LOST AGAINST KAIDO!")
        log.append("❤️ HP restored")

        return "\n".join(log)