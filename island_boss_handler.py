# island_boss_handler.py
#
# فایت دکمه‌ای (مثل PVP) با باس‌های جزیره‌ای (همون ۴۸ باس داخل
# island_bosses.py؛ Big Mom/Kaido/Blackbeard جدان و با /raid زده می‌شن).
# دقیقاً همون قوانین راید رو داره: چندبار فایت آزاد، ۵ دقیقه کول‌داون
# فقط بعد از کشتن، ۵٪ شانس دراپ آیتم مخصوص با رریتی‌ی وابسته به لولِ
# جزیره، و پسیوِ خودِ شخصیت هم اعمال می‌شه.

import time
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from database import db, cursor
from characters import characters
from islands import islands
from skill import SKILL_DB
from fight import create_battle, apply_action, get_actions
from island_bosses import (
    ISLAND_BOSSES, RAID_REDIRECT, COOLDOWN_SECONDS, RARE_DROP_CHANCE,
    get_bosses_for_island, get_boss_stats, get_boss_skills_and_form,
    get_rarity_multiplier, get_drop_item_name
)
from passive_system import apply_passive

# دیکشنری global، کلیدش user_id (هر پلیر همزمان فقط یه فایت باس-جزیره‌ای)
active_island_battles = {}


def _remaining_cooldown(user_id: int, boss_id: str) -> int:
    cursor.execute(
        "SELECT defeated_at FROM boss_cooldowns WHERE user_id=? AND boss_id=?",
        (user_id, boss_id)
    )
    row = cursor.fetchone()
    if not row:
        return 0
    remaining = COOLDOWN_SECONDS - (time.time() - row[0])
    return max(0, int(remaining))


def _get_current_island(user_id: int) -> str:
    cursor.execute("SELECT level, current_island FROM players WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        return "East Blue"
    level, current_island = row
    if not current_island or current_island not in islands:
        current_island = "East Blue"
    if current_island == "East Blue":
        candidates = [n for n, d in islands.items() if level >= d["required_level"]]
        if candidates:
            best = max(candidates, key=lambda n: islands[n]["required_level"])
            if best != "East Blue":
                current_island = best
                cursor.execute("UPDATE players SET current_island=? WHERE user_id=?", (current_island, user_id))
                db.commit()
    return current_island


async def island_boss_cmd(update, context):
    """لیست باس‌های جزیره‌ی فعلی پلیر (با وضعیت کول‌داون)."""
    user = update.effective_user
    cursor.execute("SELECT character, hp FROM players WHERE user_id=?", (user.id,))
    data = cursor.fetchone()
    if not data or not data[0]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    if data[1] <= 0:
        await update.message.reply_text("❌ HP نداری! از /daily استفاده کن.")
        return

    current_island = _get_current_island(user.id)
    bosses = get_bosses_for_island(current_island)

    lines = [f"🗺️ باس‌های {current_island}:\n"]
    buttons = []

    # اگه یکی از Yonkoهای راید (Big Mom/Kaido/Blackbeard) توی این جزیره باشه، راهنمایی می‌کنیم
    for name in RAID_REDIRECT:
        from raid_bosses import RAID_BOSSES
        for boss_id, info in RAID_BOSSES.items():
            if info["island"] == current_island:
                lines.append(f"👑 {name} — این یه Raid Boss ـه! با /raid بزنش.")

    if not bosses:
        lines.append("این جزیره باس جزیره‌ای دیگه‌ای نداره.")
    for boss_id, b in bosses.items():
        cd = _remaining_cooldown(user.id, boss_id)
        label = f"Part {b['part_num']} ({b['part_name']}) — {b['display']}"
        if cd > 0:
            m, s = divmod(cd, 60)
            lines.append(f"⏳ {label} — کول‌داون {m}:{s:02d}")
            buttons.append([InlineKeyboardButton(f"⏳ {b['display']}", callback_data="ibpick_locked")])
        else:
            lines.append(f"✅ {label}")
            buttons.append([InlineKeyboardButton(b["display"], callback_data=f"ibpick_{boss_id}")])

    await update.message.reply_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(buttons))


def _boss_ai_pick(state) -> int:
    actions = get_actions(state, "p2")
    return random.randrange(len(actions))


def _build_action_keyboard(state):
    actions = get_actions(state, "p1")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(a["name"], callback_data=f"ibatk_{i}")]
        for i, a in enumerate(actions)
    ])


