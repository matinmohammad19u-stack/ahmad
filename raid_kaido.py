# raid_kaido.py
import random
from database import db, cursor
from characters import characters


def kaido(user_id: int):
    """
    Raid: Kaido (King of Beasts)
    برمی‌گردونه: (result_text, won_bool)
    """
    cursor.execute(
        "SELECT character, hp, max_hp, level FROM players WHERE user_id=?",
        (user_id,)
    )
    data = cursor.fetchone()

    if not data or not data[0]:
        return "❌ شخصیت نداری!", False

    char_name, hp, max_hp, level = data

    if hp <= 0:
        return "❌ HP نداری! از /daily استفاده کن.", False

    char_stats = characters[char_name]["stats"]
    player_attack = char_stats["attack"]
    player_defense = char_stats["defense"]

    # Kaido Stats
    boss_hp = 6000 + level * 250
    boss_attack = 220 + level * 10
    boss_defense = 180 + level * 4

    player_hp = hp
    log = [
        "🐉 RAID BOSS: Kaido (King of Beasts)!",
        f"❤️ Boss HP: {boss_hp}",
        f"⚔️ تو: {char_name} | HP: {player_hp}",
        "━━━━━━━━━━━━━━━━━━━━━━",
    ]

    turn = 1
    while player_hp > 0 and boss_hp > 0 and turn <= 25:
        # حمله بازیکن
        dmg = int((player_attack * random.uniform(0.9, 1.2)) - boss_defense * 0.2)
        dmg = max(1, dmg)
        boss_hp -= dmg
        crit = random.random() < 0.1
        if crit:
            bonus = dmg // 2
            boss_hp -= bonus
            log.append(f"Turn {turn}: تو {dmg + bonus} 💥CRIT زدی!")
        else:
            log.append(f"Turn {turn}: تو {dmg} زدی به Kaido")

        if boss_hp <= 0:
            break

        # حمله Boss - Kaido فازهای مختلف داره
        phase = turn // 8
        if phase == 0:
            b_dmg = int(boss_attack * random.uniform(0.9, 1.1))
            log.append(f"Turn {turn}: Kaido با Bolo Breath {b_dmg} زد!")
        elif phase == 1:
            b_dmg = int(boss_attack * 1.3 * random.uniform(0.9, 1.1))
            log.append(f"Turn {turn}: 🐉 Dragon Kaido! Thunder Bagua: {b_dmg} DMG!")
        else:
            b_dmg = int(boss_attack * 1.6 * random.uniform(0.9, 1.1))
            log.append(f"Turn {turn}: ⚡ Hybrid Kaido! Ragnaraku: {b_dmg} DMG!")

        b_dmg = max(1, int(b_dmg - player_defense * 0.3))
        player_hp -= b_dmg
        turn += 1

    won = player_hp > 0
    final_hp = max(1, player_hp) if won else max_hp

    cursor.execute("UPDATE players SET hp=? WHERE user_id=?", (final_hp, user_id))
    db.commit()

    log.append("━━━━━━━━━━━━━━━━━━━━━━")
    if won:
        log.append("🏆 Kaido افتاد! تو قوی‌ترین موجود در دنیا رو شکست دادی!")
    else:
        log.append("💀 Kaido پیروز شد! HP ریست شد.")

    return "\n".join(log), won
