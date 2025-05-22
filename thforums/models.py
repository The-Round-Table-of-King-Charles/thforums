from datetime import datetime
from thforums import db, login_manager
from flask_login import UserMixin

# this function is used by flask-login to load a user by their id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# create Guild Table
class Guild(db.Model):
    id = db.Column(db.Integer, primary_key=True) #guild id
    guild_name = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False) #guild description
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) #time created
    user_id = db.Column(db.Integer, db.ForeignKey("user.id")) #foreign key for users
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    members = db.relationship("User", backref="guild", lazy=True, foreign_keys="User.guild_id")

    def is_owner(self, user):
        return self.owner_id == user.id

    def member_count(self):
        return len(self.members)

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
    exp = db.Column(db.Integer, nullable=False, default=0)  # exp for user, default 0
    level = db.Column(db.Integer, nullable=False, default=1)  # user level, default 1
    commends_received = db.relationship("Commend", backref="user_target", lazy=True, primaryjoin="User.id==Commend.user_id_target")
    guild_id = db.Column(db.Integer, db.ForeignKey("guild.id"), nullable=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

    def commend_count(self):
        return len([c for c in self.commends_received if c.user_id_target == self.id])

    def is_commended_by(self, user):
        return any(c.user_id == user.id for c in self.commends_received if c.user_id_target == self.id)

    def required_exp_for_next_level(self):
        return 100 * self.level

    def add_exp(self, amount):
        self.exp += amount
        leveled_up = False
        while self.exp >= self.required_exp_for_next_level():
            self.exp -= self.required_exp_for_next_level()
            self.level += 1
            leveled_up = True
        return leveled_up

    def exp_progress(self):
        # returns (current_exp, required_exp) for progress bar
        return self.exp, self.required_exp_for_next_level()

# association table for many-to-many relationship between Thread and Tag
thread_tags = db.Table(
    'thread_tags',
    db.Column('thread_id', db.Integer, db.ForeignKey('thread.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    threads = db.relationship('Thread', secondary=thread_tags, back_populates='tags')

    def __repr__(self):
        return f"Tag('{self.name}')"


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
    commends = db.relationship("Commend", backref="thread", lazy=True, primaryjoin="Thread.id==Commend.thread_id")
    tags = db.relationship('Tag', secondary=thread_tags, back_populates='threads')
    image_file = db.Column(db.String(128))  # filename of uploaded image (nullable)
    quest = db.relationship('Quest', backref='thread', uselist=False, lazy='joined')

    def __repr__(self):
        return f"Thread('{self.title}', '{self.date_posted}')"

    def commend_count(self):
        return len([c for c in self.commends if c.thread_id == self.id])

    def is_commended_by(self, user):
        return any(c.user_id == user.id for c in self.commends if c.thread_id == self.id)

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
    commends = db.relationship("Commend", backref="reply", lazy=True, primaryjoin="Reply.id==Commend.reply_id")
    image_file = db.Column(db.String(128))  # filename of uploaded image (nullable)

    def __repr__(self):
        return f"Reply('{self.content[:20] if self.content else ''}', '{self.date_posted}')"

    def commend_count(self):
        return len([c for c in self.commends if c.reply_id == self.id])

    def is_commended_by(self, user):
        return any(c.user_id == user.id for c in self.commends if c.reply_id == self.id)

# commend model for well, commending a.k.a liking system
class Commend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey("thread.id"), nullable=True)
    reply_id = db.Column(db.Integer, db.ForeignKey("reply.id"), nullable=True)
    user_id_target = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)  # for user-to-user commend

    __table_args__ = (
        db.UniqueConstraint('user_id', 'thread_id', name='unique_user_thread_commend'),
        db.UniqueConstraint('user_id', 'reply_id', name='unique_user_reply_commend'),
        db.UniqueConstraint('user_id', 'user_id_target', name='unique_user_user_commend'),
    )

# notification model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(32), nullable=False)  # e.g., 'reply', 'commend', 'mention'
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))

class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), unique=True, nullable=False)
    completer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default="open")  # open, accepted, completed

    completer = db.relationship("User", foreign_keys=[completer_id])
