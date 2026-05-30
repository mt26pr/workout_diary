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

# workouts
@app.route('/workouts')
@login_required
def workouts_history():
    conn = get_db_connection()
    workouts = conn.execute('''
                            SELECT workouts.*, sports.name as sport_name
                            FROM workouts
                                     INNER JOIN sports ON workouts.sport_id = sports.id
                            WHERE workouts.user_id = ?
                            ''', (current_user.id,)).fetchall()
    conn.close()
    return render_template('index.html', workouts=workouts)

# trainings adding
@app.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    if request.method == 'POST':
        date_value = request.form['date']
        sport_id = request.form['sport_id']
        duration = request.form['duration']

        conn = get_db_connection()
        conn.execute('INSERT INTO workouts (user_id, date, sport_id, duration) VALUES (?, ?, ?, ?)',
                     (current_user.id, date_value, sport_id, duration))
        conn.commit()
        conn.close()
        flash('Workout added successfully!', 'success')
        return redirect('/workouts')
    conn = get_db_connection()
    sports = conn.execute('SELECT * FROM sports').fetchall()

    # to see variants
    from datetime import date
    today_date = date.today().strftime('%Y-%m-%d')
    conn.close()
    return render_template('add.html', sports=sports, today_date=today_date)

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
from datetime import datetime, timedelta


@app.route('/analytics')
@login_required
def analytics():
    conn = get_db_connection()

    total_workouts = conn.execute('SELECT COUNT(*) FROM workouts WHERE user_id = ?', (current_user.id,)).fetchone()[0]
    total_minutes = conn.execute('SELECT SUM(duration) FROM workouts WHERE user_id = ?', (current_user.id,)).fetchone()[
                        0] or 0
    total_hours = round(total_minutes / 60, 1)

    favorite_sport_row = conn.execute('''
                                      SELECT s.name, COUNT(w.id) as count
                                      FROM workouts w
                                               JOIN sports s ON w.sport_id = s.id
                                      WHERE w.user_id = ?
                                      GROUP BY w.sport_id
                                      ORDER BY count DESC
                                      LIMIT 1
                                      ''', (current_user.id,)).fetchone()
    favorite_sport = favorite_sport_row['name'] if favorite_sport_row else "None yet"
    # --------------------------------

    today = datetime.today()

    week_labels = []
    week_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        week_labels.append(day.strftime('%d %b'))

        count = conn.execute(
            'SELECT COUNT(*) FROM workouts WHERE user_id = ? AND date = ?',
            (current_user.id, day_str)
        ).fetchone()[0]
        week_data.append(count)

    month_labels = []
    month_data = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        month_labels.append(day.strftime('%d'))

        count = conn.execute(
            'SELECT COUNT(*) FROM workouts WHERE user_id = ? AND date = ?',
            (current_user.id, day_str)
        ).fetchone()[0]
        month_data.append(count)

    year_data = {}

    for i in range(364, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')

        count = conn.execute(
            'SELECT COUNT(*) FROM workouts WHERE user_id = ? AND date = ?',
            (current_user.id, day_str)
        ).fetchone()[0]

        if count > 0:
            year_data[day_str] = count

    conn.close()

    return render_template(
        'analytics.html',
        total_workouts=total_workouts,
        total_hours=total_hours,
        favorite_sport=favorite_sport,
        week_labels=week_labels,
        week_data=week_data,
        month_labels=month_labels,
        month_data=month_data,
        year_data = year_data
    )


# delete workout
@app.route('/delete/<int:workout_id>')
@login_required
def delete_workout(workout_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM workouts WHERE id = ? AND user_id = ?', (workout_id, current_user.id))
    conn.commit()
    conn.close()
    flash('Workout deleted successfully!', 'success')
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
        sport_id = request.form['sport_id']
        duration = request.form['duration']
        conn.execute('''
                 UPDATE workouts
                 SET date       = ?,
                     sport_id = ?,
                     duration   = ?
                 WHERE id = ?
                   AND user_id = ?
                 ''', (date, sport_id, duration, workout_id, current_user.id))
        conn.commit()
        conn.close()
        flash('Workout updated successfully!', 'success')
        return redirect('/workouts')
    sports = conn.execute('SELECT * FROM sports').fetchall()
    conn.close()
    return render_template('edit.html', workout=workout, sports=sports)

if __name__ == '__main__':
    app.run(debug=True)