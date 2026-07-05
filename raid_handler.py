# raid_handler.py
#
# بازنویسی کامل: قبلاً هر Raid Boss (Big Mom/Kaido/Blackbeard) یه فایت
# خودکار و بی‌دکمه بود (راید_bigmom.py و بقیه، فقط یه لاگ متنی برمی‌گردوندن).
# الان دقیقاً از همون موتور fight.py که برای PVP استفاده می‌شه استفاده
# می‌کنیم → یعنی فایت با راید باس واقعاً "مثل فایت با یه پلیر" شده: دکمه،
# انتخاب اسکیل، جاخالی، دفاع. باس هم توی نوبت خودش با AI ساده (رندوم بین
# اسکیل‌ها/جاخالی/دفاعِ خودش) بازی می‌کنه.
#
# + کول‌داون ۵ دقیقه‌ای بعد از کشتن یه باس (تا قبلش می‌شه هر چقدر خواستی
#   باهاش فایت بدی، حتی اگه ببازی).
# + شانس خیلی کم (۵٪) دراپ آیتم مخصوص همون باس، با رریتی‌ای که به لولِ
#   جزیره‌ی باس بستگی داره.

import time
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from database import db, cursor
from characters import characters
from skill import SKILL_DB
from fight import create_battle, apply_action, get_actions
from raid_bosses import (
    RAID_BOSSES, COOLDOWN_SECONDS, RARE_DROP_CHANCE,
    get_boss_stats, get_boss_form, get_rarity_multiplier, get_drop_item_name
)
from passive_system import apply_passive

# مثل active_battles توی main.py: یه دیکشنری ساده و global، کلیدش user_id
# (چون راید همیشه یه‌نفره‌س، نیازی به battle_id جدا نیست)
active_raid_battles = {}


def _remaining_cooldown(user_id: int, boss_id: str) -> int:
    cursor.execute(
        "SELECT defeated_at FROM boss_cooldowns WHERE user_id=? AND boss_id=?",
        (user_id, boss_id)
    )
    row = cursor.fetchone()
    if not row:
        return 0
    elapsed = time.time() - row[0]
    remaining = COOLDOWN_SECONDS - elapsed
    return max(0, int(remaining))


async def raid(update, context):
    user = update.effective_user
    cursor.execute("SELECT character, hp FROM players WHERE user_id=?", (user.id,))
    data = cursor.fetchone()
    if not data or not data[0]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    if data[1] <= 0:
        await update.message.reply_text("❌ HP نداری! از /daily استفاده کن.")
        return

    buttons = []
    lines = ["⚔️ Raid Boss — کدوم رو می‌خوای بزنی؟\n"]
    for boss_id, info in RAID_BOSSES.items():
        cd = _remaining_cooldown(user.id, boss_id)
        if cd > 0:
            m, s = divmod(cd, 60)
            lines.append(f"{info['display']} — ⏳ کول‌داون: {m}:{s:02d}")
            buttons.append([InlineKeyboardButton(f"⏳ {info['display']}", callback_data="raid_cd_locked")])
        else:
            lines.append(f"{info['display']} — ✅ آماده")
            buttons.append([InlineKeyboardButton(info["display"], callback_data=f"raid_{boss_id}")])

    await update.message.reply_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(buttons))


def _boss_ai_pick(state) -> int:
    """باس توی نوبت خودش یه اکشن رندوم انتخاب می‌کنه (شامل جاخالی/دفاع اگه شارژ داشته باشه)."""
    actions = get_actions(state, "p2")
    return random.randrange(len(actions))


def _build_action_keyboard(state):
    actions = get_actions(state, "p1")
    buttons = [
        [InlineKeyboardButton(a["name"], callback_data=f"ratk_{i}")]
        for i, a in enumerate(actions)
    ]
    return InlineKeyboardMarkup(buttons)


async def raid_callback(update, context):
    """دکمه‌ی انتخاب باس (raid_<boss_id>) توی منوی /raid زده شد → شروع فایت."""
    query = update.callback_query
    user = query.from_user

    if query.data == "raid_cd_locked":
        await query.answer("⏳ این باس هنوز کول‌داونه!", show_alert=True)
        return

    boss_id = query.data[len("raid_"):]
    if boss_id not in RAID_BOSSES:
        await query.answer("❌ باس نامعتبره")
        return

    cd = _remaining_cooldown(user.id, boss_id)
    if cd > 0:
        m, s = divmod(cd, 60)
        await query.answer(f"⏳ {m}:{s:02d} دیگه مونده تا این باس دوباره ظاهر شه!", show_alert=True)
        return

    cursor.execute("SELECT character, hp, level FROM players WHERE user_id=?", (user.id,))
    data = cursor.fetchone()
    if not data or not data[0]:
        await query.answer("❌ اول /character_select بزن.", show_alert=True)
        return
    char_name, hp, level = data
    if hp <= 0:
        await query.answer("❌ HP نداری! از /daily استفاده کن.", show_alert=True)
        return

    info = RAID_BOSSES[boss_id]
    player_stats = apply_passive(char_name, dict(characters[char_name]["stats"], hp=hp))
    boss_stats = get_boss_stats(boss_id, level)
    boss_form = get_boss_form(boss_id)

    p1 = {"name": char_name, "stats": player_stats}
    p2 = {"name": info["character"], "stats": boss_stats}
    state = create_battle(p1, p2, SKILL_DB, p1_form="Base", p2_form=boss_form)

    active_raid_battles[user.id] = {"state": state, "boss_id": boss_id}

    # FIX: قبلاً همیشه فرض می‌شد نوبت اول با پلیره. اگه باس سریع‌تر باشه
    # (state["turn"] == "p2")، باید همون‌جا خودکار حرکت اول باسو بزنیم
    # (چون طرف دومِ راید یه AI ـه، نه یه انسانِ منتظر) وگرنه اولین دکمه‌ای
    # که پلیر می‌زد با "not this side's turn" کرش می‌کرد.
    if state["turn"] == "p2" and not state["finished"]:
        apply_action(state, "p2", _boss_ai_pick(state))

    await query.answer()

    if state["finished"]:
        del active_raid_battles[user.id]
        won = (state["winner"] == "p1")
        await _finish_raid(query, user, won=won, boss_id=boss_id, state=state)
        return
    text = "\n".join(state["log"]) + "\n\n🎯 نوبت توعه! یه اسکیل انتخاب کن:"
    await query.edit_message_text(text, reply_markup=_build_action_keyboard(state))


