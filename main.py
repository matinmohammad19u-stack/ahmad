from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from database import db, cursor
from characters import characters
from skill import SKILL_DB
from skill_system import get_available_skills, add_mastery
from shop import buy_item, SHOP_ITEMS, get_money
from inventory import get_inventory, add_item
from awakening import check_awakening
from form import change_form
from ships import ships
from swords_shop import SWORDS_SHOP
from islands import islands
import os
import random
import datetime
from raid_bigmom import bigmom
from raid_kaido import kaido
from raid_blackbeard import blackbeard
from raid_handler import raid, raid_callback
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
    cursor.execute("INSERT OR IGNORE INTO players (user_id, username) VALUES (?, ?)", (user.id, username))
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
        "/shop - فروشگاه آیتم\n"
        "/sword_shop - فروشگاه شمشیر\n"
        "/ship_shop - فروشگاه کشتی\n"
        "/buy - خرید\n"
        "/inventory - کیف\n"
        "/equip - تجهیز آیتم\n"
        "/ship - کشتی فعلی\n"
        "/island - جزیره فعلی\n"
        "/travel - سفر\n"
        "/upgrade - ارتقا\n"
        "/daily - جایزه روزانه\n"
        "/rank - رتبه‌بندی\n"
        "/help - راهنما"
        "/raid - نبرد گروهی\n"
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
    keyboard = [[InlineKeyboardButton(name, callback_data=f"pick_{name}")] for name in available]
    await update.message.reply_text("🎭 یه شخصیت انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))

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
    cursor.execute("INSERT OR IGNORE INTO players (user_id, username) VALUES (?, ?)", (user.id, user.username or "no_username"))
    cursor.execute("UPDATE players SET character=?, hp=?, max_hp=? WHERE user_id=?", (chosen_name, hp, hp, user.id))
    cursor.execute("DELETE FROM available_characters WHERE name=?", (chosen_name,))
    db.commit()
    await query.edit_message_text(
        f"🎉 تبریک {user.first_name}!\n\n"
        f"🎭 شخصیت: {chosen_name}\n"
        f"❤️ HP: {hp}"
    )

# =========================
# STATS
# =========================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("""
        SELECT level, xp, money, character, hp, max_hp, equipped_weapon, current_ship
        FROM players WHERE user_id=?
    """, (user.id,))
    data = cursor.fetchone()
    if not data or not data[3]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    level, xp, money, char_name, hp, max_hp, weapon, ship = data
    char_stats = characters[char_name]["stats"]
    attack = char_stats["attack"]
    defense = char_stats["defense"]
    speed = char_stats["speed"]
    if weapon and weapon in SWORDS_SHOP:
        sword_attack = SWORDS_SHOP[weapon]["attack"]
        bonus = int(sword_attack * 1.5) if char_name == "Roronoa Zoro" else sword_attack
        attack += bonus
    await update.message.reply_text(
        f"📊 آمار {char_name}\n\n"
        f"⭐ لول: {level}\n"
        f"💰 پول: {money}\n"
        f"❤️ HP: {hp}/{max_hp}\n"
        f"⚔️ Attack: {attack}\n"
        f"🛡️ Defense: {defense}\n"
        f"💨 Speed: {speed}\n"
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
        f"⚡ فرم: {form}\n"
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
    keyboard = [[InlineKeyboardButton(f"⚔️ {name}", callback_data=f"fight_{uid}")] for uid, name in enemies.items()]
    await update.message.reply_text("⚔️ با کی میخوای بجنگی؟", reply_markup=InlineKeyboardMarkup(keyboard))

async def fight_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    enemy_id = int(query.data.replace("fight_", ""))
    cursor.execute("SELECT character, hp FROM players WHERE user_id=?", (user.id,))
    p1 = cursor.fetchone()
    cursor.execute("SELECT character, hp FROM players WHERE user_id=?", (enemy_id,))
    p2 = cursor.fetchone()
    if not p1 or not p1[0] or not p2 or not p2[0]:
        await query.edit_message_text("❌ یکی از بازیکنا شخصیت ندارن!")
        return
    p1_data = {"name": p1[0], "stats": characters[p1[0]]["stats"].copy()}
    p2_data = {"name": p2[0], "stats": characters[p2[0]]["stats"].copy()}
    p1_data["stats"]["hp"] = p1[1]
    p2_data["stats"]["hp"] = p2[1]
    log, winner, earned_money = battle(p1_data, p2_data, SKILL_DB)
    if winner == p1[0]:
        cursor.execute("UPDATE players SET level=level+5, xp=0, money=money+? WHERE user_id=?", (earned_money, user.id))
        cursor.execute("UPDATE players SET hp=max_hp WHERE user_id=?", (enemy_id,))
    else:
        cursor.execute("UPDATE players SET hp=max_hp WHERE user_id=?", (user.id,))
    cursor.execute("""
        INSERT INTO fight_history (user_id, enemy, result, reward_xp, reward_money)
        VALUES (?, ?, ?, ?, ?)
    """, (user.id, p2[0], "WIN" if winner == p1[0] else "LOSE", 0, earned_money))
    db.commit()
    await query.edit_message_text(log[:4000])
# =========================
# BOSS
# =========================
async def boss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("SELECT character, hp, level FROM players WHERE user_id=?", (user.id,))
    data = cursor.fetchone()
    if not data or not data[0]:
        await update.message.reply_text("❌ اول /character_select بزن.")
        return
    char_name, hp, level = data
    if hp <= 0:
        await update.message.reply_text("❌ HP نداری!")
        return
    bosses = ["Kaido", "Big Mom", "Blackbeard", "Akainu", "Doflamingo"]
    boss_name = random.choice(bosses)
    boss_hp = 2000 + level * 200
    player_attack = characters[char_name]["stats"]["attack"]
    boss_attack = 100 + level * 10
    log = [f"👹 Boss Battle: {char_name} VS {boss_name}!", f"❤️ Boss HP: {boss_hp}"]
    turn = 1
    player_hp = hp
    while player_hp > 0 and boss_hp > 0:
        dmg = int(player_attack * random.uniform(0.9, 1.2))
        boss_hp -= dmg
        log.append(f"Turn {turn}: تو {dmg} زدی به {boss_name}")
        if boss_hp <= 0:
            break
        b_dmg = int(boss_attack * random.uniform(0.8, 1.3))
        player_hp -= b_dmg
        log.append(f"Turn {turn}: {boss_name} {b_dmg} زد به تو")
        turn += 1
    if player_hp > 0:
        money = 500 + level * 50
        cursor.execute("UPDATE players SET level=level+5, xp=0, money=money+?, hp=? WHERE user_id=?", (money, max(1, player_hp), user.id))
        log.append(f"🏆 Boss کشتی! +5 لول 💰 +{money}")
    else:
        cursor.execute("UPDATE players SET hp=max_hp WHERE user_id=?", (user.id,))
        log.append("💀 باختی! HP ریست شد.")
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
        text += f"- {name}: {item['price']} 💰\n"
    text += "\nبرای خرید: /buy [نام آیتم]"
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
            cursor.execute("UPDATE players SET money=money-? WHERE user_id=?", (sword["price"], user.id))
            add_item(user.id, item_name, "sword")
            db.commit()
            result = f"✅ {item_name} خریداری شد!"
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
                cursor.execute("UPDATE players SET money=money-?, current_ship=? WHERE user_id=?", (ship["price"], item_name, user.id))
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
    cursor.execute("SELECT quantity FROM inventory WHERE user_id=? AND item_name=?", (user.id, item_name))
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
        cursor.execute("UPDATE players SET equipped_weapon=? WHERE user_id=?", (item_name, user.id))
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
    skill_list = get_available_skills(user.id, char_name, SKILLS_DB, form or "Base")
    if not skill_list:
        await update.message.reply_text("❌ اسکیلی پیدا نشد.")
        return
    text = f"⚡ اسکیل‌های {char_name} ({form}):\n\n"
    for sk in skill_list:
        locked = "🔒" if not sk["unlocked"] else "✅"
        text += f"{locked} {sk['name']} | DMG: {sk['damage']} | Mastery: {sk['mastery']}/100\n"
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
        await update.message.reply_text("❌ هنوز مستری نداری! اول /fight بزن.")
        return
    text = f"🎯 Mastery {char_name}:\n\n"
    for skill_name, mast, unlocked in rows:
        bar = "█" * (mast // 10) + "░" * (10 - mast // 10)
        status = "✅" if unlocked else "🔒"
        text += f"{status} {skill_name}\n[{bar}] {mast}/100\n\n"
    await update.message.reply_text(text)

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
            text += f"- {name} (Lv{data['required_level']})\n"
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
    await update.message.reply_text(f"✅ به {dest} سفر کردی! 🌊")

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
    cursor.execute("UPDATE players SET money=money-500, max_hp=max_hp+50, hp=hp+50 WHERE user_id=?", (user.id,))
    db.commit()
    await update.message.reply_text("✅ HP +50 شد!")

async def upgrade_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute("SELECT money FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row or row[0] < 500:
        await update.message.reply_text("❌ پول کافی نداری! (نیاز: 500 💰)")
        return
    cursor.execute("UPDATE players SET money=money-500 WHERE user_id=?", (user.id,))
    db.commit()
    await update.message.reply_text("✅ Attack +10 شد!")

async def upgrade_defense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute("SELECT money FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row or row[0] < 500:
        await update.message.reply_text("❌ پول کافی نداری! (نیاز: 500 💰)")
        return
    cursor.execute("UPDATE players SET money=money-500 WHERE user_id=?", (user.id,))
    db.commit()
    await update.message.reply_text("✅ Defense +10 شد!")

async def upgrade_speed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute("SELECT money FROM players WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row or row[0] < 500:
        await update.message.reply_text("❌ پول کافی نداری! (نیاز: 500 💰)")
        return
    cursor.execute("UPDATE players SET money=money-500 WHERE user_id=?", (user.id,))
    db.commit()
    await update.message.reply_text("✅ Speed +10 شد!")

# =========================
# DAILY
# =========================
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    today = datetime.date.today().isoformat()
    if 'daily_claims' not in context.bot_data:
        context.bot_data['daily_claims'] = {}
    if context.bot_data['daily_claims'].get(user.id) == today:
        await update.message.reply_text("❌ جایزه روزانه رو قبلاً گرفتی! فردا بیا.")
        return
    cursor.execute("UPDATE players SET money=money+500, xp=0, hp=max_hp WHERE user_id=?", (user.id,))
    db.commit()
    context.bot_data['daily_claims'][user.id] = today
    await update.message.reply_text("🎁 جایزه روزانه!\n\n💰 +500\n❤️ HP ریست شد!")

# =========================
# RANK
# =========================
async def rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    online_users[user.id] = user.first_name
    cursor.execute("""
        SELECT username, character, level FROM players
        ORDER BY level DESC, xp DESC LIMIT 10
    """)
    rows = cursor.fetchall()
    text = "🏆 رتبه‌بندی:\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (username, char_name, level) in enumerate(rows):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} @{username} | {char_name} | Lv{level}\n"
    await update.message.reply_text(text)
    
# =========================
# HELP
# =========================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 راهنما:\n\n"
        "/start - شروع\n/character_select - انتخاب شخصیت\n"
        "/character - شخصیت\n/stats - آمار\n/profile - پروفایل\n"
        "/fight - مبارزه\n/boss - باس\n/skills - اسکیل\n"
        "/mastery - مستری\n/shop - فروشگاه\n/sword_shop - شمشیر\n"
        "/ship_shop - کشتی\n/buy [نام] - خرید\n/inventory - کیف\n"
        "/equip [نام] - تجهیز\n/ship - کشتی فعلی\n"
        "/island - جزیره\n/travel [نام] - سفر\n"
        "/upgrade - ارتقا\n/daily - جایزه روزانه\n/rank - رتبه‌بندی"
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
app.add_handler(CallbackQueryHandler(pick_character_callback, pattern="^pick_"))
app.add_handler(CallbackQueryHandler(fight_callback, pattern="^fight_"))
app.add_handler(CommandHandler("raid", raid))
app.add_handler(CallbackQueryHandler(raid_callback, pattern="^raid_"))
print("Bot Online...")
app.run_polling()
