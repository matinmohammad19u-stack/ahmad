import sqlite3

db = sqlite3.connect("game.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    money INTEGER DEFAULT 100
)
""")

db.commit()