async def raid_attack_callback(update, context):
    """دکمه‌ی اسکیل/جاخالی/دفاع توی فایتِ راید (ratk_<index>) زده شد."""
    query = update.callback_query
    user = query.from_user

    battle = active_raid_battles.get(user.id)
    if not battle:
        await query.answer("❌ فایتی در حال انجام نیست. با /raid یکی شروع کن.", show_alert=True)
        return

    state = battle["state"]
    boss_id = battle["boss_id"]

    try:
        idx = int(query.data[len("ratk_"):])
    except ValueError:
        idx = 0

    apply_action(state, "p1", idx)

    # اگه با ضربه‌ی خود پلیر تموم شد، دیگه نوبت باس نمی‌رسه
    if not state["finished"]:
        boss_idx = _boss_ai_pick(state)
        apply_action(state, "p2", boss_idx)

    await query.answer()

    if state["finished"]:
        del active_raid_battles[user.id]
        winner = state["winner"]
        won = (winner == "p1")
        await _finish_raid(query, user, won=won, boss_id=boss_id, state=state)
        return

    text = "\n".join(state["log"][-6:]) + "\n\n🎯 نوبت توعه! یه اسکیل انتخاب کن:"
    await query.edit_message_text(text, reply_markup=_build_action_keyboard(state))


async def _finish_raid(query, user, won, boss_id, state):
    info = RAID_BOSSES[boss_id]
    cursor.execute("SELECT max_hp FROM players WHERE user_id=?", (user.id,))
    max_hp = cursor.fetchone()[0]

    final_hp = max(1, state["fighters"]["p1"]["hp"]) if won else max_hp
    lines = state["log"][-6:]

    if won:
        # +15 لول = +1500 پوینت (طبق سیستم پوینت: هر لول = ۱۰۰ پوینت)
        raid_points_gained = 15 * 100
        cursor.execute(
            "UPDATE players SET level=level+15, points=points+?, hp=? WHERE user_id=?",
            (raid_points_gained, final_hp, user.id)
        )
        # کول‌داون ۵ دقیقه‌ای همین باس برای همین کاربر شروع می‌شه
        cursor.execute(
            "INSERT INTO boss_cooldowns (user_id, boss_id, defeated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id, boss_id) DO UPDATE SET defeated_at=excluded.defeated_at",
            (user.id, boss_id, time.time())
        )
        lines.append(f"\n🏆 {info['display']} کشتی! +15 لول 🎯 +{raid_points_gained} پوینت")
        lines.append("⏳ این باس ۵ دقیقه کول‌داونه، بعدش دوباره می‌تونی بزنیش.")

        # شانس خیلی کم دراپ آیتم مخصوص باس (رریتی‌ش به لول جزیره‌ی باس بستگی داره)
        if random.random() < RARE_DROP_CHANCE:
            rarity = get_rarity_multiplier(boss_id)
            bonus_attack = int(8 * rarity)
            item_name = get_drop_item_name(boss_id)
            cursor.execute(
                "INSERT INTO inventory (user_id, item_name, item_type, quantity) VALUES (?, ?, 'raid_relic', 1) "
                "ON CONFLICT(user_id, item_name) DO UPDATE SET quantity=quantity+1",
                (user.id, item_name)
            )
            cursor.execute(
                "UPDATE players SET extra_attack = extra_attack + ? WHERE user_id=?",
                (bonus_attack, user.id)
            )
            lines.append(
                f"\n💎 دراپ نادر! {item_name} گرفتی (Attack دائمی +{bonus_attack})! "
                f"با /inventory ببینش."
            )
    else:
        cursor.execute("UPDATE players SET hp=? WHERE user_id=?", (final_hp, user.id))
        lines.append(f"\n💀 {info['display']} پیروز شد! HP ـت ریست شد. (کول‌داون نداره، دوباره امتحان کن)")

    db.commit()
    await query.edit_message_text("\n".join(lines))
