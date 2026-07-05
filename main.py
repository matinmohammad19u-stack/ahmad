from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from database import db, cursor

from characters import characters
from skill import SKILL_DB
from skill_system import get_available_skills, add_mastery
from shop import buy_item, SHOP_ITEMS, get_money
from inventory import get_inventory, add_item
from awakening import check_awakening
from form_system import change_form, get_switchable_forms, has_form_choice, get_forms_with_requirements
from ship_system import ships
from swords_shop import SWORDS_SHOP
from daily import claim_daily
from islands import islands
from raid_handler import raid, raid_callback, raid_attack_callback
from fight import create_battle, apply_action, get_actions
from compute_damage import compute_damage
from points_system import get_points, spend_points, POINT_UPGRADES, POINTS_PER_LEVEL
from passive_system import apply_passive, describe_passive
from island_boss_handler import (
    island_boss_cmd, island_boss_pick_callback, island_boss_attack_callback
)

import os
import random
import datetime

# =========================
# TOKEN SAFETY FIX
# =========================
TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise ValueError("❌ TOKEN is not set! Please set it in Railway Variables.")

# =========================
# آنلاین یوزرها
# =========================
online_users = {}

# =========================
# فایت‌های فعال (Button Battle)
# هر فایت یه battle_id داره. active_battles نگه‌دارنده‌ی کامل state
# (از fight.py) + متادیتای تلگرام (آیدی/چت دو طرف). user_in_battle
# برای جلوگیری از اینه که یه نفر همزمان توی دو فایت باشه.
# =========================
active_battles = {}
user_in_battle = {}
_battle_id_counter = {"n": 0}


def _new_battle_id():
    _battle_id_counter["n"] += 1
    return str(_battle_id_counter["n"])


def _skill_keyboard(battle_id, skills):
    buttons = []
    for idx, sk in enumerate(skills):
        # FIX: جاخالی و دفاع اسکیل حمله نیستن، دکمه‌ی جدا و متمایز می‌گیرن
        # (شمارنده‌ی تعداد باقیمونده‌ی هرکدوم توی اسم خودشون ست، مثلاً
        # "جاخالی (4/5)")
        a_type = sk.get("type", "attack")
        if a_type == "dodge":
            label = f"🌀 {sk['name']}"
        elif a_type == "defense":
            label = f"🛡 {sk['name']}"
        else:
            dmg_label = f"{sk['damage']} دمیج" if sk.get("damage") else "Utility"
            label = f"💥 {sk['name']} ({dmg_label})"
        buttons.append([
            InlineKeyboardButton(label, callback_data=f"atk_{battle_id}_{idx}")
        ])
    return InlineKeyboardMarkup(buttons)


def _hp_line(state):
    f1 = state["fighters"]["p1"]
    f2 = state["fighters"]["p2"]
    return f"❤️ {f1['name']}: {f1['hp']}/{f1['max_hp']} | {f2['name']}: {f2['hp']}/{f2['max_hp']}"


def _cleanup_battle(battle_id):
    battle = active_battles.pop(battle_id, None)
    if battle:
        user_in_battle.pop(battle["p1_id"], None)
        user_in_battle.pop(battle["p2_id"], None)

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.effective_message

    username = user.username or "no_username"

    cursor.execute(
        "INSERT OR IGNORE INTO players (user_id, username) VALUES (?, ?)",
        (user.id, username)
    )
    db.commit()

    online_users[user.id] = user.first_name

    if not msg:
        return

    await msg.reply_text(
        "🏴‍☠️ به One Piece RPG خوش اومدی!\n\n"
        "📋 دستورات اصلی:\n"
        "/character_select - انتخاب شخصیت\n"
        "/character - مشاهده شخصیت\n"
        "/stats - آمار کامل\n"
        "/profile - پروفایل\n"
        "/fight - مبارزه با بازیکن\n"
        "/boss - مبارزه با باس\n"
        "/skills - مهارت‌ها\n"
        "/mastery - مستری\n"
        "/awaken - فعال‌سازی Awakening\n"
        "/form - انتخاب فرم (با دکمه)\n"
        "/points - خرج کردن پوینت (Attack/Defense/Speed/HP)\n"
        "/shop - فروشگاه آیتم\n"
        "/sword_shop - فروشگاه شمشیر\n"
        "/ship_shop - فروشگاه کشتی\n"
        "/buy [نام] - خرید\n"
        "/inventory - کیف\n"
        "/equip [نام] - تجهیز\n"
        "/ship - کشتی فعلی\n"
        "/island - جزیره فعلی\n"
        "/island_boss - فایت دکمه‌ای با باس‌های جزیره‌ی فعلی\n"
        "/travel [نام] - سفر\n"
        "/upgrade - ارتقا\n"
        "/daily - جایزه روزانه\n"
        "/rank - رتبه‌بندی\n"
        "/raid - فایت با Raid Boss (دکمه‌ای، مثل PVP)\n"
        "/help - راهنما"
    )

