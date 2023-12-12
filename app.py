import sys
sys.path.append('/home/tarthur/fitnexapp/gaol')
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_pymongo import PyMongo
import bcrypt


app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/your_database_name'
app.config['SECRET_KEY'] = 'your-secret-key'

mongo = PyMongo(app)
login_manager = LoginManager(app)

# User class for Flask-Login
class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    user = mongo.db.users.find_one({'_id': user_id})
    if user:
        user_obj = User()
        user_obj.id = user['_id']
        return user_obj
    return None

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get user input from the registration form
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the user already exists
        if mongo.db.users.find_one({'username': username}):
            return 'User already exists'

        # Hash the password before storing it (use a secure method in production)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Add the user to the MongoDB collection
        user_id = mongo.db.users.insert_one({
            'username': username,
            'password': hashed_password
        }).inserted_id

        # Create a User object for Flask-Login
        user_obj = User()
        user_obj.id = user_id

        # Log in the user
        login_user(user_obj)

        return redirect(url_for('workout_logging'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = mongo.db.users.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Create a User object for Flask-Login
            user_obj = User()
            user_obj.id = user['_id']

            # Log in the user
            login_user(user_obj)

            return redirect(url_for('workout_logging'))
        return 'Invalid username or password'

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Workout Logging route
@app.route('/workout_logging', methods=['GET', 'POST'])
@login_required
def workout_logging():
    if request.method == 'POST':
        exercise = request.form.get('exercise')
        sets = int(request.form.get('sets'))
        reps = int(request.form.get('reps'))
        weight = float(request.form.get('weight'))

        # Retrieve the current logged-in user
        username = current_user.id

        # Add the workout to the MongoDB collection
        mongo.db.workouts.insert_one({
            'username': username,
            'exercise': exercise,
            'sets': sets,
            'reps': reps,
            'weight': weight
        })

        return redirect(url_for('dashboard'))

    return render_template('workout_logging.html')

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    # Retrieve the current logged-in user
    username = current_user.id

    # Retrieve the user's goals from the database
    goals = mongo.db.goals.find({'username': username})

    # Retrieve the user's progress from the database
    progress = mongo.db.goals.find({'username': username}, {'progress_sets': 1, 'progress_reps': 1, 'progress_weight': 1})

    return render_template('dashboard.html', goals=goals, progress=progress)

@app.route('/create_goal', methods=['POST'])
@login_required
def create_goal():
    # Retrieve the goal data from the request form
    goal_name = request.form.get('goal_name')
    description = request.form.get('description')

    # Validate and sanitize the input data
    if not goal_name or not description:
        return 'Goal name and description are required'

    # Retrieve the current logged-in user
    username = current_user.id

    # Save the goal data to the database
    goal_id = mongo.db.goals.insert_one({
        'username': username,
        'goal_name': goal_name,
        'description': description
    }).inserted_id

    return redirect(url_for('dashboard'))

@app.route('/edit_goal/<goal_id>', methods=['GET', 'POST'])
@login_required
def edit_goal(goal_id):
    # Retrieve the goal from the database
    goal = mongo.db.goals.find_one({'_id': ObjectId(goal_id)})

    if not goal:
        return 'Goal not found'

    # Check if the goal belongs to the current user
    if goal['username'] != current_user.id:
        return 'Unauthorized access'

    if request.method == 'POST':
        # Retrieve the updated goal data from the request form
        goal_name = request.form.get('goal_name')
        description = request.form.get('description')

        # Validate and sanitize the input data
        if not goal_name or not description:
            return 'Goal name and description are required'

        # Update the goal data in the database
        mongo.db.goals.update_one({'_id': ObjectId(goal_id)}, {'$set': {'goal_name': goal_name, 'description': description}})

        return redirect(url_for('dashboard'))
    
    return render_template('edit_goal.html', goal=goal)

@app.route('/update_progress/<goal_id>', methods=['POST'])
@login_required
def update_progress(goal_id):
    # Retrieve the goal from the database
    goal = mongo.db.goals.find_one({'_id': ObjectId(goal_id)})

    if not goal:
        return 'Goal not found'

    # Check if the goal belongs to the current user
    if goal['username'] != current_user.id:
        return 'Unauthorized access'

    # Retrieve the progress data from the request form
    sets = int(request.form.get('sets'))
    reps = int(request.form.get('reps'))
    weight = float(request.form.get('weight'))
    photo = request.files.get('photo')

    # Perform any required validation or processing of the progress data

    # Update the goal's progress in the database
    mongo.db.goals.update_one(
        {'_id': ObjectId(goal_id)},
        {'$set': {'progress_sets': sets, 'progress_reps': reps, 'progress_weight': weight}}
    )

    # Save the progress photo if provided
    if photo:
        # Save the file to a designated location or database field

    # Redirect the user back to the dashboard
     return redirect(url_for('dashboard'))
    

if __name__ == '__main__':
    app.run(debug=True)