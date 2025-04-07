import os

from flask import render_template, url_for, flash, redirect, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from thforums import app, db, bcrypt
from PIL import Image
from datetime import datetime

# import forms and models
from thforums.forms import RegistrationForm, LoginForm, UpdateProfileForm, ThreadForm, ReplyForm, EditThreadForm, EditReplyForm, SearchForm
from thforums.models import User, Thread, Reply

# helper function to save profile pictures
def save_picture(form_picture):
    random_hex = os.urandom(8).hex()  # generate a random filename
    _, f_ext = os.path.splitext(form_picture.filename)  # get the file extension
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

    # resize the cropped image
    output_size = (125, 125)
    i = i.resize(output_size)

    # save the image
    i.save(picture_path)

    # return the filename
    return picture_fn

# route for the home page
@app.route("/")
@app.route("/home")
def home():
    categories = ["General Discussion", "Looking for Adventurers", "Commissions and Quest"]  # predefined categories
    # latest_threads is a dictionary where each category maps to its latest threads
    latest_threads = {category: Thread.query.filter_by(category=category).order_by(Thread.date_posted.desc()).limit(3).all() for category in categories}
    return render_template("home.html", title="Home", latest_threads=latest_threads)
    
# route for the about page
@app.route("/about")
def about():
    return render_template("about.html", title="About")
    
# route for the user profile page
@app.route("/profile")
@login_required
def profile():
    page = request.args.get("page", 1, type=int)  # get the current page number
    threads = Thread.query.filter_by(author=current_user).order_by(Thread.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("profile.html", title="Profile", threads=threads)

# route to update user profile
@app.route("/profile/update", methods=["GET", "POST"])
@login_required
def update_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)  # save the new profile picture
            current_user.image_file = picture_file
        # update user's profile information
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.gender = form.gender.data
        current_user.birthdate = form.birthdate.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash("Your profile has been updated!", "success")
        return redirect(url_for("profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.gender.data = current_user.gender
        form.birthdate.data = current_user.birthdate
        form.bio.data = current_user.bio
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("update_profile.html", title="Update Profile", image_file=image_file, form=form)

# route to create a new thread
@app.route("/thread/new", methods=["GET", "POST"])
@login_required
def new_thread():
    category = request.args.get("category")  # get the category from the query parameter
    form = ThreadForm()
    if category:
        form.category.data = category  # pre-fill the category if provided
    # if a category is provided in the query parameter, pre-fill the form's category field
    if form.validate_on_submit():
        thread = Thread(title=form.title.data, content=form.content.data, category=form.category.data, author=current_user)
        db.session.add(thread)
        db.session.commit()
        flash("Your thread has been created!", "success")
        return redirect(url_for("category_threads", category=form.category.data))
    return render_template("create_thread.html", title="New Thread", form=form)

# route to view threads in a specific category
@app.route("/forums/<string:category>", methods=["GET"])
def category_threads(category):
    page = request.args.get("page", 1, type=int)  # get the current page number
    # paginate threads to display 10 per page
    threads = Thread.query.filter_by(category=category).order_by(Thread.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template("category.html", title=category, category=category, threads=threads)

# route to view a specific thread and its replies
@app.route("/thread/<int:thread_id>", methods=["GET", "POST"])
def view_thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)  # get the thread or return 404 if not found
    form = ReplyForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You must be logged in to post a reply.", "error")
            return redirect(url_for("login"))
        # if the form is valid, create a new reply and associate it with the thread
        reply = Reply(content=form.content.data, user_id=current_user.id, thread=thread)  # create a new reply
        db.session.add(reply)
        db.session.commit()
        flash("Your reply has been posted!", "success")
        return redirect(url_for("view_thread", thread_id=thread.id))
    
    page = request.args.get("page", 1, type=int)  # get the current page number
    replies = Reply.query.filter_by(thread_id=thread.id).order_by(Reply.date_posted.asc()).paginate(page=page, per_page=5)
    return render_template("thread.html", title=thread.title, thread=thread, form=form, replies=replies)

# route to view all forums
@app.route("/forums", methods=["GET", "POST"])
def forums():
    form = SearchForm()
    search_query = ""
    if form.validate_on_submit():  # handle form submission
        search_query = form.search.data
    elif request.method == "GET":  # handle query parameter for pagination
        search_query = request.args.get("search", "", type=str)
    
    page = request.args.get("page", 1, type=int)  # get the current page number
    categories = ["General Discussion", "Looking for Adventurers", "Commissions and Quest"]  # predefined categories
    
    if search_query:
        threads = Thread.query.filter(Thread.title.ilike(f"%{search_query}%")).order_by(Thread.date_posted.desc()).paginate(page=page, per_page=10)
    else:
        threads = None  # no search results to display
    
    return render_template("forum.html", title="Forums", categories=categories, form=form, threads=threads, search_query=search_query)

# route to register a new user
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:  # check if the user is already logged in
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():  # validate form inputs
        # hash the user's password before saving it to the database
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")  # hash the password
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))  # redirect to login page after registration
    return render_template("register.html", title="Register", form=form)

