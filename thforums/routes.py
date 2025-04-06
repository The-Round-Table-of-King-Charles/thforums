import os

from flask import render_template, url_for, flash, redirect, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from thforums import app, db, bcrypt
from PIL import Image

# it has to be thforums.<module> because we are in a package under the thforums folder
from thforums.forms import RegistrationForm, LoginForm, UpdateProfileForm
from thforums.models import User, Post # import from models.py

# mock database
posts = [
    {   "author": "Charles Arvin",
        "title": "Looking for coins",
        "content": "I am looking for some coins. Please help!",
        "date_posted": "3/20/2025"
    },
    {   "author": "Carl Melo",
        "title": "Billie Eillish is awesome, change my mind",
        "content": "Spoilers, but nothing can change my mind",
        "date_posted": "3/21/2025"
    },
    {   "author": "Charles Arvin",
        "title": "Found some coins",
        "content": "Check out these coins I found!",
        "date_posted": "3/21/2025"
    },
]

def save_picture(form_picture):
    random_hex = os.urandom(8).hex()
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    # open the image
    i = Image.open(form_picture)

    # crop the image to a square
    width, height = i.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    i = i.crop((left, top, right, bottom))

    # resize the cropped image to the desired size
    output_size = (125, 125)
    i = i.resize(output_size)

    # save the image
    i.save(picture_path)

    # return the filename
    return picture_fn

# website routes
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home", posts=posts)
    
@app.route("/about")
def about():
    return render_template("about.html", title="About")
    
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", title="Profile")  # Removed unused posts parameter

@app.route("/profile/update", methods=["GET", "POST"])
@login_required
def update_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your profile has been updated!", "success")
        return redirect(url_for("profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("update_profile.html", title="Update Profile", image_file=image_file, form=form)

# authentication routes, might put this on a seperate file
@app.route("/register", methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit(): # validation means if lahat ng entry sa forms is valid after submit
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit(): # validation means if lahat ng entry sa forms is valid after submit
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            flash(f"Logged in successfully!", "success")  # Changed flash category to "success"
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash(f"Wrong credentials", "error")
    return render_template("login.html", title="Login", form=form)
    
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))