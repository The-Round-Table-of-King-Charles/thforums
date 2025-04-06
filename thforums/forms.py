from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from thforums.models import User
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user

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
    email = StringField("Email:", validators=[DataRequired(), Email()])  # email field
    password = PasswordField("Password:", validators=[DataRequired()])  # password field
    remember = BooleanField("Remember Me?")  # remember me checkbox
    submit = SubmitField("Login")  # submit button

# form for updating user profile
class UpdateProfileForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired(), Length(min=2, max=20)])  # username field
    email = StringField("Email:", validators=[DataRequired(), Email()])  # email field
    picture = FileField("Update Profile Picture", validators=[FileAllowed(['jpg', 'png'])])  # profile picture upload
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
    submit = SubmitField("Create Thread")  # submit button

# form for replying to a thread
class ReplyForm(FlaskForm):
    content = TextAreaField("Reply", validators=[DataRequired()])  # reply content field
    submit = SubmitField("Post Reply")  # submit button