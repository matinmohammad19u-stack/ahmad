import sqlite3
import os

# =========================
# FORCE SAFE PATH (Railway fix)
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "game.db")

db = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = db.cursor()

print(f"📂 Database connected: {DB_PATH}")
