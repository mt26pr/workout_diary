from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-123'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = None

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(id=user['id'], username=user['username'])
    return None

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

#main menu
@app.route('/')
@login_required
def index():
    return render_template('dashboard.html')

@app.route('/workouts')
@login_required
def workouts_history():
    conn = get_db_connection()
    workouts = conn.execute('SELECT * FROM workouts WHERE user_id = ?', (current_user.id,)).fetchall()
    conn.close()
    return render_template('index.html', workouts=workouts)

# trainings adding
@app.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    if request.method == 'POST':
        date = request.form['date']
        sport = request.form['sport_type']
        duration = request.form['duration']

        conn = get_db_connection()
        conn.execute('INSERT INTO workouts (user_id, date, sport_type, duration) VALUES (?, ?, ?, ?)',
                     (current_user.id, date, sport, duration))
        conn.commit()
        conn.close()
        return redirect('/workouts')
    return render_template('add.html')

# registration
@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()
            return redirect("/login")
        except sqlite3.IntegrityError:
            conn.close()
            flash('This login is already in use!', 'error')
            return redirect('/register')
    return render_template("register.html")

# loging in
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = True if request.form.get('remember') else False

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(id=user['id'], username=user['username'])
            login_user(user_obj, remember=remember)
            return redirect('/')
        else:
            flash('Wrong login or password!', 'error')
            return redirect('/login')
    return render_template("login.html")

#loging off
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

#analytics
@app.route('/analytics')
@login_required
def analytics():
    conn = get_db_connection()
    #number of trainings
    total_workouts_row = conn.execute(
        'SELECT COUNT(*) as total FROM workouts WHERE user_id = ?',
        (current_user.id,)).fetchone()
    total_workouts = total_workouts_row['total']

    #total duration
    total_duration_row = conn.execute(
        'SELECT SUM(duration) as total_sum FROM workouts WHERE user_id = ?',
        (current_user.id,)).fetchone()
    total_duration = total_duration_row['total_sum'] or 0

    # favourite sport
    favorite_sport_row = conn.execute('''
                                      SELECT sport_type, COUNT(sport_type) as count
                                      FROM workouts
                                      WHERE user_id = ?
                                      GROUP BY sport_type
                                      ORDER BY count DESC
                                      LIMIT 1
                                      ''', (current_user.id,)).fetchone()
    if favorite_sport_row:
        favorite_sport = favorite_sport_row['sport_type']
    else:
        favorite_sport = 'None yet'
    # record
    max_duration_row = conn.execute(
        'SELECT MAX(duration) as max_dur FROM workouts WHERE user_id = ?',
        (current_user.id,)).fetchone()
    max_duration = max_duration_row['max_dur'] or 0

    # average time
    avg_duration_row = conn.execute(
        'SELECT AVG(duration) as avg_dur FROM workouts WHERE user_id = ?',
        (current_user.id,)).fetchone()
    avg_duration = round(avg_duration_row['avg_dur'], 1) if avg_duration_row['avg_dur'] else 0

    conn.close()

    return render_template(
        'analytics.html',
        total_workouts=total_workouts,
        total_duration=total_duration,
        favorite_sport=favorite_sport,
        max_duration=max_duration,
        avg_duration=avg_duration)

# delete workout
@app.route('/delete/<int:workout_id>')
@login_required
def delete_workout(workout_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM workouts WHERE id = ? AND user_id = ?', (workout_id, current_user.id))
    conn.commit()
    conn.close()
    return redirect('/workouts')

# edit workout
@app.route('/edit/<int:workout_id>', methods=('GET', 'POST'))
@login_required
def edit_workout(workout_id):
    conn = get_db_connection()
    workout = conn.execute('SELECT * FROM workouts WHERE id = ? AND user_id = ?',
                           (workout_id, current_user.id)).fetchone()
    if workout is None:
        conn.close()
        return redirect('/workouts')
    if request.method == 'POST':
        date = request.form['date']
        sport = request.form['sport_type']
        duration = request.form['duration']
        conn.execute('''
                 UPDATE workouts
                 SET date       = ?,
                     sport_type = ?,
                     duration   = ?
                 WHERE id = ?
                   AND user_id = ?
                 ''', (date, sport, duration, workout_id, current_user.id))
        conn.commit()
        conn.close()
        return redirect('/workouts')
    conn.close()
    return render_template('edit.html', workout=workout)

if __name__ == '__main__':
    app.run(debug=True)