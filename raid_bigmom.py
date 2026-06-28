import sqlite3
import random

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
# BIG MOM RAID
# =========================
def bigmom(user_id):
    player = get_player(user_id)

    if not player:
        return "❌ پلیر پیدا نشد"

    character, p_hp, max_hp, level, xp, money = player

    bm_hp = 1400 + level * 280
    bm_attack = 110 + level * 22
    bm_defense = 70 + level * 18

    log = []
    log.append("👑 RAID BOSS: BIG MOM STARTED!")

    # =========================
    # SOUL POWER (ویژگی خاص)
    # =========================
    soul_buff_active = False

    # =========================
    # FIGHT LOOP
    # =========================
    while p_hp > 0 and bm_hp > 0:

        # PLAYER ATTACK
        damage, crit = compute_damage(
            base_damage=85 + level * 18,
            mastery=level * 3,
            form_multiplier=1.4,
            crit_chance=12,
            enemy_defense=bm_defense
        )

        bm_hp -= damage

        if crit:
            log.append(f"🔥 CRIT! شما {damage} به Big Mom زدی")
        else:
            log.append(f"⚔️ شما {damage} به Big Mom زدی")

        if bm_hp <= 0:
            break

        # =========================
        # BIG MOM ATTACK
        # =========================
        attack_type = random.randint(1, 100)

        bm_damage = bm_attack

        # 🔥 Soul boost (هر از گاهی خشم روح‌ها)
        if attack_type > 80:
            bm_damage *= 2
            soul_buff_active = True
            log.append("👻 BIG MOM SOUL MODE!")

        # 🔥 Healing ability (خاص بیگ مام)
        if attack_type < 15:
            heal = 100 + level * 20
            bm_hp += heal
            log.append(f"💖 Big Mom healed {heal} HP!")

        bm_damage = max(1, bm_damage - (level * 2))
        p_hp -= bm_damage

        log.append(f"💀 Big Mom {bm_damage} دمیج زد")

    # =========================
    # RESULT
    # =========================
    if p_hp > 0:
        xp_gain = 280 + level * 45
        money_gain = 180 + level * 35

        update_player(user_id, max_hp, xp_gain, money_gain)

        loot_pool = [
            "Soul Fragment",
            "Homie Core",
            "Mythic Armor",
            "Big Mom Essence"
        ]

        loot = random.choice(loot_pool)

        log.append("\n🏆 YOU DEFEATED BIG MOM!")
        log.append(f"✨ XP +{xp_gain}")
        log.append(f"💰 Money +{money_gain}")
        log.append(f"🎁 Loot: {loot}")

        return "\n".join(log)

    else:
        update_player(user_id, max_hp, 25, 25)

        log.append("\n☠️ YOU LOST AGAINST BIG MOM!")
        log.append("❤️ HP restored")

        return "\n".join(log)