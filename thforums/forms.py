from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from thforums.models import User
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from flask_login import current_user
from wtforms.fields import DateField

# form for user registration
class RegistrationForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired(), Length(min=2, max=20)])  # username field
    email = StringField("Email:", validators=[DataRequired(), Email()])  # email field
    password = PasswordField("Password:", validators=[DataRequired()])  # password field
    confirm_password = PasswordField("Confirm Password:", validators=[DataRequired(), EqualTo("password")])  # confirm password field
    submit = SubmitField("Sign Up")  # submit button
    
    # custom validator to check if username is already taken
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already taken!")
    
    # custom validator to check if email is already taken
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already taken!")
        
# form for user login
class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired(), Length(min=2, max=20)])  # username field
    password = PasswordField("Password:", validators=[DataRequired()])  # password field
    remember = BooleanField("Remember Me?")  # remember me checkbox
    submit = SubmitField("Login")  # submit button

# form for updating user profile
class UpdateProfileForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired(), Length(min=2, max=20)])  # username field
    email = StringField("Email:", validators=[DataRequired(), Email()])  # email field
    picture = FileField("Update Profile Picture", validators=[FileAllowed(['jpg', 'png'])])  # profile picture upload
    gender = SelectField("Gender:", choices=[("", "Select"), ("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
    birthdate = DateField("Birthdate:", format='%Y-%m-%d', validators=[Optional()])
    bio = TextAreaField("Bio:", validators=[Length(max=500)])
    submit = SubmitField("Update")  # submit button

    # custom validator to check if username is already taken
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("Username already taken!")

    # custom validator to check if email is already taken
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("Email already taken!")

# form for creating a new thread
class ThreadForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=1, max=100)])  # thread title field
    category = SelectField("Category", choices=[
        ("General Discussion", "General Discussion"),
        ("Looking for Adventurers", "Looking for Adventurers"),
        ("Commissions and Quest", "Commissions and Quest")
    ], validators=[DataRequired()])  # category dropdown
    content = TextAreaField("Content", validators=[DataRequired()])  # thread content field
    tags = StringField("Tags (comma-separated)", validators=[Optional(), Length(max=128)])
    image = FileField("Attach Image", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField("Create Thread")  # submit button

# form for replying to a thread
class ReplyForm(FlaskForm):
    content = TextAreaField("Reply", validators=[DataRequired()])  # reply content field
    image = FileField("Attach Image", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField("Post Reply")  # submit button

# form for editing a thread
class EditThreadForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=1, max=100)])
    content = TextAreaField("Content", validators=[DataRequired()])
    tags = StringField("Tags (comma-separated)", validators=[Optional(), Length(max=128)])
    image = FileField("Change Image", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField("Update Thread")

# form for editing replies
class EditReplyForm(FlaskForm):
    content = TextAreaField("Reply", validators=[DataRequired()])
    image = FileField("Change Image", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField("Update Reply")

# form for searches
class SearchForm(FlaskForm):
    search = StringField("Search:", validators=[Optional(), Length(max=50)])
    submit = SubmitField("Search")

#form for guild registration
class RegisterGuild(FlaskForm):
    guild_name = StringField("Guild_Name:", validators=[DataRequired(), Length(min=2, max=20)])  # guild_name field
    content = StringField("What's your guild about?:", validators=[DataRequired(), Email()])  # content field
    submit = SubmitField("Sign Up")  # submit button

# form for editing guilds
class EditGuildForm(FlaskForm):
    guild_name = StringField("Guild Name", validators=[DataRequired(), Length(min=2, max=50)])
    content = TextAreaField("Description", validators=[DataRequired(), Length(max=500)])
    submit = SubmitField("Update Guild")

# form for transferring guild ownership
class TransferGuildOwnershipForm(FlaskForm):
    new_owner = SelectField("Transfer Ownership To", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Transfer Ownership")

# form for joining and leaving guilds
class JoinGuildForm(FlaskForm):
    submit = SubmitField("Join Guild")

class LeaveGuildForm(FlaskForm):
    submit = SubmitField("Leave Guild")

# form for password recovery
class PasswordRecoveryForm(FlaskForm):
    email = StringField("Email:", validators=[DataRequired(), Email()])
    new_password = PasswordField("New Password:", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm New Password:", validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField("Reset Password")

# form for posting in the guild
class GuildPostForm(FlaskForm):
    content = TextAreaField("Message", validators=[DataRequired()])
    image = FileField("Attach Image", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField("Post")