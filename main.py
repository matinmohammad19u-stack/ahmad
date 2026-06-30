from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from database import db, cursor
from characters import characters
from skill import SKILL_DB                          # FIX: نام درست
from skill_system import get_available_skills, add_mastery
from shop import buy_item, SHOP_ITEMS, get_money
from inventory import get_inventory, add_item
from awakening import check_awakening
from form_system import change_form                  # FIX: form_system نه form
from ship_system import ships                        # FIX: ship_system نه ships
from swords_shop import SWORDS_SHOP                  # FIX: فایل ساخته شد
from islands import islands
from raid_handler import raid, raid_callback          # FIX: raid files ساخته شدن
from fight import battle                              # FIX: import فراموش شده بود
from compute_damage import compute_damage             # FIX: برای mastery scaling در boss
import os
import random
import datetime

TOKEN = os.environ.get("TOKEN")

# =========================
# آنلاین یوزرها
# =========================
online_users = {}

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username or "no_username"
    cursor.execute(
        "INSERT OR IGNORE INTO players (user_id, username) VALUES (?, ?)",
        (user.id, username)
    )
    db.commit()
    online_users[user.id] = user.first_name
    await update.message.reply_text(
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
        "/form - تغییر فرم\n"
        "/shop - فروشگاه آیتم\n"
        "/sword_shop - فروشگاه شمشیر\n"
        "/ship_shop - فروشگاه کشتی\n"
        "/buy [نام] - خرید\n"
        "/inventory - کیف\n"
        "/equip [نام] - تجهیز\n"
        "/ship - کشتی فعلی\n"
        "/island - جزیره فعلی\n"
        "/travel [نام] - سفر\n"
        "/upgrade - ارتقا\n"
        "/daily - جایزه روزانه\n"
        "/rank - رتبه‌بندی\n"
        "/raid - نبرد گروهی\n"
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
               equipped_weapon, extra_attack, extra_defense, extra_speed
        FROM players WHERE user_id=?
    """, (user.id,))
    data = cursor.fetchone()
    if not data or not data[0]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    char_name, hp, max_hp, form, awakening, weapon, ex_atk, ex_def, ex_spd = data
    char_stats = characters[char_name]["stats"]
    forms_available = list(SKILL_DB.get(char_name, {}).keys())

    total_atk = char_stats["attack"] + ex_atk
    total_def = char_stats["defense"] + ex_def
    total_spd = char_stats["speed"] + ex_spd

    if weapon and weapon in SWORDS_SHOP:
        sword_bonus = SWORDS_SHOP[weapon]["attack"]
        sword_bonus = int(sword_bonus * 1.5) if char_name == "Roronoa Zoro" else sword_bonus
        total_atk += sword_bonus

    await update.message.reply_text(
        f"🎭 شخصیت: {char_name}\n"
        f"⚡ فرم فعلی: {form or 'Base'}\n"
        f"🌀 Awakening: {'🔥 Yes' if awakening else '❌ No'}\n"
        f"❤️ HP: {hp}/{max_hp}\n"
        f"⚔️ Attack: {total_atk}\n"
        f"🛡️ Defense: {total_def}\n"
        f"💨 Speed: {total_spd}\n"
        f"🗡️ سلاح: {weapon or 'ندارم'}\n\n"
        f"🔄 فرم‌های موجود:\n" +
        "\n".join(f"  • {f}" for f in forms_available)
    )

# =========================
# STATS
# =========================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("""
        SELECT level, xp, money, character, hp, max_hp,
               equipped_weapon, current_ship,
               extra_attack, extra_defense, extra_speed
        FROM players WHERE user_id=?
    """, (user.id,))
    data = cursor.fetchone()
    if not data or not data[3]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    level, xp, money, char_name, hp, max_hp, weapon, ship, ex_atk, ex_def, ex_spd = data
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
# FIGHT (PVP آنلاین)
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
    enemies = {uid: name for uid, name in online_users.items() if uid != user.id}
    if not enemies:
        await update.message.reply_text("❌ بازیکن آنلاین دیگه‌ای نیست!")
        return
    keyboard = [
        [InlineKeyboardButton(f"⚔️ {name}", callback_data=f"fight_{uid}")]
        for uid, name in enemies.items()
    ]
    await update.message.reply_text("⚔️ با کی میخوای بجنگی؟", reply_markup=InlineKeyboardMarkup(keyboard))

async def fight_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    enemy_id = int(query.data.replace("fight_", ""))

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

    # FIX: قبلاً سلاح تجهیزشده فقط توی /stats نشون داده می‌شد ولی روی فایت واقعی
    # هیچ تاثیری نداشت! الان واقعاً توی محاسبه دمیج اعمال می‌شه.
    if p1[5] and p1[5] in SWORDS_SHOP:
        bonus = SWORDS_SHOP[p1[5]]["attack"]
        bonus = int(bonus * 1.5) if p1[0] == "Roronoa Zoro" else bonus
        p1_data["stats"]["attack"] += bonus
    if p2[5] and p2[5] in SWORDS_SHOP:
        bonus = SWORDS_SHOP[p2[5]]["attack"]
        bonus = int(bonus * 1.5) if p2[0] == "Roronoa Zoro" else bonus
        p2_data["stats"]["attack"] += bonus

    # FIX: قبلاً battle() همیشه از فرم Base استفاده می‌کرد و /form هیچ
    # تاثیری روی PVP نداشت! حالا فرم واقعی هر بازیکن پاس داده می‌شه.
    p1_form = p1[6] or "Base"
    p2_form = p2[6] or "Base"

    # FIX: battle حالا final_hp1, final_hp2, skills_used هم برمی‌گردونه
    log, winner, earned_money, final_hp1, final_hp2, skills_used = battle(
        p1_data, p2_data, SKILL_DB, p1_form, p2_form
    )

    # FIX: قبلاً اگه p1 می‌باخت، برنده‌ی واقعی (p2/حریف) هیچ جایزه‌ای نمی‌گرفت!
    # و سطح‌بندی PvP باید +5 باشه (هماهنگ با بقیه‌ی بات)، نه +1
    if winner == p1[0]:
        cursor.execute(
            "UPDATE players SET level=level+5, money=money+?, hp=? WHERE user_id=?",
            (earned_money, max(1, final_hp1), user.id)
        )
        cursor.execute("UPDATE players SET hp=max_hp WHERE user_id=?", (enemy_id,))
    else:
        cursor.execute("UPDATE players SET hp=max_hp WHERE user_id=?", (user.id,))
        cursor.execute(
            "UPDATE players SET level=level+5, money=money+?, hp=? WHERE user_id=?",
            (earned_money, max(1, final_hp2), enemy_id)
        )

    cursor.execute("""
        INSERT INTO fight_history (user_id, enemy, result, reward_xp, reward_money)
        VALUES (?, ?, ?, ?, ?)
    """, (user.id, p2[0], "WIN" if winner == p1[0] else "LOSE", 0, earned_money))

    # FIX: مستری اسکیل‌های استفاده‌شده آپدیت می‌شه (قبلاً هیچوقت آپدیت نمی‌شد،
    # یعنی /skills و /mastery همیشه قفل و صفر می‌موندن!)
    mastery_rate = 3 if winner == p1[0] else 1
    for skill_name, count in skills_used.items():
        add_mastery(user.id, p1[0], skill_name, amount=mastery_rate * count)

    db.commit()
    await query.edit_message_text("\n".join(log)[:4000])

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

    # دقیقاً مثل /stats: attack پایه + ارتقا + بونوس شمشیر
    total_attack = characters[char_name]["stats"]["attack"] + extra_attack
    if weapon and weapon in SWORDS_SHOP:
        sword_bonus = SWORDS_SHOP[weapon]["attack"]
        sword_bonus = int(sword_bonus * 1.5) if char_name == "Roronoa Zoro" else sword_bonus
        total_attack += sword_bonus

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
        cursor.execute(
            "UPDATE players SET level=level+5, money=money+?, hp=? WHERE user_id=?",
            (money_reward, max(1, player_hp), user.id)
        )
        log.append(f"🏆 Boss کشتی! +5 لول 💰 +{money_reward}")
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
# SWORD SHOP - FIX: این تابع وجود نداشت ولی handler ثبت شده بود!
# =========================
async def sword_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    text = "⚔️ فروشگاه شمشیر:\n\n"
    for name, sword in SWORDS_SHOP.items():
        text += f"🗡️ {name}\n   ATK: +{sword['attack']} | {sword['price']} 💰\n   {sword.get('description', '')}\n\n"
    text += "برای خرید: /buy [نام شمشیر]"
    await update.message.reply_text(text)

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
# FORM - FIX: این دستور import شده بود ولی handler نداشت
# =========================
async def form_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    if not context.args:
        cursor.execute("SELECT character, current_form FROM players WHERE user_id=?", (user.id,))
        data = cursor.fetchone()
        if not data or not data[0]:
            await update.message.reply_text("❌ اول /character_select بزن.")
            return
        char_name, form = data
        forms = list(SKILL_DB.get(char_name, {}).keys())
        text = f"⚡ فرم فعلی: {form or 'Base'}\n\nفرم‌های موجود:\n"
        for f in forms:
            text += f"• {f}\n"
        text += "\nبرای تغییر: /form [نام فرم]"
        await update.message.reply_text(text)
        return
    form_name = " ".join(context.args)
    result = change_form(user.id, form_name)
    await update.message.reply_text(result)

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
    cursor.execute("SELECT level FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row:
        await update.message.reply_text("❌ اول /start بزن.")
        return
    level = row[0]
    current_island = "East Blue"
    for name, data in islands.items():
        if level >= data["required_level"]:
            current_island = name
    island_data = islands[current_island]
    text = f"🗺️ جزیره فعلی: {current_island}\n"
    text += f"⭐ لول مورد نیاز: {island_data['required_level']}\n\n📍 پارت‌ها:\n"
    for num, part in island_data["parts"].items():
        text += f"  Part {num}: {part['name']}\n  👹 Boss: {', '.join(part['bosses'])}\n\n"
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
    await update.message.reply_text(f"✅ به {dest} سفر کردی!")

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
# DAILY
# =========================
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    today = datetime.date.today().isoformat()

    cursor.execute("SELECT last_daily, character FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row or not row[1]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return

    # FIX: قبلاً وضعیت claim توی context.bot_data (حافظه) نگه داشته می‌شد
    # و با هر ری‌استارت بات پاک می‌شد. الان توی دیتابیس ذخیره می‌شه.
    if row[0] == today:
        await update.message.reply_text("❌ جایزه روزانه رو قبلاً گرفتی! فردا بیا.")
        return

    cursor.execute(
        "UPDATE players SET money=money+500, hp=max_hp, last_daily=? WHERE user_id=?",
        (today, user.id)
    )
    db.commit()
    await update.message.reply_text("🎁 جایزه روزانه!\n\n💰 +500\n❤️ HP ریست شد!")

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
        "/form [نام] - تغییر فرم\n"
        "/shop - فروشگاه\n"
        "/sword_shop - فروشگاه شمشیر\n"
        "/ship_shop - فروشگاه کشتی\n"
        "/buy [نام] - خرید\n"
        "/inventory - کیف\n"
        "/equip [نام] - تجهیز شمشیر\n"
        "/ship - کشتی فعلی\n"
        "/island - جزیره فعلی\n"
        "/travel [نام] - سفر به جزیره\n"
        "/upgrade - منوی ارتقا (HP/Attack/Defense/Speed)\n"
        "/daily - جایزه روزانه\n"
        "/rank - رتبه‌بندی\n"
        "/raid - نبرد Raid Boss (Big Mom / Kaido / Blackbeard)"
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

app.add_handler(CommandHandler("ship", ship))

app.add_handler(CommandHandler("island", island))
app.add_handler(CommandHandler("travel", travel))

app.add_handler(CommandHandler("upgrade", upgrade))
app.add_handler(CommandHandler("upgrade_hp", upgrade_hp))
app.add_handler(CommandHandler("upgrade_attack", upgrade_attack))
app.add_handler(CommandHandler("upgrade_defense", upgrade_defense))
app.add_handler(CommandHandler("upgrade_speed", upgrade_speed))

app.add_handler(CommandHandler("daily", daily))
app.add_handler(CommandHandler("rank", rank))
app.add_handler(CommandHandler("help", help_cmd))

app.add_handler(CommandHandler("raid", raid))

app.add_handler(CallbackQueryHandler(pick_character_callback, pattern=r"^pick_"))
app.add_handler(CallbackQueryHandler(fight_callback, pattern=r"^fight_"))
app.add_handler(CallbackQueryHandler(raid_callback, pattern=r"^raid_"))
print("🏴‍☠️ Bot Online - One Piece RPG")
app.run_polling()
