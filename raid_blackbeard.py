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
# BLACKBEARD RAID
# =========================
def blackbeard(user_id):
    player = get_player(user_id)

    if not player:
        return "❌ پلیر پیدا نشد"

    character, p_hp, max_hp, level, xp, money = player

    bb_hp = 1800 + level * 320
    bb_attack = 130 + level * 28
    bb_defense = 80 + level * 20

    log = []
    log.append("🖤 RAID BOSS: BLACKBEARD STARTED!")

    # =========================
    # DARKNESS MODE SYSTEM
    # =========================
    darkness_mode = False

    # =========================
    # FIGHT LOOP
    # =========================
    while p_hp > 0 and bb_hp > 0:

        # PLAYER ATTACK
        damage, crit = compute_damage(
            base_damage=95 + level * 22,
            mastery=level * 4,
            form_multiplier=1.5,
            crit_chance=15,
            enemy_defense=bb_defense
        )

        bb_hp -= damage

        if crit:
            log.append(f"🔥 CRIT! شما {damage} به Blackbeard زدی")
        else:
            log.append(f"⚔️ شما {damage} به Blackbeard زدی")

        if bb_hp <= 0:
            break

        # =========================
        # BLACKBEARD ATTACK
        # =========================
        attack_roll = random.randint(1, 100)

        bb_damage = bb_attack

        # 🖤 Darkness Mode (مهارت اصلی)
        if attack_roll > 75:
            darkness_mode = True
            bb_damage *= 2
            log.append("🖤 DARKNESS MODE ACTIVATED!")

        # 🌑 Gravity Pull