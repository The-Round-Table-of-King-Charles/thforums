from flask import Flask 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = 'aa56904776ed5bafe4537348b65e1bf5' # Required by certain imports for security reasons daw, ewan
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

from thforums import routes