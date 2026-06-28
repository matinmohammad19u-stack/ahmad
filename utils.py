import random
import time


# =========================
# RANDOM HELPERS
# =========================
def random_damage(base_damage: int, variance: int = 10):
    """
    دمیج رو کمی رندوم می‌کنه (برای واقعی شدن فایت)
    """
    return max(1, base_damage + random.randint(-variance, variance))


def chance(percent: int) -> bool:
    """
    درصد شانس (مثلاً کریتیکال)
    """
    return random.randint(1, 100) <= percent


# =========================
# COOLDOWN HELPERS
# =========================
def current_time():
    return int(time.time())


def is_on_cooldown(end_time: int) -> bool:
    return current_time() < end_time


def remaining_cooldown(end_time: int) -> int:
    return max(0, end_time - current_time())


# =========================
# TEXT HELPERS
# =========================
def bar(current: int, max_value: int, size: int = 10):
    """
    HP bar ساده برای نمایش فایت
    """
    if max_value == 0:
        return "[----------]"

    filled = int((current / max_value) * size)
    return "█" * filled + "░" * (size - filled)


# =========================
# LEVEL SYSTEM HELPERS
# =========================
def xp_to_level(xp: int) -> int:
    """
    تبدیل XP به لول ساده
    """
    return (xp // 100) + 1


def xp_required(level: int) -> int:
    """
    XP لازم برای لول بعدی
    """
    return level * 100