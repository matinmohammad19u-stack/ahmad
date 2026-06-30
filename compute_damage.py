import random


def compute_damage(
    base_damage: int,
    mastery: int = 0,
    form_multiplier: float = 1.0,
    crit_chance: int = 10,
    enemy_defense: int = 0
):
    """
    ⚔️ سیستم کامل دمیج RPG
    شامل:
    - mastery scaling
    - form multiplier
    - crit system
    - random variance
    - enemy defense reduction
    """

    # =========================
    # 1. MASTERY SCALING
    # هر 100 مستری = +100% قدرت
    # =========================
    mastery_multiplier = 1 + (mastery / 100)

    # =========================
    # 2. RANDOM VARIATION (واقعی‌تر شدن فایت)
    # =========================
    variance = random.uniform(0.9, 1.1)

    # =========================
    # 3. CRIT SYSTEM
    # =========================
    is_crit = random.randint(1, 100) <= crit_chance
    crit_multiplier = 2 if is_crit else 1

    # =========================
    # 4. RAW DAMAGE CALCULATION
    # =========================
    damage = (
        base_damage
        * mastery_multiplier
        * form_multiplier
        * variance
        * crit_multiplier
    )

    # =========================
    # 5. DEFENSE REDUCTION
    # =========================
    damage -= enemy_defense * 0.3

    # =========================
    # 6. MIN DAMAGE SAFETY
    # =========================
    final_damage = max(1, int(damage))

    return final_damage, is_crit
