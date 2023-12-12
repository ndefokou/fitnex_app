from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session  # Import Flask-Session

app = Flask(__name__)
app.secret_key = 'your-secret-key'
db_path = 'workout.db'

user_profiles = {}

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        return user_profiles.get(user_id)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Securely configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize Flask-Session
Session(app)

def create_tables():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                exercise TEXT,
                sets INTEGER,
                reps INTEGER,
                weight REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                goal TEXT,
                target INTEGER
            )
        ''')
        conn.commit()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        age = int(request.form.get('age'))
        gender = request.form.get('gender')
        weight = float(request.form.get('weight'))
        height = float(request.form.get('height'))

        if username in user_profiles:
            return 'User already exists'

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        user_profiles[username] = {'username': username, 'password': hashed_password, 'age': age, 'gender': gender, 'weight': weight, 'height': height}

        return redirect(url_for('Workout_Logging'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = user_profiles.get(username)
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('Workout_Logging'))
        return 'Invalid username or password'

    return render_template('login.html')

@app.route('/Workout_Logging', methods=['GET', 'POST'])
@login_required
def Workout_Logging():
    if request.method == 'POST':
        exercise = request.form.get('exercise')
        sets = int(request.form.get('sets'))
        reps = int(request.form.get('reps'))
        weight = float(request.form.get('weight'))

        username = session.get('username')
        if not username:
            return redirect(url_for('login'))

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO workouts (username, exercise, sets, reps, weight)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, exercise, sets, reps, weight))
            conn.commit()

        return redirect(url_for('dashboard'))
    return render_template('Workout_Logging.html')

@app.route('/dashboard')
@login_required
def dashboard():
    username = session.get('username')

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM workouts WHERE username = ?', (username,))
        workouts = cursor.fetchall()

        cursor.execute('SELECT * FROM goals WHERE username = ?', (username,))
        goals = cursor.fetchall()

    return render_template('dashboard.html', workouts=workouts, goals=goals)

@app.route('/create_goal', methods=['POST'])
@login_required
def create_goal():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    goal = request.form.get('goal')
    target = int(request.form.get('target'))

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO goals (username, goal, target)
            VALUES (?, ?, ?)
        ''', (username, goal, target))
        conn.commit()

    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)