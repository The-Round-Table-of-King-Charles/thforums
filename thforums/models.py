from datetime import datetime
from thforums import db, login_manager
from flask_login import UserMixin

# this function is used by flask-login to load a user by their id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# create Guild Table
# Add exp attribute to users

# user model represents a registered user in the database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # unique id for each user
    username = db.Column(db.String(20), unique=True, nullable=False)  # username must be unique
    email = db.Column(db.String(120), unique=True, nullable=False)  # email must be unique
    image_file = db.Column(db.String(20), nullable=False, default="default.png")  # profile picture
    password = db.Column(db.String(60), nullable=False)  # hashed password
    gender = db.Column(db.String(10), nullable=True)  # gender field
    birthdate = db.Column(db.Date, nullable=True)  # birthdate field
    bio = db.Column(db.Text, nullable=True)  # bio field
    threads = db.relationship("Thread", backref="author", lazy=True)  # relationship to threads created by the user
    replies = db.relationship("Reply", backref="author", lazy=True)  # relationship to replies made by the user
    exp = db.Column(db.Integer, nullable=True) #exp for user
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
        
# thread model represents a forum thread
class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # unique id for each thread
    title = db.Column(db.String(100), nullable=False)  # thread title
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # timestamp of thread creation
    content = db.Column(db.Text, nullable=False)  # thread content
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # foreign key linking to the user who created the thread
    category = db.Column(db.String(50), nullable=False)  # category of the thread
    replies = db.relationship("Reply", backref="thread", lazy=True)  # relationship to replies in the thread
    edited = db.Column(db.Boolean, default=False)  # flag to indicate if the thread was edited
    last_edited = db.Column(db.DateTime)  # timestamp of the last edit

    def __repr__(self):
        return f"Thread('{self.title}', '{self.date_posted}')"

# reply model represents a reply to a thread
class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # unique id for each reply
    content = db.Column(db.Text, nullable=False)  # reply content
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # timestamp of reply creation
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # foreign key linking to the user who made the reply
    thread_id = db.Column(db.Integer, db.ForeignKey("thread.id"), nullable=False)  # foreign key linking to the thread being replied to
    edited = db.Column(db.Boolean, default=False)  # flag to indicate if the reply was edited
    last_edited = db.Column(db.DateTime)  # timestamp of the last edit
    deleted = db.Column(db.Boolean, default=False)  # flag to indicate if the reply is deleted

    def __repr__(self):
        return f"Reply('{self.content[:20] if self.content else ''}', '{self.date_posted}')"
    
class Guild():
     id = db.Column(db.Integer, primary_key=True)
