# raid_blackbeard.py
import random
from database import db, cursor
from characters import characters


def blackbeard(user_id: int):
    """
    Raid: Marshall D. Teach (Blackbeard)
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

    # Blackbeard Stats - دو Devil Fruit داره!
    boss_hp = 5500 + level * 220
    boss_attack = 210 + level * 9
    boss_defense = 160 + level * 3

    player_hp = hp
    log = [
        "☠️ RAID BOSS: Marshall D. Teach (Blackbeard)!",
        f"💀 Boss HP: {boss_hp}",
        f"⚔️ تو: {char_name} | HP: {player_hp}",
        "⚠️ Blackbeard دو Devil Fruit داره: Yami Yami & Gura Gura!",
        "━━━━━━━━━━━━━━━━━━━━━━",
    ]

    yami_active = False
    turn = 1
    while player_hp > 0 and boss_hp > 0 and turn <= 25:
        # حمله بازیکن
        # Yami Yami: هاکی بازیکن رو خنثی می‌کنه
        if yami_active:
            dmg = int((player_attack * 0.7 * random.uniform(0.8, 1.0)) - boss_defense * 0.2)
            log.append(f"Turn {turn}: Yami Yami هاکیت رو خنثی کرد! {max(1, dmg)} زدی")
        else:
            dmg = int((player_attack * random.uniform(0.9, 1.2)) - boss_defense * 0.2)
            log.append(f"Turn {turn}: تو {max(1, dmg)} زدی به Blackbeard")

        boss_hp -= max(1, dmg)
        yami_active = False

        if boss_hp <= 0:
            break

        # حمله Boss
        attack_type = random.randint(1, 3)
        if attack_type == 1:
            b_dmg = int(boss_attack * random.uniform(0.9, 1.1))
            log.append(f"Turn {turn}: Black Hole! {b_dmg} DMG!")
        elif attack_type == 2:
            b_dmg = int(boss_attack * 1.4 * random.uniform(0.9, 1.1))
            log.append(f"Turn {turn}: 🌍 Gura Gura! Quake Punch: {b_dmg} DMG!")
        else:
            b_dmg = int(boss_attack * 0.5)
            yami_active = True
            log.append(f"Turn {turn}: ☠️ Yami Yami فعال شد! دفعه بعد هاکیت کار نمی‌کنه. {b_dmg} DMG")

        b_dmg = max(1, int(b_dmg - player_defense * 0.3))
        player_hp -= b_dmg
        turn += 1

    won = player_hp > 0
    final_hp = max(1, player_hp) if won else max_hp

    cursor.execute("UPDATE players SET hp=? WHERE user_id=?", (final_hp, user_id))
    db.commit()

    log.append("━━━━━━━━━━━━━━━━━━━━━━")
    if won:
        log.append("🏆 Blackbeard شکست خورد! دو Devil Fruit رو شکست دادی!")
    else:
        log.append("💀 Blackbeard پیروز شد! HP ریست شد.")

    return "\n".join(log), won
