from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
import os

# initialize flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = 'aa56904776ed5bafe4537348b65e1bf5'  # secret key for security purposes
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"  # database configuration

# initialize extensions
db = SQLAlchemy(app)  # database instance
bcrypt = Bcrypt(app)  # bcrypt for password hashing
login_manager = LoginManager(app)  # login manager for user authentication
login_manager.login_view = "login"  # redirect to login page if not authenticated
login_manager.login_message_category = "info"  # flash message category for login

from thforums.models import Notification

# create database if not seen on the instance folder
db_path = os.path.join(app.instance_path, 'database.db')
if not os.path.exists(db_path):
    from thforums import models
    with app.app_context():
        db.create_all()

# for notifications
@app.context_processor
def inject_notifications():
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).limit(20).all()
        unread_notifications = Notification.query.filter_by(user_id=current_user.id, read=False).all()
        return dict(notifications=notifications, unread_notifications=unread_notifications)
    return dict(notifications=[], unread_notifications=[])

# import routes to register them with the app
from thforums import routes