import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS workouts 
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    sport_type TEXT NOT NULL,
    duration INTEGER NOT NULL,
    comment TEXT)
""")
conn.commit()
conn.close()

print("big penis")