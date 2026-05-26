from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    workouts = conn.execute('SELECT * FROM workouts').fetchall()
    conn.close()
    return render_template('index.html', workouts=workouts)

@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        date = request.form['date']
        sport = request.form['sport_type']
        duration = request.form['duration']
        comment = request.form['comment']

        conn = get_db_connection()
        conn.execute('INSERT INTO workouts (date, sport_type, duration, comment) VALUES (?, ?, ?, ?)',
                     (date, sport, duration, comment))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True)