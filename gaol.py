from flask import Flask, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask_pymongo import PyMongo
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/your_database_name'
app.config['SECRET_KEY'] = 'your-secret-key'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'your-mail-server'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'

mail = Mail(app)
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

@app.route('/create_goal', methods=['POST'])
@login_required
def create_goal():
    user_id = current_user.id  # Get the current user's ID

    # Get goal data from the form
    description = request.form.get('description')
    target_date = request.form.get('targetDate')
    target_weight = float(request.form.get('targetWeight'))

    # Validate and sanitize input data
    if not (description and target_date and isinstance(target_weight, float)):
        return 'Invalid input data'

    # Save the goal data to the database, associating it with the respective user
    goal_id = mongo.db.goals.insert_one({
        'user_id': user_id,
        'description': description,
        'target_date': target_date,
        'target_weight': target_weight
    }).inserted_id

    # Send a goal reminder email
    send_goal_reminder_email(current_user, description, target_date)

    return redirect(url_for('dashboard'))

def send_goal_reminder_email(user, goal_description, target_date):
    msg = Message('Goal Reminder', sender='your-email@example.com', recipients=[user.email])
    msg.body = f"Hi {user.username},\n\nThis is a reminder for your goal: {goal_description} with a target date of {target_date}.\n\nStay motivated!\n\nYour Goal Tracking App"
    mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True)