# route to log in a user
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():  # validate form inputs
        user = User.query.filter_by(email=form.email.data).first()
        # check if the user's credentials are valid
        if user and bcrypt.check_password_hash(user.password, form.password.data):  # check credentials
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            flash(f"Logged in successfully!", "success")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash(f"Wrong credentials", "error")
    return render_template("login.html", title="Login", form=form)
    
# route to log out a user
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

# route to view another user's profile
@app.route("/user/<string:username>")
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)  # get the current page number
    threads = Thread.query.filter_by(author=user).order_by(Thread.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("user_profile.html", title=f"{user.username}'s Profile", user=user, threads=threads)

# route to edit a thread
@app.route("/thread/<int:thread_id>/edit", methods=["GET", "POST"])
@login_required
def edit_thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    if thread.author != current_user:
        flash("You are not authorized to edit this thread.", "error")
        return redirect(url_for("view_thread", thread_id=thread.id))
    form = EditThreadForm()
    if form.validate_on_submit():
        thread.title = form.title.data
        thread.content = form.content.data
        thread.edited = True
        thread.last_edited = datetime.utcnow()
        db.session.commit()
        flash("Thread updated successfully!", "success")
        return redirect(url_for("view_thread", thread_id=thread.id))
    elif request.method == "GET":
        form.title.data = thread.title
        form.content.data = thread.content
    return render_template("edit_thread.html", title="Edit Thread", form=form)

# route to delete a thread
@app.route("/thread/<int:thread_id>/delete", methods=["POST"])
@login_required
def delete_thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    if thread.author != current_user:
        flash("You are not authorized to delete this thread.", "error")
        return redirect(url_for("view_thread", thread_id=thread.id))
    db.session.delete(thread)  # permanently delete the thread
    db.session.commit()
    flash("Thread has been deleted.", "success")
    return redirect(url_for("forums"))

# route to edit a reply
@app.route("/reply/<int:reply_id>/edit", methods=["GET", "POST"])
@login_required
def edit_reply(reply_id):
    reply = Reply.query.get_or_404(reply_id)
    if reply.author != current_user:
        flash("You are not authorized to edit this reply.", "error")
        return redirect(url_for("view_thread", thread_id=reply.thread_id))
    form = EditReplyForm()
    if form.validate_on_submit():
        reply.content = form.content.data
        reply.edited = True
        reply.last_edited = datetime.utcnow()
        db.session.commit()
        flash("Reply updated successfully!", "success")
        return redirect(url_for("view_thread", thread_id=reply.thread_id))
    elif request.method == "GET":
        form.content.data = reply.content
    return render_template("edit_reply.html", title="Edit Reply", form=form)

# route to delete a reply
@app.route("/reply/<int:reply_id>/delete", methods=["POST"])
@login_required
def delete_reply(reply_id):
    reply = Reply.query.get_or_404(reply_id)
    if reply.author != current_user:
        flash("You are not authorized to delete this reply.", "error")
        return redirect(url_for("view_thread", thread_id=reply.thread_id))
    if reply.deleted:
        flash("Reply is already deleted.", "info")
        return redirect(url_for("view_thread", thread_id=reply.thread_id))
    reply.deleted = True  # mark the reply as deleted
    db.session.commit()
    flash("Reply has been deleted.", "success")
    return redirect(url_for("view_thread", thread_id=reply.thread_id))

# route to list all users
@app.route("/users", methods=["GET", "POST"])
def list_users():
    form = SearchForm()
    search_query = ""
    if form.validate_on_submit():  # handle form submission
        search_query = form.search.data
    elif request.method == "GET":  # handle query parameter for pagination
        search_query = request.args.get("search", "", type=str)
    page = request.args.get("page", 1, type=int)
    if search_query:
        users = User.query.filter(User.username.ilike(f"%{search_query}%")).paginate(page=page, per_page=10)
    else:
        users = User.query.paginate(page=page, per_page=10)
    return render_template("list_users.html", title="Users", users=users, form=form, search_query=search_query)

# 404 error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title="Page Not Found"), 404

# 500 error page
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', title="Server Error"), 500

