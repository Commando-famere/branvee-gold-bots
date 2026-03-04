import sqlite3

conn = sqlite3.connect('data/branvee.db')
c = conn.cursor()

try:
    c.execute("ALTER TABLE users ADD COLUMN telegram_id INTEGER")
    print("✅ Added telegram_id column")
except:
    print("ℹ️ telegram_id column may already exist")

conn.commit()
conn.close()