async def island_boss_pick_callback(update, context):
    query = update.callback_query
    user = query.from_user

    if query.data == "ibpick_locked":
        await query.answer("⏳ این باس هنوز کول‌داونه!", show_alert=True)
        return

    boss_id = query.data[len("ibpick_"):]
    if boss_id not in ISLAND_BOSSES:
        await query.answer("❌ باس نامعتبره", show_alert=True)
        return

    cd = _remaining_cooldown(user.id, boss_id)
    if cd > 0:
        m, s = divmod(cd, 60)
        await query.answer(f"⏳ {m}:{s:02d} دیگه مونده تا این باس دوباره ظاهر شه!", show_alert=True)
        return

    cursor.execute("SELECT character, hp FROM players WHERE user_id=?", (user.id,))
    data = cursor.fetchone()
    if not data or not data[0]:
        await query.answer("❌ اول /character_select بزن.", show_alert=True)
        return
    char_name, hp = data
    if hp <= 0:
        await query.answer("❌ HP نداری! از /daily استفاده کن.", show_alert=True)
        return

    b = ISLAND_BOSSES[boss_id]
    cursor.execute("SELECT level FROM players WHERE user_id=?", (user.id,))
    level = cursor.fetchone()[0]

    player_stats = apply_passive(char_name, dict(characters[char_name]["stats"], hp=hp))
    boss_stats = get_boss_stats(boss_id, level)
    skills, form, boss_char_name = get_boss_skills_and_form(boss_id)

    # اگه باس یه کاراکتر واقعی توی SKILL_DB باشه، مستقیم از SKILL_DB استفاده
    # می‌شه؛ وگرنه یه کپی از SKILL_DB می‌سازیم و فقط یه ورودی مصنوعی برای
    # این باس بهش اضافه می‌کنیم (تا اسکیل‌های خودِ پلیر هم درست پیدا شن)
    if boss_char_name in SKILL_DB:
        skills_db_for_fight = SKILL_DB
    else:
        skills_db_for_fight = dict(SKILL_DB)
        skills_db_for_fight[boss_char_name] = {form: skills}

    p1 = {"name": char_name, "stats": player_stats}
    p2 = {"name": boss_char_name, "stats": boss_stats}
    state = create_battle(p1, p2, skills_db_for_fight, p1_form="Base", p2_form=form)

    active_island_battles[user.id] = {"state": state, "boss_id": boss_id}

    # FIX: همون باگ راید؛ اگه باس سریع‌تر باشه باید حرکت اولش خودکار زده
    # شه، وگرنه اولین دکمه‌ی پلیر با "not this side's turn" کرش می‌کرد.
    if state["turn"] == "p2" and not state["finished"]:
        apply_action(state, "p2", _boss_ai_pick(state))

    await query.answer()

    if state["finished"]:
        del active_island_battles[user.id]
        won = (state["winner"] == "p1")
        await _finish_island_boss(query, user, won, boss_id, state)
        return
    text = "\n".join(state["log"]) + "\n\n🎯 نوبت توعه! یه اسکیل انتخاب کن:"
    await query.edit_message_text(text, reply_markup=_build_action_keyboard(state))


async def island_boss_attack_callback(update, context):
    query = update.callback_query
    user = query.from_user

    battle = active_island_battles.get(user.id)
    if not battle:
        await query.answer("❌ فایتی در حال انجام نیست. با /island_boss یکی شروع کن.", show_alert=True)
        return

    state = battle["state"]
    boss_id = battle["boss_id"]

    try:
        idx = int(query.data[len("ibatk_"):])
    except ValueError:
        idx = 0

    apply_action(state, "p1", idx)
    if not state["finished"]:
        apply_action(state, "p2", _boss_ai_pick(state))

    await query.answer()

    if state["finished"]:
        del active_island_battles[user.id]
        won = (state["winner"] == "p1")
        await _finish_island_boss(query, user, won, boss_id, state)
        return

    text = "\n".join(state["log"][-6:]) + "\n\n🎯 نوبت توعه! یه اسکیل انتخاب کن:"
    await query.edit_message_text(text, reply_markup=_build_action_keyboard(state))


async def _finish_island_boss(query, user, won, boss_id, state):
    b = ISLAND_BOSSES[boss_id]
    cursor.execute("SELECT max_hp FROM players WHERE user_id=?", (user.id,))
    max_hp = cursor.fetchone()[0]
    final_hp = max(1, state["fighters"]["p1"]["hp"]) if won else max_hp
    lines = state["log"][-6:]

    if won:
        # پاداش کوچیک‌تر از راید (این باس‌ها آسون‌تر از یونکو‌ها هستن): +2 لول = +200 پوینت
        points_gained = 2 * 100
        money_reward = 100 + b["island_level"]
        cursor.execute(
            "UPDATE players SET level=level+2, points=points+?, money=money+?, hp=? WHERE user_id=?",
            (points_gained, money_reward, final_hp, user.id)
        )
        cursor.execute(
            "INSERT INTO boss_cooldowns (user_id, boss_id, defeated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id, boss_id) DO UPDATE SET defeated_at=excluded.defeated_at",
            (user.id, boss_id, time.time())
        )
        lines.append(f"\n🏆 {b['display']} رو کشتی! +2 لول 🎯 +{points_gained} پوینت 💰 +{money_reward}")
        lines.append("⏳ این باس ۵ دقیقه کول‌داونه.")

        if random.random() < RARE_DROP_CHANCE:
            rarity = get_rarity_multiplier(boss_id)
            bonus_attack = int(5 * rarity)
            item_name = get_drop_item_name(boss_id)
            cursor.execute(
                "INSERT INTO inventory (user_id, item_name, item_type, quantity) VALUES (?, ?, 'boss_relic', 1) "
                "ON CONFLICT(user_id, item_name) DO UPDATE SET quantity=quantity+1",
                (user.id, item_name)
            )
            cursor.execute(
                "UPDATE players SET extra_attack = extra_attack + ? WHERE user_id=?",
                (bonus_attack, user.id)
            )
            lines.append(f"\n💎 دراپ نادر! {item_name} گرفتی (Attack دائمی +{bonus_attack})!")
    else:
        cursor.execute("UPDATE players SET hp=? WHERE user_id=?", (final_hp, user.id))
        lines.append(f"\n💀 {b['display']} پیروز شد! HP ـت ریست شد. (کول‌داون نداره، دوباره امتحان کن)")

    db.commit()
    await query.edit_message_text("\n".join(lines))