# =========================
# CHARACTER SELECT
# =========================
async def character_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("SELECT character FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if row and row[0]:
        await update.message.reply_text(f"✅ تو قبلاً شخصیت {row[0]} رو گرفتی!")
        return
    cursor.execute("SELECT name FROM available_characters")
    available = [r[0] for r in cursor.fetchall()]
    if not available:
        await update.message.reply_text("❌ همه شخصیت‌ها گرفته شدن!")
        return
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"pick_{name}")]
        for name in available
    ]
    await update.message.reply_text(
        "🎭 یه شخصیت انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def pick_character_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    cursor.execute("SELECT character FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if row and row[0]:
        await query.edit_message_text(f"✅ تو قبلاً شخصیت {row[0]} رو گرفتی!")
        return
    chosen_name = query.data.replace("pick_", "")
    cursor.execute("SELECT name FROM available_characters WHERE name=?", (chosen_name,))
    if not cursor.fetchone():
        await query.edit_message_text("❌ این شخصیت گرفته شده! دوباره /character_select بزن.")
        return
    chosen = characters[chosen_name]
    hp = chosen["stats"]["hp"]
    cursor.execute(
        "INSERT OR IGNORE INTO players (user_id, username) VALUES (?, ?)",
        (user.id, user.username or "no_username")
    )
    cursor.execute(
        "UPDATE players SET character=?, hp=?, max_hp=? WHERE user_id=?",
        (chosen_name, hp, hp, user.id)
    )
    cursor.execute("DELETE FROM available_characters WHERE name=?", (chosen_name,))
    db.commit()
    await query.edit_message_text(
        f"🎉 تبریک {user.first_name}!\n\n"
        f"🎭 شخصیت: {chosen_name}\n"
        f"❤️ HP: {hp}\n"
        f"⚔️ Attack: {chosen['stats']['attack']}\n"
        f"🛡️ Defense: {chosen['stats']['defense']}\n"
        f"💨 Speed: {chosen['stats']['speed']}"
    )

# =========================
# CHARACTER - FIX: این تابع وجود نداشت ولی handler ثبت شده بود!
# =========================
async def character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("""
        SELECT character, hp, max_hp, current_form, awakening,
               equipped_weapon, extra_attack, extra_defense, extra_speed, level
        FROM players WHERE user_id=?
    """, (user.id,))
    data = cursor.fetchone()
    if not data or not data[0]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    char_name, hp, max_hp, form, awakening, weapon, ex_atk, ex_def, ex_spd, level = data
    char_stats = characters[char_name]["stats"]
    forms_with_req = get_forms_with_requirements(char_name)

    total_atk = char_stats["attack"] + ex_atk
    total_def = char_stats["defense"] + ex_def
    total_spd = char_stats["speed"] + ex_spd

    if weapon and weapon in SWORDS_SHOP:
        sword_bonus = SWORDS_SHOP[weapon]["attack"]
        sword_bonus = int(sword_bonus * 1.5) if char_name == "Roronoa Zoro" else sword_bonus
        total_atk += sword_bonus

    if len(forms_with_req) >= 2:
        lines = []
        for f, required in forms_with_req:
            if level >= required:
                lines.append(f"  ✅ {f}" + (f" (Lv{required})" if required else ""))
            else:
                lines.append(f"  🔒 {f} (Lv{required})")
        forms_line = "\n".join(lines)
    else:
        forms_line = "  فرم قابل‌تغییری نداره"

    await update.message.reply_text(
        f"🎭 شخصیت: {char_name}\n"
        f"⚡ فرم فعلی: {form or 'Base'}\n"
        f"🌀 Awakening: {'🔥 Yes' if awakening else '❌ No'}\n"
        f"{describe_passive(char_name)}\n"
        f"❤️ HP: {hp}/{max_hp}\n"
        f"⚔️ Attack: {total_atk}\n"
        f"🛡️ Defense: {total_def}\n"
        f"💨 Speed: {total_spd}\n"
        f"🗡️ سلاح: {weapon or 'ندارم'}\n\n"
        f"🔄 فرم‌های موجود (با /form تغییرشون بده):\n" +
        forms_line
    )
# =========================
# STATS
# =========================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("""
        SELECT level, xp, money, points, character, hp, max_hp,
               equipped_weapon, current_ship,
               extra_attack, extra_defense, extra_speed
        FROM players WHERE user_id=?
    """, (user.id,))
    data = cursor.fetchone()
    if not data or not data[4]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    level, xp, money, points, char_name, hp, max_hp, weapon, ship, ex_atk, ex_def, ex_spd = data
    char_stats = characters[char_name]["stats"]
    # FIX: extra stats اضافه شد
    total_atk = char_stats["attack"] + ex_atk
    total_def = char_stats["defense"] + ex_def
    total_spd = char_stats["speed"] + ex_spd

    if weapon and weapon in SWORDS_SHOP:
        sword_bonus = SWORDS_SHOP[weapon]["attack"]
        sword_bonus = int(sword_bonus * 1.5) if char_name == "Roronoa Zoro" else sword_bonus
        total_atk += sword_bonus

    await update.message.reply_text(
        f"📊 آمار {char_name}\n\n"
        f"⭐ لول: {level}\n"
        f"💰 پول: {money}\n"
        f"🎯 پوینت: {points} (با /points خرجش کن)\n"
        f"❤️ HP: {hp}/{max_hp}\n"
        f"⚔️ Attack: {total_atk}\n"
        f"🛡️ Defense: {total_def}\n"
        f"💨 Speed: {total_spd}\n"
        f"🗡️ سلاح: {weapon or 'ندارم'}\n"
        f"⛵ کشتی: {ship or 'ندارم'}"
        )

# =========================
# PROFILE
# =========================
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("""
        SELECT level, xp, money, character, hp, max_hp, equipped_weapon,
               current_ship, awakening, current_form
        FROM players WHERE user_id=?
    """, (user.id,))
    data = cursor.fetchone()
    if not data or not data[3]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    level, xp, money, char_name, hp, max_hp, weapon, ship, awakening, form = data
    cursor.execute("SELECT COUNT(*) FROM fight_history WHERE user_id=? AND result='WIN'", (user.id,))
    wins = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM fight_history WHERE user_id=? AND result='LOSE'", (user.id,))
    losses = cursor.fetchone()[0]
    await update.message.reply_text(
        f"👤 پروفایل {user.first_name}\n\n"
        f"🎭 شخصیت: {char_name}\n"
        f"⚡ فرم: {form or 'Base'}\n"
        f"🌀 Awakening: {'🔥 Yes' if awakening else '❌ No'}\n"
        f"⭐ لول: {level}\n"
        f"💰 پول: {money}\n"
        f"❤️ HP: {hp}/{max_hp}\n"
        f"🗡️ سلاح: {weapon or 'ندارم'}\n"
        f"⛵ کشتی: {ship or 'ندارم'}\n\n"
        f"🏆 بردها: {wins}\n"
        f"💀 باختا: {losses}"
)
    # =========================
# FIGHT (PVP آنلاین) — Button Battle
# تغییر اصلی: قبلاً فایت یه‌جا اتوماتیک شبیه‌سازی می‌شد (اسکیل‌های رندوم
# برای هر دو طرف) و فقط یه لاگ متنی نشون داده می‌شد؛ پلیر هیچ نقشی توی
# نتیجه نداشت. الان فایت نوبتی شده: هر کی نوبتشه یه پیام با دکمه‌ی
# اسکیل‌هاش می‌گیره، خودش انتخاب می‌کنه، و نتیجه برای هر دو طرف فرستاده
# می‌شه تا نوبت بعدی برسه.
# =========================
async def fight_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("SELECT character, hp FROM players WHERE user_id=?", (user.id,))
    data = cursor.fetchone()
    if not data or not data[0]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    if data[1] <= 0:
        await update.message.reply_text("❌ HP نداری! از /daily استفاده کن.")
        return
    # FIX: اگه خودت وسط یه فایت دیگه‌ای، نباید بتونی همزمان یه فایت جدید شروع کنی
    if user.id in user_in_battle:
        await update.message.reply_text("❌ تو همین الان وسط یه مبارزه‌ای! اول اون رو تموم کن.")
        return
    # FIX: کسایی که خودشون وسط یه فایت دیگه‌ان از لیست حریف‌های قابل‌انتخاب حذف می‌شن
    enemies = {
        uid: name for uid, name in online_users.items()
        if uid != user.id and uid not in user_in_battle
    }
    if not enemies:
        await update.message.reply_text("❌ بازیکن آنلاین و آزاد دیگه‌ای نیست!")
        return
    keyboard = [
        [InlineKeyboardButton(f"⚔️ {name}", callback_data=f"fight_{uid}")]
        for uid, name in enemies.items()
    ]
    await update.message.reply_text("⚔️ با کی میخوای بجنگی؟", reply_markup=InlineKeyboardMarkup(keyboard))


async def fight_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب حریف → ساخت مبارزه و فرستادن دکمه‌ی اولین نوبت."""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    enemy_id = int(query.data.replace("fight_", ""))

    if enemy_id == user.id:
        await query.edit_message_text("❌ نمی‌تونی با خودت بجنگی!")
        return
    if user.id in user_in_battle:
        await query.edit_message_text("❌ تو همین الان وسط یه مبارزه‌ای!")
        return
    if enemy_id in user_in_battle:
        await query.edit_message_text("❌ این بازیکن الان وسط یه مبارزه‌ی دیگه‌ست.")
        return

    cursor.execute(
        "SELECT character, hp, extra_attack, extra_defense, extra_speed, equipped_weapon, current_form FROM players WHERE user_id=?",
        (user.id,)
    )
    p1 = cursor.fetchone()
    cursor.execute(
        "SELECT character, hp, extra_attack, extra_defense, extra_speed, equipped_weapon, current_form FROM players WHERE user_id=?",
        (enemy_id,)
    )
    p2 = cursor.fetchone()

    if not p1 or not p1[0] or not p2 or not p2[0]:
        await query.edit_message_text("❌ یکی از بازیکنا شخصیت ندارن!")
        return
    if p1[1] <= 0:
        await query.edit_message_text("❌ HP نداری! از /daily استفاده کن.")
        return
    if p2[1] <= 0:
        await query.edit_message_text("❌ این بازیکن الان HP نداره، یکی دیگه رو امتحان کن.")
        return

    p1_data = {"name": p1[0], "stats": characters[p1[0]]["stats"].copy()}
    p2_data = {"name": p2[0], "stats": characters[p2[0]]["stats"].copy()}
    # FIX: HP و extra stats (از /upgrade_*) اعمال می‌شن
    p1_data["stats"]["hp"] = p1[1]
    p1_data["stats"]["attack"] += p1[2]
    p1_data["stats"]["defense"] += p1[3]
    p1_data["stats"]["speed"] += p1[4]
    p2_data["stats"]["hp"] = p2[1]
    p2_data["stats"]["attack"] += p2[2]
    p2_data["stats"]["defense"] += p2[3]
    p2_data["stats"]["speed"] += p2[4]

    # سلاح تجهیزشده توی محاسبه‌ی دمیج اعمال می‌شه
    if p1[5] and p1[5] in SWORDS_SHOP:
        bonus = SWORDS_SHOP[p1[5]]["attack"]
        bonus = int(bonus * 1.5) if p1[0] == "Roronoa Zoro" else bonus
        p1_data["stats"]["attack"] += bonus
    if p2[5] and p2[5] in SWORDS_SHOP:
        bonus = SWORDS_SHOP[p2[5]]["attack"]
        bonus = int(bonus * 1.5) if p2[0] == "Roronoa Zoro" else bonus
        p2_data["stats"]["attack"] += bonus

    p1_form = p1[6] or "Base"
    p2_form = p2[6] or "Base"

    # پسیو هر شخصیت (باف خودکار و همیشگی، بدون دمیج) اینجا اعمال می‌شه
    p1_data["stats"] = apply_passive(p1[0], p1_data["stats"])
    p2_data["stats"] = apply_passive(p2[0], p2_data["stats"])

    state = create_battle(p1_data, p2_data, SKILL_DB, p1_form, p2_form)
    battle_id = _new_battle_id()
    battle = {
        "state": state,
        "p1_id": user.id,
        "p2_id": enemy_id,
        "p1_char": p1[0],
        "p2_char": p2[0],
        "p1_chat_id": query.message.chat_id,
        "p2_chat_id": enemy_id,  # توی چت خصوصی، chat_id همون user_id ـه
    }

    intro = "\n".join(state["log"])
    turn_side = state["turn"]
    turn_user_name = p1[0] if turn_side == "p1" else p2[0]

    try:
        if turn_side == "p1":
            await query.edit_message_text(
                f"{intro}\n\n🎯 نوبت توعه! یه اسکیل انتخاب کن:",
                reply_markup=_skill_keyboard(battle_id, get_actions(state, "p1"))
            )
            await context.bot.send_message(
                chat_id=battle["p2_chat_id"],
                text=f"{intro}\n\n⏳ {turn_user_name} داره فکر می‌کنه... صبر کن نوبتت بشه."
            )
        else:
            await context.bot.send_message(
                chat_id=battle["p2_chat_id"],
                text=f"{intro}\n\n🎯 نوبت توعه! یه اسکیل انتخاب کن:",
                reply_markup=_skill_keyboard(battle_id, get_actions(state, "p2"))
            )
            await query.edit_message_text(
                f"{intro}\n\n⏳ {turn_user_name} سریع‌تر بود و اول حمله می‌کنه. صبر کن..."
            )
    except Exception:
        # FIX: اگه نشه به طرف مقابل پیام داد (مثلاً بات رو بلاک کرده)، مبارزه
        # اصلاً ثبت نمی‌شه و کسی توی state گیر نمی‌کنه
        await query.edit_message_text("❌ نشد به حریف پیام بدم (شاید بات رو بلاک کرده). مبارزه لغو شد.")
        return

    active_battles[battle_id] = battle
    user_in_battle[user.id] = battle_id
    user_in_battle[enemy_id] = battle_id


async def fight_attack_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وقتی یکی از طرفین روی دکمه‌ی یه اسکیل می‌زنه."""
    query = update.callback_query
    user = query.from_user

    parts = query.data.split("_")
    if len(parts) != 3:
        await query.answer("❌ دکمه نامعتبره.", show_alert=True)
        return
    _, battle_id, skill_idx_str = parts
    try:
        skill_idx = int(skill_idx_str)
    except ValueError:
        await query.answer("❌ دکمه نامعتبره.", show_alert=True)
        return

    battle = active_battles.get(battle_id)
    if not battle:
        await query.answer("⚠️ این مبارزه دیگه فعال نیست.", show_alert=True)
        try:
            await query.edit_message_text("⚠️ این مبارزه قبلاً تموم شده یا منقضی شده.")
        except Exception:
            pass
        return

    if user.id == battle["p1_id"]:
        side = "p1"
    elif user.id == battle["p2_id"]:
        side = "p2"
    else:
        await query.answer("❌ این مبارزه‌ی تو نیست!", show_alert=True)
        return

    state = battle["state"]

    if state["finished"]:
        await query.answer("⚠️ این مبارزه تموم شده.", show_alert=True)
        return

    if state["turn"] != side:
        await query.answer("⏳ نوبت تو نیست! صبر کن طرف مقابل حمله کنه.", show_alert=True)
        return

    await query.answer()

    try:
        result = apply_action(state, side, skill_idx)
    except ValueError:
        await query.answer("❌ این حرکت دیگه معتبر نیست.", show_alert=True)
        return

    other_side = "p2" if side == "p1" else "p1"
    other_chat_id = battle["p2_chat_id"] if side == "p1" else battle["p1_chat_id"]

    attacker_name = state["fighters"][side]["name"]
    defender_name = state["fighters"][other_side]["name"]

    # FIX: جاخالی/دفاع دیگه به شکل «حمله‌ای با ۰ دمیج» نشون داده نمی‌شن؛
    # یه پیام مخصوص خودشون دارن. همینطور وقتی حمله‌ی طرف مقابل با
    # جاخالی/دفاعِ قبلیِ حریف خنثی یا کم‌اثر شده، اون هم توی پیام مشخصه.
    action_type = result.get("action_type", "attack")
    mitigated = result.get("mitigated")

    if action_type == "dodge":
        line = f"🌀 {attacker_name} جاخالی داد! ضربه‌ی بعدی {defender_name} روش اثر نمی‌کنه."
    elif action_type == "defense":
        line = f"🛡 {attacker_name} دفاع گرفت! ضربه‌ی بعدی {defender_name} کم‌اثرتر می‌شه."
    else:
        crit_text = " 💥 CRIT!" if result["crit"] and result["damage"] > 0 else ""
        if mitigated == "dodge":
            line = f"⚔️ {attacker_name} از {result['skill_name']} استفاده کرد، ولی {defender_name} جاخالی داد و کامل رد کرد! (۰ دمیج)"
        elif mitigated == "defense_full":
            line = f"⚔️ {attacker_name} از {result['skill_name']} استفاده کرد، ولی {defender_name} با دفاع کامل خنثی‌ش کرد! (۰ دمیج)"
        elif mitigated == "defense_half":
            line = f"⚔️ {attacker_name} از {result['skill_name']} استفاده کرد → {defender_name} با دفاع نصف دمیج رو کم کرد → {result['damage']} دمیج{crit_text}"
        elif mitigated == "defense_quarter":
            line = f"⚔️ {attacker_name} از {result['skill_name']} استفاده کرد → {defender_name} با دفاع دمیج رو یک‌چهارم کرد → {result['damage']} دمیج{crit_text}"
        else:
            line = f"⚔️ {attacker_name} از {result['skill_name']} استفاده کرد → {result['damage']} دمیج{crit_text}"

    turn_summary = f"{line}\n{_hp_line(state)}"

    if not result["finished"]:
        # نوبت میره طرف مقابل
        if action_type == "dodge":
            actor_confirm = "✅ جاخالی دادی!"
        elif action_type == "defense":
            actor_confirm = "✅ دفاع گرفتی!"
        else:
            actor_confirm = "✅ تو زدی!"
        await query.edit_message_text(f"{actor_confirm}\n\n{turn_summary}\n\n⏳ منتظر نوبتت بمون...")
        next_side = state["turn"]
        try:
            await context.bot.send_message(
                chat_id=other_chat_id,
                text=f"{turn_summary}\n\n🎯 نوبت توعه! یه اسکیل انتخاب کن:",
                reply_markup=_skill_keyboard(battle_id, get_actions(state, next_side))
            )
        except Exception:
            # FIX: اگه نشه به نفر بعدی پیام داد، مبارزه‌ای که قراره گیر کنه رو
            # به جای ابدی موندن توی active_battles، می‌بندیم تا کسی قفل نشه
            _cleanup_battle(battle_id)
            await query.edit_message_text(
                f"✅ تو زدی!\n\n{turn_summary}\n\n⚠️ نشد به حریف پیام بدم، مبارزه متوقف شد."
            )
        return

    # ---------- مبارزه تموم شد ----------
    winner_side = result["winner"]
    loser_side = "p2" if winner_side == "p1" else "p1"
    winner_id = battle["p1_id"] if winner_side == "p1" else battle["p2_id"]
    loser_id = battle["p2_id"] if winner_side == "p1" else battle["p1_id"]
    winner_char = battle["p1_char"] if winner_side == "p1" else battle["p2_char"]
    loser_char = battle["p2_char"] if winner_side == "p1" else battle["p1_char"]
    earned_money = result["earned_money"]
    winner_hp = max(1, state["fighters"][winner_side]["hp"])

    # FIX: برنده +5 لول و جایزه می‌گیره، HP باقیمونده‌ش ثبت می‌شه؛
    # بازنده HP ـش ریست به max_hp می‌شه (مثل نسخه‌ی قبلی)
    # سیستم پوینت: هر لول = 100 پوینت → برد فایت (+5 لول) = +500 پوینت،
    # قابل خرج کردن با /points روی هر ترکیبی از دمیج/دفاع/سرعت/جون.
    LEVELS_PER_WIN = 5
    points_gained = LEVELS_PER_WIN * POINTS_PER_LEVEL
    cursor.execute(
        "UPDATE players SET level=level+?, points=points+?, money=money+?, hp=? WHERE user_id=?",
        (LEVELS_PER_WIN, points_gained, earned_money, winner_hp, winner_id)
    )
    cursor.execute("UPDATE players SET hp=max_hp WHERE user_id=?", (loser_id,))

    # FIX: قبلاً فقط برای کسی که /fight رو زده بود fight_history ثبت می‌شد و
    # برد/باخت حریف هیچوقت توی /profile اون یکی نفر دیده نمی‌شد. الان برای
    # هر دو طرف ثبت می‌شه.
    cursor.execute("""
        INSERT INTO fight_history (user_id, enemy, result, reward_xp, reward_money)
        VALUES (?, ?, ?, ?, ?)
    """, (winner_id, loser_char, "WIN", 0, earned_money))
    cursor.execute("""
        INSERT INTO fight_history (user_id, enemy, result, reward_xp, reward_money)
        VALUES (?, ?, ?, ?, ?)
    """, (loser_id, winner_char, "LOSE", 0, 0))

    # FIX: مستری اسکیل‌های هر دو طرف آپدیت می‌شه (قبلاً فقط طرف اول)
    for skill_name, count in state["fighters"]["p1"]["skills_used"].items():
        rate = 3 if winner_side == "p1" else 1
        add_mastery(battle["p1_id"], battle["p1_char"], skill_name, amount=rate * count)
    for skill_name, count in state["fighters"]["p2"]["skills_used"].items():
        rate = 3 if winner_side == "p2" else 1
        add_mastery(battle["p2_id"], battle["p2_char"], skill_name, amount=rate * count)

    db.commit()
    _cleanup_battle(battle_id)

    timeout_note = "⏱️ سقف راندها رسید! بر اساس HP باقیمونده برنده مشخص شد.\n\n" if result["timeout"] else ""

    def _outcome(viewer_side):
        if viewer_side == winner_side:
            return (
                f"🏆 تو بردی!\n💰 جایزه: +{earned_money} | ⭐ +{LEVELS_PER_WIN} لول | "
                f"🎯 +{points_gained} پوینت (با /points خرجش کن)"
            )
        return "💀 تو باختی! HP ـت ریست شد به ماکزیمم."

    actor_text = f"{timeout_note}{turn_summary}\n\n{_outcome(side)}"
    other_text = f"{timeout_note}{turn_summary}\n\n{_outcome(other_side)}"

    await query.edit_message_text(actor_text)
    try:
        await context.bot.send_message(chat_id=other_chat_id, text=other_text)
    except Exception:
        pass  # نتونستیم به حریف خبر بدیم؛ نتیجه توی دیتابیس قبلاً ثبت شده

# =========================
# BOSS
# =========================
async def boss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("""
        SELECT character, hp, level, current_form, form_multiplier,
               extra_attack, equipped_weapon
        FROM players WHERE user_id=?
    """, (user.id,))
    data = cursor.fetchone()
    if not data or not data[0]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    char_name, hp, level, form, form_multiplier, extra_attack, weapon = data
    if hp <= 0:
        await update.message.reply_text("❌ HP نداری! از /daily استفاده کن.")
        return

    current_form = form or "Base"
    form_multiplier = form_multiplier or 1.0

    # FIX: قبلاً boss فقط از player_attack خام استفاده می‌کرد، نه اسکیل‌های واقعی
    # شخصیت (یعنی /skills و /mastery هیچ معنایی نداشتن چون boss ازشون استفاده نمی‌کرد)
    skill_list = SKILL_DB.get(char_name, {}).get(current_form, [])
    if not skill_list:
        skill_list = [{"name": "Basic Attack", "damage": characters[char_name]["stats"]["attack"]}]

    # دقیقاً مثل /stats: attack پایه + ارتقا + بونوس شمشیر + پسیو
    total_attack = characters[char_name]["stats"]["attack"] + extra_attack
    if weapon and weapon in SWORDS_SHOP:
        sword_bonus = SWORDS_SHOP[weapon]["attack"]
        sword_bonus = int(sword_bonus * 1.5) if char_name == "Roronoa Zoro" else sword_bonus
        total_attack += sword_bonus
    passive = apply_passive(char_name, {"attack": total_attack})
    total_attack = passive["attack"]

    bosses = ["Kaido", "Big Mom", "Blackbeard", "Akainu", "Doflamingo"]
    boss_name = random.choice(bosses)
    boss_hp = 2000 + level * 200
    boss_defense = 20 + level * 2
    boss_attack = 100 + level * 10

    log = [f"👹 Boss Battle: {char_name} VS {boss_name}!", f"❤️ Boss HP: {boss_hp}", "━━━━━━━━━━━━━━━━━━━━━━"]
    turn = 1
    player_hp = hp
    skills_used = {}

    while player_hp > 0 and boss_hp > 0 and turn <= 100:
        skill = random.choice(skill_list)

        cursor.execute(
            "SELECT mastery FROM skill_mastery WHERE user_id=? AND character=? AND skill_name=?",
            (user.id, char_name, skill["name"])
        )
        mrow = cursor.fetchone()
        mastery_val = mrow[0] if mrow else 0

        # FIX: دمیج حالا واقعاً به damage اسکیل + mastery + فرم + Attack بستگی داره
        effective_base = skill["damage"] + int(total_attack * 0.3)
        dmg, crit = compute_damage(
            base_damage=effective_base,
            mastery=mastery_val,
            form_multiplier=form_multiplier,
            crit_chance=10,
            enemy_defense=boss_defense
        )
        boss_hp -= dmg
        skills_used[skill["name"]] = skills_used.get(skill["name"], 0) + 1

        crit_text = " 💥 CRIT!" if crit else ""
        log.append(f"Turn {turn}: {skill['name']} → {dmg} dmg{crit_text}")

        if boss_hp <= 0:
            break

        b_dmg = int(boss_attack * random.uniform(0.8, 1.3))
        player_hp -= b_dmg
        log.append(f"Turn {turn}: {boss_name} {b_dmg} زد به تو")
        turn += 1

    log.append("━━━━━━━━━━━━━━━━━━━━━━")

    # FIX: قبلاً فقط "player_hp > 0" چک می‌شد. با اضافه شدن سقف turn، این یعنی
    # حتی اگه boss هنوز نمرده بود هم به اشتباه "برد" حساب می‌شد. الان درست:
    if boss_hp <= 0:
        money_reward = 500 + level * 50
        boss_points_gained = 5 * POINTS_PER_LEVEL
        cursor.execute(
            "UPDATE players SET level=level+5, points=points+?, money=money+?, hp=? WHERE user_id=?",
            (boss_points_gained, money_reward, max(1, player_hp), user.id)
        )
        log.append(f"🏆 Boss کشتی! +5 لول 💰 +{money_reward} 🎯 +{boss_points_gained} پوینت")
        mastery_rate = 5
    elif player_hp <= 0:
        cursor.execute("UPDATE players SET hp=max_hp WHERE user_id=?", (user.id,))
        log.append("💀 باختی! HP ریست شد.")
        mastery_rate = 2
    else:
        cursor.execute("UPDATE players SET hp=? WHERE user_id=?", (max(1, player_hp), user.id))
        log.append("⏱️ Boss خیلی قویه! وقت تموم شد، دوباره امتحان کن.")
        mastery_rate = 2

    # FIX: مستری اسکیل‌های استفاده‌شده آپدیت می‌شه (قبلاً اصلاً این اتفاق نمی‌افتاد!)
    for skill_name, count in skills_used.items():
        add_mastery(user.id, char_name, skill_name, amount=mastery_rate * count)
    if boss_hp <= 0:
        log.append("📈 Mastery اسکیل‌هات بالا رفت! با /mastery چک کن.")

    db.commit()
    await update.message.reply_text("\n".join(log)[:4000])

# =========================
# SHOP
# =========================
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    text = "🏪 فروشگاه آیتم‌ها:\n\n"
    for name, item in SHOP_ITEMS.items():
        text += f"• {name}: {item['price']} 💰\n"
    text += "\nبرای خرید: /buy [نام آیتم]"
    await update.message.reply_text(text)

# =========================
# SWORD SHOP - FIX: قبلاً همه‌ی شمشیرها توی یه پیام تکست تنها ساخته می‌شدن.
# تلگرام سقف ۴۰۹۶ کاراکتر برای هر پیام داره؛ با اضافه شدن شمشیرهای زیاد،
# اون پیام رد می‌شد و ارسالش خطا می‌داد (کرش این دستور). الان فروشگاه
# شمشیر صفحه‌بندی (pagination) شده: هر صفحه فقط چندتا شمشیر نشون می‌ده و
# با دکمه‌های ⬅️/➡️ می‌شه بین صفحه‌ها رفت. این یعنی فرقی نمی‌کنه چندتا
# شمشیر توی SWORDS_SHOP باشه (۱۰تا یا ۱۰۰۰تا)، هیچ‌وقت این دستور کرش
# نمی‌کنه.
# =========================
SWORDS_PER_PAGE = 8


def _sword_shop_total_pages() -> int:
    return max(1, (len(SWORDS_SHOP) + SWORDS_PER_PAGE - 1) // SWORDS_PER_PAGE)


def _sword_shop_page_text(page: int) -> str:
    names = list(SWORDS_SHOP.keys())
    total_pages = _sword_shop_total_pages()
    page = max(0, min(page, total_pages - 1))
    start = page * SWORDS_PER_PAGE
    chunk = names[start:start + SWORDS_PER_PAGE]

    text = f"⚔️ فروشگاه شمشیر (صفحه {page + 1}/{total_pages} | مجموع {len(SWORDS_SHOP)} شمشیر)\n\n"
    for name in chunk:
        sword = SWORDS_SHOP[name]
        text += f"🗡️ {name}\n   ATK: +{sword['attack']} | {sword['price']} 💰\n   {sword.get('description', '')}\n\n"
    text += "برای خرید: /buy [نام شمشیر]"
    return text


def _sword_shop_keyboard(page: int) -> InlineKeyboardMarkup:
    total_pages = _sword_shop_total_pages()
    page = max(0, min(page, total_pages - 1))
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ قبلی", callback_data=f"swdpg_{page - 1}"))
    nav_row.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="swdpg_noop"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("بعدی ➡️", callback_data=f"swdpg_{page + 1}"))
    return InlineKeyboardMarkup([nav_row])


async def sword_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    await update.message.reply_text(
        _sword_shop_page_text(0),
        reply_markup=_sword_shop_keyboard(0)
    )


async def sword_shop_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دکمه‌های ⬅️ قبلی / بعدی ➡️ صفحه‌بندی فروشگاه شمشیر."""
    query = update.callback_query
    await query.answer()
    if query.data == "swdpg_noop":
        return  # دکمه‌ی شماره صفحه، فقط نمایشیه و کاری نمی‌کنه
    try:
        page = int(query.data.replace("swdpg_", ""))
    except ValueError:
        return
    await query.edit_message_text(
        _sword_shop_page_text(page),
        reply_markup=_sword_shop_keyboard(page)
    )

# =========================
# SHIP SHOP
# =========================
async def ship_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    text = "⛵ فروشگاه کشتی:\n\n"
    for name, item in ships.items():
        text += (
            f"🚢 {name}\n"
            f"   Lv{item['required_level']} | {item['price']} 💰\n"
            f"   Speed:{item['speed']} Durability:{item['durability']} Cargo:{item['cargo']}\n"
            f"   {item['description']}\n\n"
        )
    text += "برای خرید: /buy [نام کشتی]"
    await update.message.reply_text(text)

# =========================
# BUY
# =========================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    if not context.args:
        await update.message.reply_text("❌ بنویس: /buy [نام آیتم]")
        return
    item_name = " ".join(context.args)

    if item_name in SHOP_ITEMS:
        result = buy_item(user.id, item_name)
    elif item_name in SWORDS_SHOP:
        sword = SWORDS_SHOP[item_name]
        money = get_money(user.id)
        if money < sword["price"]:
            result = "❌ پول کافی نداری"
        else:
            cursor.execute(
                "UPDATE players SET money=money-? WHERE user_id=?",
                (sword["price"], user.id)
            )
            add_item(user.id, item_name, "sword")
            db.commit()
            result = f"✅ {item_name} خریداری شد! ⚔️ ATK+{sword['attack']}"
    elif item_name in ships:
        ship = ships[item_name]
        cursor.execute("SELECT level FROM players WHERE user_id=?", (user.id,))
        row = cursor.fetchone()
        if not row:
            result = "❌ پلیر پیدا نشد"
        elif row[0] < ship["required_level"]:
            result = f"❌ نیاز به لول {ship['required_level']} داری"
        else:
            money = get_money(user.id)
            if money < ship["price"]:
                result = "❌ پول کافی نداری"
            else:
                cursor.execute(
                    "UPDATE players SET money=money-?, current_ship=? WHERE user_id=?",
                    (ship["price"], item_name, user.id)
                )
                db.commit()
                result = f"⛵ {item_name} خریداری شد!"
    else:
        result = "❌ این آیتم وجود نداره"

    await update.message.reply_text(result)

# =========================
# INVENTORY
# =========================
async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    await update.message.reply_text(get_inventory(user.id))

# =========================
# EQUIP
# =========================
async def equip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    if not context.args:
        await update.message.reply_text("❌ بنویس: /equip [نام شمشیر]")
        return
    item_name = " ".join(context.args)
    cursor.execute(
        "SELECT quantity FROM inventory WHERE user_id=? AND item_name=?",
        (user.id, item_name)
    )
    row = cursor.fetchone()
    if not row:
        await update.message.reply_text("❌ این آیتم توی کیفت نیست!")
        return
    cursor.execute("SELECT character FROM players WHERE user_id=?", (user.id,))
    char_row = cursor.fetchone()
    char_name = char_row[0] if char_row else None

    if item_name in SWORDS_SHOP:
        sword_attack = SWORDS_SHOP[item_name]["attack"]
        bonus = int(sword_attack * 1.5) if char_name == "Roronoa Zoro" else sword_attack
        cursor.execute(
            "UPDATE players SET equipped_weapon=? WHERE user_id=?",
            (item_name, user.id)
        )
        db.commit()
        zoro_note = " (⚡ Zoro Bonus x1.5!)" if char_name == "Roronoa Zoro" else ""
        await update.message.reply_text(f"✅ {item_name} تجهیز شد! ATK+{bonus}{zoro_note}")
    else:
        await update.message.reply_text("❌ این آیتم قابل تجهیز نیست!")

# =========================
# SKILLS
# =========================
async def skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("SELECT character, current_form FROM players WHERE user_id=?", (user.id,))
    data = cursor.fetchone()
    if not data or not data[0]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    char_name, form = data
    current_form = form or "Base"
    # FIX: SKILLS_DB → SKILL_DB
    skill_list = get_available_skills(user.id, char_name, SKILL_DB, current_form)
    if not skill_list:
        await update.message.reply_text(f"❌ اسکیلی برای فرم {current_form} پیدا نشد.")
        return
    text = f"⚡ اسکیل‌های {char_name} ({current_form}):\n\n"
    for sk in skill_list:
        locked = "🔒" if not sk["unlocked"] else "✅"
        text += f"{locked} {sk['name']} | DMG: {sk['damage']} | Mastery: {sk['mastery']}/100\n"
    text += "\nبرای دیدن فرم‌های دیگه: /form"
    await update.message.reply_text(text)

# =========================
# MASTERY
# =========================
async def mastery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("SELECT character FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row or not row[0]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    char_name = row[0]
    cursor.execute("""
        SELECT skill_name, mastery, unlocked FROM skill_mastery
        WHERE user_id=? AND character=?
    """, (user.id, char_name))
    rows = cursor.fetchall()
    if not rows:
        await update.message.reply_text("❌ هنوز مستری نداری! اول /fight یا /boss بزن.")
        return
    text = f"🎯 Mastery {char_name}:\n\n"
    for skill_name, mast, unlocked in rows:
        bar = "█" * (mast // 10) + "░" * (10 - mast // 10)
        status = "✅" if unlocked else "🔒"
        text += f"{status} {skill_name}\n[{bar}] {mast}/100\n\n"
    await update.message.reply_text(text)

# =========================
# AWAKEN - FIX: سیستم awakening.py از اول تعریف شده بود ولی هیچ
# دستوری توی main.py براش وجود نداشت، یعنی هیچوقت قابل دسترس نبود!
# =========================
async def awaken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("SELECT character, awakening FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row or not row[0]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    char_name, already = row
    if already:
        await update.message.reply_text(f"🔥 {char_name} از قبل Awakening شده!")
        return
    cursor.execute(
        "SELECT MAX(mastery) FROM skill_mastery WHERE user_id=? AND character=?",
        (user.id, char_name)
    )
    result = cursor.fetchone()
    max_mastery = result[0] if result and result[0] else 0
    msg = check_awakening(user.id, max_mastery)
    await update.message.reply_text(f"{msg}\n\n📊 بیشترین Mastery فعلی: {max_mastery}/100")

# =========================
# FORM - بازنویسی کامل: قبلاً با تایپ کردن اسم فرم کار می‌کرد (/form Gear 2)
# که هم دست‌وپاگیر بود هم اجازه می‌داد فرم‌های Awakening/Awakened رو بدون
# باز کردن Awakening واقعی ست کنی. الان فقط با دکمه کار می‌کنه و فرم‌های
# Awakening اصلاً توی لیست نیستن (اونا فقط از طریق /awaken باز می‌شن).
# فقط شخصیت‌هایی که واقعاً چند حالت دارن (مثل Luffy: Gear 2/4/5، Zoro:
# Asura/King of Hell) دکمه‌ی انتخاب فرم می‌گیرن.
#
# + لول‌گیت: فرم اول همیشه از لول ۰ آزاده؛ از فرم دوم به بعد هر فرم ۱۰۰
# لول بیشتر از قبلی می‌خواد (فرم۲=۲۰۰, فرم۳=۳۰۰, فرم۴=۴۰۰, ...). فرم‌هایی
# که لولش نرسیده با 🔒 و لولِ لازم نشون داده می‌شن؛ زدن دکمه‌شون هم قفله.
# =========================
async def form_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("SELECT character, current_form, level FROM players WHERE user_id=?", (user.id,))
    data = cursor.fetchone()
    if not data or not data[0]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    char_name, form, level = data
    current_form = form or "Base"
    forms_with_req = get_forms_with_requirements(char_name)

    if len(forms_with_req) < 2:
        await update.message.reply_text(
            f"⚡ فرم فعلی: {current_form}\n\n"
            f"🎭 {char_name} فرم قابل‌تغییری نداره."
        )
        return

    keyboard = []
    lines = [f"⚡ فرم فعلی: {current_form}  |  ⭐ لول: {level}\n", "🔄 کدوم فرم رو میخوای بگیری؟"]
    for f, required in forms_with_req:
        unlocked = level >= required
        mark = "✅ " if f == current_form else ""
        if unlocked:
            label = f"{mark}{f}" + (f" (Lv{required})" if required else "")
            keyboard.append([InlineKeyboardButton(label, callback_data=f"frm_{f}")])
        else:
            keyboard.append([InlineKeyboardButton(f"🔒 {f} (Lv{required})", callback_data="frm_locked")])
            lines.append(f"🔒 {f} — نیاز به لول {required} (الان {level})")

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def form_pick_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دکمه‌ی انتخاب فرم توی /form زده شد."""
    query = update.callback_query
    user = query.from_user
    if query.data == "frm_locked":
        await query.answer("🔒 لولت هنوز به این فرم نرسیده!", show_alert=True)
        return
    form_name = query.data[len("frm_"):]
    result = change_form(user.id, form_name)
    await query.answer()
    await query.edit_message_text(result)

# =========================
# SHIP
# =========================
async def ship(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("SELECT current_ship FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row or not row[0]:
        await update.message.reply_text("❌ کشتی نداری! از /ship_shop بخر.")
        return
    ship_name = row[0]
    ship_data = ships.get(ship_name, {})
    await update.message.reply_text(
        f"⛵ کشتی فعلی: {ship_name}\n\n"
        f"💨 Speed: {ship_data.get('speed', '?')}\n"
        f"🛡️ Durability: {ship_data.get('durability', '?')}\n"
        f"📦 Cargo: {ship_data.get('cargo', '?')}\n"
        f"📝 {ship_data.get('description', '')}"
)

# =========================
# ISLAND
# =========================
async def island(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("SELECT level, current_island FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row:
        await update.message.reply_text("❌ اول /start بزن.")
        return
    level, current_island = row
    # FIX: قبلاً current_island هیچ‌جا ذخیره نمی‌شد و هر بار از رو لول
    # حساب می‌شد (یعنی /travel هیچ اثر واقعی‌ای نداشت). الان از ستون
    # واقعی current_island خونده می‌شه.
    if not current_island or current_island not in islands:
        current_island = "East Blue"
    if current_island == "East Blue":
        # برای کاربرهای قدیمی: قبلاً current_island ذخیره نمی‌شد و هر بار از
        # رو لول حساب می‌شد. اینجا یه‌بار همون منطق رو اجرا و ذخیره می‌کنیم
        # تا پیشرفت قبلیشون از دست نره.
        candidates = [n for n, d in islands.items() if level >= d["required_level"]]
        if candidates:
            best = max(candidates, key=lambda n: islands[n]["required_level"])
            if best != "East Blue":
                current_island = best
                cursor.execute("UPDATE players SET current_island=? WHERE user_id=?", (current_island, user.id))
                db.commit()
    island_data = islands[current_island]
    text = f"🗺️ جزیره فعلی: {current_island}\n"
    text += f"⭐ لول مورد نیاز: {island_data['required_level']}\n\n📍 پارت‌ها:\n"
    for num, part in island_data["parts"].items():
        text += f"  Part {num}: {part['name']}\n  👹 Boss: {', '.join(part['bosses'])}\n\n"
    text += "برای فایت با باس‌های این جزیره: /island_boss"
    await update.message.reply_text(text)

# =========================
# TRAVEL
# =========================
async def travel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    if not context.args:
        text = "🗺️ جزیره‌های موجود:\n\n"
        for name, data in islands.items():
            text += f"• {name} (Lv{data['required_level']})\n"
        text += "\nبرای سفر: /travel [نام جزیره]"
        await update.message.reply_text(text)
        return
    dest = " ".join(context.args)
    if dest not in islands:
        await update.message.reply_text("❌ این جزیره وجود نداره!")
        return
    cursor.execute("SELECT level, current_ship FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row:
        await update.message.reply_text("❌ اول /start بزن.")
        return
    level, current_ship = row
    island_data = islands[dest]
    if level < island_data["required_level"]:
        await update.message.reply_text(f"❌ نیاز به لول {island_data['required_level']} داری!")
        return
    if island_data["boat_required"] and not current_ship:
        await update.message.reply_text("❌ برای این جزیره کشتی نیاز داری! از /ship_shop بخر.")
        return
    # FIX: قبلاً اینجا فقط پیام "سفر کردی" نشون داده می‌شد ولی هیچی توی
    # دیتابیس ذخیره نمی‌شد؛ یعنی /travel در عمل هیچ اثری نداشت.
    cursor.execute("UPDATE players SET current_island=? WHERE user_id=?", (dest, user.id))
    db.commit()
    await update.message.reply_text(
        f"✅ به {dest} سفر کردی!\nبرای فایت با باس‌های این جزیره: /island_boss"
    )
    # =========================
# UPGRADE
# =========================
async def upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("SELECT money FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    money = row[0]
    await update.message.reply_text(
        "⬆️ ارتقای ویژگی‌ها (هر ارتقا 500 💰):\n\n"
        "/upgrade_hp - افزایش HP +50\n"
        "/upgrade_attack - افزایش Attack +10\n"
        "/upgrade_defense - افزایش Defense +10\n"
        "/upgrade_speed - افزایش Speed +10\n\n"
        f"💰 پول فعلی: {money}"
    )

async def upgrade_hp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute("SELECT money FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row or row[0] < 500:
        await update.message.reply_text("❌ پول کافی نداری! (نیاز: 500 💰)")
        return
    cursor.execute(
        "UPDATE players SET money=money-500, max_hp=max_hp+50, hp=hp+50 WHERE user_id=?",
        (user.id,)
    )
    db.commit()
    await update.message.reply_text("✅ HP +50 شد!")

async def upgrade_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute("SELECT money FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row or row[0] < 500:
        await update.message.reply_text("❌ پول کافی نداری! (نیاز: 500 💰)")
        return
    # FIX: قبلاً فقط پول کم می‌شد ولی attack ذخیره نمی‌شد!
    cursor.execute(
        "UPDATE players SET money=money-500, extra_attack=extra_attack+10 WHERE user_id=?",
        (user.id,)
    )
    db.commit()
    await update.message.reply_text("✅ Attack +10 شد!")

async def upgrade_defense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute("SELECT money FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row or row[0] < 500:
        await update.message.reply_text("❌ پول کافی نداری! (نیاز: 500 💰)")
        return
    # FIX: قبلاً فقط پول کم می‌شد ولی defense ذخیره نمی‌شد!
    cursor.execute(
        "UPDATE players SET money=money-500, extra_defense=extra_defense+10 WHERE user_id=?",
        (user.id,)
    )
    db.commit()
    await update.message.reply_text("✅ Defense +10 شد!")

async def upgrade_speed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute("SELECT money FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row or row[0] < 500:
        await update.message.reply_text("❌ پول کافی نداری! (نیاز: 500 💰)")
        return
    # FIX: قبلاً فقط پول کم می‌شد ولی speed ذخیره نمی‌شد!
    cursor.execute(
        "UPDATE players SET money=money-500, extra_speed=extra_speed+10 WHERE user_id=?",
        (user.id,)
    )
    db.commit()
    await update.message.reply_text("✅ Speed +10 شد!")

# =========================
# POINTS - سیستم جدید Stat Points
# هر لول = 100 پوینت (POINTS_PER_LEVEL). چون هر برد فایت/باس = +5 لول و
# هر برد Raid = +15 لول، این پوینت‌ها همونجا که لول اضافه می‌شه محاسبه
# می‌شن. اینجا فقط منوی خرجشون رو نشون می‌دیم: با دکمه، آزادانه بین
# Attack/Defense/Speed/HP انتخاب می‌کنی.
# =========================
def _points_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for stat, info in POINT_UPGRADES.items():
        buttons.append([InlineKeyboardButton(
            f"{info['label']} +{info['gain']} ({info['cost']} 🎯)",
            callback_data=f"pts_{stat}"
        )])
    return InlineKeyboardMarkup(buttons)


async def points_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("SELECT character FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row or not row[0]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    points = get_points(user.id)
    await update.message.reply_text(
        f"🎯 پوینت فعلی: {points}\n\n"
        "هر لول +100 پوینت می‌ده (برد فایت/باس = +500، برد Raid = +1500).\n"
        "کدوم ویژگی رو میخوای بالا ببری؟",
        reply_markup=_points_keyboard()
    )


async def points_spend_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    stat = query.data[len("pts_"):]
    result = spend_points(user.id, stat)
    await query.answer(result, show_alert=False)
    points = get_points(user.id)
    await query.edit_message_text(
        f"{result}\n\n🎯 پوینت فعلی: {points}\n\nکدوم ویژگی رو میخوای بالا ببری؟",
        reply_markup=_points_keyboard()
    )
# =========================
# RANK
# =========================
async def rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("""
        SELECT username, character, level FROM players
        ORDER BY level DESC, money DESC LIMIT 10
    """)
    rows = cursor.fetchall()
    text = "🏆 رتبه‌بندی:\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (username, char_name, level) in enumerate(rows):
        medal = medals[i] if i < 3 else f"{i+1}."
        char_display = char_name or "بدون شخصیت"
        text += f"{medal} @{username} | {char_display} | Lv{level}\n"
    await update.message.reply_text(text)
    # =========================
# HELP
# =========================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 راهنما:\n\n"
        "/start - شروع\n"
        "/character_select - انتخاب شخصیت\n"
        "/character - شخصیت\n"
        "/stats - آمار\n"
        "/profile - پروفایل\n"
        "/fight - مبارزه PVP\n"
        "/boss - باس\n"
        "/skills - اسکیل‌ها\n"
        "/mastery - مستری\n"
        "/awaken - فعال‌سازی Awakening (نیاز: یه اسکیل با mastery 100)\n"
        "/form - انتخاب فرم با دکمه (فقط شخصیت‌هایی که چند حالت دارن)\n"
        "/points - خرج کردن پوینت‌های لول‌آپ روی Attack/Defense/Speed/HP\n"
        "/shop - فروشگاه\n"
        "/sword_shop - فروشگاه شمشیر\n"
        "/ship_shop - فروشگاه کشتی\n"
        "/buy [نام] - خرید\n"
        "/inventory - کیف\n"
        "/equip [نام] - تجهیز شمشیر\n"
        "/ship - کشتی فعلی\n"
        "/island - جزیره فعلی\n"
        "/island_boss - فایت دکمه‌ای با باس‌های جزیره‌ی فعلی (کول‌داون ۵ دقیقه بعد از کشتن)\n"
        "/travel [نام] - سفر به جزیره\n"
        "/upgrade - منوی ارتقا (HP/Attack/Defense/Speed)\n"
        "/daily - جایزه روزانه\n"
        "/rank - رتبه‌بندی\n"
        "/raid - فایت دکمه‌ای با Raid Boss (Big Mom / Kaido / Blackbeard)، "
        "بعد از کشتنش ۵ دقیقه کول‌داون داره"
        )

# =========================
# APP SETUP
# =========================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("character", character))
app.add_handler(CommandHandler("character_select", character_select))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("profile", profile))

app.add_handler(CommandHandler("fight", fight_cmd))
app.add_handler(CommandHandler("boss", boss))

app.add_handler(CommandHandler("shop", shop))
app.add_handler(CommandHandler("sword_shop", sword_shop))
app.add_handler(CommandHandler("ship_shop", ship_shop))
app.add_handler(CommandHandler("buy", buy))

app.add_handler(CommandHandler("inventory", inventory))
app.add_handler(CommandHandler("equip", equip))

app.add_handler(CommandHandler("skills", skills))
app.add_handler(CommandHandler("mastery", mastery))

app.add_handler(CommandHandler("awaken", awaken))
app.add_handler(CommandHandler("form", form_cmd))
app.add_handler(CommandHandler("points", points_cmd))

app.add_handler(CommandHandler("ship", ship))

app.add_handler(CommandHandler("island", island))
app.add_handler(CommandHandler("island_boss", island_boss_cmd))
app.add_handler(CommandHandler("travel", travel))

app.add_handler(CommandHandler("upgrade", upgrade))
app.add_handler(CommandHandler("upgrade_hp", upgrade_hp))
app.add_handler(CommandHandler("upgrade_attack", upgrade_attack))
app.add_handler(CommandHandler("upgrade_defense", upgrade_defense))
app.add_handler(CommandHandler("upgrade_speed", upgrade_speed))
app.add_handler(CommandHandler("daily", daily_cmd))
app.add_handler(CommandHandler("rank", rank))
app.add_handler(CommandHandler("help", help_cmd))

app.add_handler(CommandHandler("raid", raid))

app.add_handler(CallbackQueryHandler(pick_character_callback, pattern=r"^pick_"))
app.add_handler(CallbackQueryHandler(fight_callback, pattern=r"^fight_"))
app.add_handler(CallbackQueryHandler(fight_attack_callback, pattern=r"^atk_"))
# FIX: قبلاً اینجا raid_pick_callback / raid_join_callback / raid_attack_callback
# رجیستر می‌شدن که اصلاً import/تعریف نشده بودن → NameError همون لحظه‌ی
# استارت ربات (کرش کامل، حتی قبل از رسیدن به polling). raid_handler.py
# اصلاً چنین کالبک‌هایی نداره؛ raid_callback واقعی (که import شده بود ولی
# هیچوقت رجیستر نشده بود) هم دقیقاً همینجا باید ثبت شه تا دکمه‌های
# Big Mom/Kaido/Blackbeard توی /raid واقعاً کار کنن.
app.add_handler(CallbackQueryHandler(raid_callback, pattern=r"^raid_"))
app.add_handler(CallbackQueryHandler(raid_attack_callback, pattern=r"^ratk_"))
app.add_handler(CallbackQueryHandler(island_boss_pick_callback, pattern=r"^ibpick_"))
app.add_handler(CallbackQueryHandler(island_boss_attack_callback, pattern=r"^ibatk_"))
app.add_handler(CallbackQueryHandler(form_pick_callback, pattern=r"^frm_"))
app.add_handler(CallbackQueryHandler(points_spend_callback, pattern=r"^pts_"))
app.add_handler(CallbackQueryHandler(sword_shop_page_callback, pattern=r"^swdpg_"))
print("🏴‍☠️ Bot Online - One Piece RPG")
app.run_polling()
