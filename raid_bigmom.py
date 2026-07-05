# raid_bigmom.py
import random
from database import db, cursor
from characters import characters


def bigmom(user_id: int):
    """
    Raid: Big Mom (Charlotte Linlin)
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

    # Big Mom Stats
    boss_hp = 5000 + level * 200
    boss_max_hp = boss_hp
    boss_attack = 200 + level * 8
    boss_defense = 150 + level * 3

    player_hp = hp
    log = [
        "👑 RAID BOSS: Charlotte Linlin (Big Mom)!",
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
            # FIX: قبلاً dmg اول به boss_hp اضافه می‌شد، بعد dmg دوباره
            # ۱.۵ برابر می‌شد و نصفش دوباره کم می‌شد → دمیج واقعی وارد‌شده
            # (۱.۷۵x) با چیزی که توی لاگ نشون داده می‌شد (۱.۵x) یکی نبود.
            # الان دقیقاً مثل raid_kaido.py: یه bonus جدا (نصف dmg اصلی)
            # کم می‌شه و توی لاگ هم دقیقاً مجموع واقعی نشون داده می‌شه.
            bonus = dmg // 2
            boss_hp -= bonus
            log.append(f"Turn {turn}: تو {dmg + bonus} 💥CRIT زدی!")
        else:
            log.append(f"Turn {turn}: تو {dmg} زدی به Big Mom")

        if boss_hp <= 0:
            break

        # حمله Boss
        special = random.random() < 0.15
        if special:
            b_dmg = int(boss_attack * 2 * random.uniform(0.9, 1.1))
            log.append(f"Turn {turn}: ⚡ Big Mom از Ikoku استفاده کرد! {b_dmg} DMG!")
        else:
            b_dmg = int((boss_attack - player_defense * 0.3) * random.uniform(0.8, 1.2))
            b_dmg = max(1, b_dmg)
            log.append(f"Turn {turn}: Big Mom {b_dmg} زد!")

        player_hp -= b_dmg
        turn += 1

    # FIX: قبلاً اگه به سقف ۲۵ راند می‌رسید بدون اینکه کسی صفر بشه، بازیکن
    # همیشه "برنده" حساب می‌شد (چون player_hp > 0 تقریباً همیشه درسته،
    # حتی اگه boss_hp هنوز خیلی بالا باشه). الان مثل fight.py، بر اساس
    # درصد HP باقیمونده‌ی هرکدوم برنده مشخص می‌شه.
    if turn > 25 and player_hp > 0 and boss_hp > 0:
        player_pct = player_hp / max_hp if max_hp else 0
        boss_pct = boss_hp / boss_max_hp if boss_max_hp else 0
        won = player_pct >= boss_pct
        log.append("⏱️ سقف راندها رسید! بر اساس HP باقیمونده برنده مشخص شد.")
    else:
        won = player_hp > 0
    final_hp = max(1, player_hp) if won else max_hp  # اگه باخت HP ریست

    cursor.execute("UPDATE players SET hp=? WHERE user_id=?", (final_hp, user_id))
    db.commit()

    log.append("━━━━━━━━━━━━━━━━━━━━━━")
    if won:
        log.append("🏆 Big Mom کشتی! Yonko رو شکست دادی!")
    else:
        log.append("💀 Big Mom پیروز شد! HP ریست شد.")

    return "\n".join(log), won
