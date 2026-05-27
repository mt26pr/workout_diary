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
    sport_id INTEGER NOT NULL,
    duration INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (sport_id) REFERENCES sports (id))
""")

# sports types
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
''')
default_sports = [('Running',), ('Swimming',), ('Cycling',), ('Gym / Workout',), ('Football',)]
cursor.executemany('INSERT OR IGNORE INTO sports (name) VALUES (?)', default_sports)

conn.commit()
conn.close()

print("success")