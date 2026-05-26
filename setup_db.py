import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# users
cursor.execute("""
CREATE TABLE IF NOT EXISTS users 
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL)
""")

# trainings
cursor.execute("""
CREATE TABLE IF NOT EXISTS workouts 
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    sport_type TEXT NOT NULL,
    duration INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id))
""")

conn.commit()
conn.close()

print("big penis")