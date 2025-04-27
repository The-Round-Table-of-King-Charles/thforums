from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
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
migrate = Migrate(app, db)

# initialize database if there is no current one
if not os.path.exists("database.db"):
    with app.app_context():
        db.create_all()

# migrates data if there are changes to models.py
if not os.path.exists("migrations"):
    os.system("flask db init")
    os.system("flask db migrate -m 'Initial migration'")
    os.system("flask db upgrade")

# import routes to register them with the app
from thforums import routes