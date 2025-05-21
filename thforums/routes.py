import os
from werkzeug.utils import secure_filename
import secrets

from flask import render_template, url_for, flash, redirect, request, current_app, g, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from thforums import app, db, bcrypt
from PIL import Image
from datetime import datetime
from thforums.models import User, Thread, Reply, Commend, Tag, Notification, Guild

# import forms and models
from thforums.forms import RegistrationForm, LoginForm, UpdateProfileForm, ThreadForm, ReplyForm, EditThreadForm, EditReplyForm, SearchForm, RegisterGuild, EditGuildForm, TransferGuildOwnershipForm, JoinGuildForm, LeaveGuildForm, PasswordRecoveryForm

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

def save_post_image(form_image):
    if not form_image:
        return None
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(secure_filename(form_image.filename))
    image_fn = random_hex + f_ext
    image_path = os.path.join(current_app.root_path, 'static', 'post_images', image_fn)
    form_image.save(image_path)
    return image_fn

def get_or_create_tags(tag_string):
    tag_names = [t.strip().lower() for t in tag_string.split(',') if t.strip()]
    tags = []
    for name in tag_names:
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
        tags.append(tag)
    return tags

# route for the landing page
@app.route("/")
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template("home.html", title="Home")

# route for the home page
@app.route("/home")
@login_required
def home():
    page = request.args.get("page", 1, type=int)
    threads = Thread.query.order_by(Thread.date_posted.desc()).paginate(page=page, per_page=15)
    notifications = []
    user_threads = []
    if current_user.is_authenticated:
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).limit(3).all()
        user_threads = Thread.query.filter_by(author=current_user).order_by(Thread.date_posted.desc()).limit(3).all()
    return render_template(
        "dashboard.html",
        title="Dashboard",
        threads=threads,
        notifications=notifications,
        user_threads=user_threads
    )

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
    form = ThreadForm()
    if form.validate_on_submit():
        image_file = None
        if form.image.data:
            image_file = save_post_image(form.image.data)
        thread = Thread(
            title=form.title.data,
            category=form.category.data,
            content=form.content.data,
            author=current_user,
            image_file=image_file
        )
        # handle tags
        if form.tags.data:
            thread.tags = get_or_create_tags(form.tags.data)
        db.session.add(thread)
        # award exp for creating a thread
        leveled_up = current_user.add_exp(20)
        db.session.commit()
        flash("Your thread has been created!", "success")
        if leveled_up:
            flash(f"You leveled up! You are now level {current_user.level}.", "success")
        return redirect(url_for("category_threads", category=form.category.data))
    return render_template("create_thread.html", title="New Thread", form=form)

# route to view threads in a specific category
@app.route("/forums/<string:category>", methods=["GET"])
def category_threads(category):
    page = request.args.get("page", 1, type=int)  # get the current page number
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
        image_file = None
        if form.image.data:
            image_file = save_post_image(form.image.data)
        reply = Reply(content=form.content.data, user_id=current_user.id, thread=thread, image_file=image_file)
        db.session.add(reply)
        # award exp for replying
        leveled_up = current_user.add_exp(5)
        db.session.commit()
        flash("Your reply has been posted!", "success")
        if leveled_up:
            flash(f"You leveled up! You are now level {current_user.level}.", "success")
        create_reply_notification(reply)
        return redirect(url_for("view_thread", thread_id=thread.id))
    
    page = request.args.get("page", 1, type=int)  # get the current page number
    replies = Reply.query.filter_by(thread_id=thread.id).order_by(Reply.date_posted.asc()).paginate(page=page, per_page=5)
    return render_template("thread.html", title=thread.title, thread=thread, form=form, replies=replies)

# route to view all forums
@app.route("/forums", methods=["GET", "POST"])
def forums():
    form = SearchForm()
    search_query = ""
    tag_search = request.args.get("tag", "", type=str)
    if form.validate_on_submit():
        search_query = form.search.data
    elif request.method == "GET":
        search_query = request.args.get("search", "", type=str)

    page = request.args.get("page", 1, type=int)
    categories = ["General Discussion", "Looking for Adventurers", "Commissions and Quest"]

    threads = None
    latest_threads = None

    if tag_search:
        tag = Tag.query.filter_by(name=tag_search.lower()).first()
        if tag:
            threads = Thread.query.filter(Thread.tags.contains(tag)).order_by(Thread.date_posted.desc()).paginate(page=page, per_page=10)
        else:
            threads = None
        search_query = ""
    elif search_query:
        threads = Thread.query.filter(
            (Thread.title.ilike(f"%{search_query}%")) |
            (Thread.tags.any(Tag.name.ilike(f"%{search_query.lower()}%")))
        ).order_by(Thread.date_posted.desc()).paginate(page=page, per_page=10)
        latest_threads = None
    else:
        threads = None
        latest_threads = {category: Thread.query.filter_by(category=category).order_by(Thread.date_posted.desc()).limit(5).all() for category in categories}

    return render_template(
        "forum.html",
        title="Forums",
        categories=categories,
        form=form,
        threads=threads,
        search_query=search_query,
        latest_threads=latest_threads
    )

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
        user = User.query.filter_by(username=form.username.data).first()
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
        # update tags
        thread.tags = get_or_create_tags(form.tags.data) if form.tags.data else []
        if form.image.data:
            thread.image_file = save_post_image(form.image.data)
        db.session.commit()
        flash("Thread updated successfully!", "success")
        return redirect(url_for("view_thread", thread_id=thread.id))
    elif request.method == "GET":
        form.title.data = thread.title
        form.content.data = thread.content
        form.tags.data = ', '.join([tag.name for tag in thread.tags])
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
        if form.image.data:
            reply.image_file = save_post_image(form.image.data)
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
    # Show only 5 users per page
    if search_query:
        users = User.query.filter(User.username.ilike(f"%{search_query}%")).paginate(page=page, per_page=5)
    else:
        users = User.query.paginate(page=page, per_page=5)
    # get top 3 users by level, then exp
    top_users = User.query.order_by(User.level.desc(), User.exp.desc()).limit(3).all()
    return render_template(
        "list_users.html",
        title="Users",
        users=users,
        form=form,
        search_query=search_query,
        top_users=top_users
    )

# sidebar
@app.context_processor
def inject_sidebar_user():
    sidebar_exp = None
    sidebar_level = None
    sidebar_exp_required = None
    if current_user.is_authenticated:
        sidebar_exp = current_user.exp
        sidebar_level = current_user.level
        sidebar_exp_required = current_user.required_exp_for_next_level()
    return {
        'sidebar_exp': sidebar_exp,
        'sidebar_level': sidebar_level,
        'sidebar_exp_required': sidebar_exp_required
    }

# guild route
@app.route("/create_guild", methods=["POST"])
@login_required
def create_guild():
    form = RegisterGuild()
    if form.validate_on_submit():  # validate form inputs
        guild = Guild(guild_name=form.guildname.data, content=form.description.data)
        db.session.add(guild)
        db.session.commit()
        flash(f"Guild Created!")
    return render_template("create_guild.html", title="Create Guild", form=form)

# commend or uncommend a thread
@app.route("/commend/thread/<int:thread_id>", methods=["POST"])
@login_required
def commend_thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    commend = Commend.query.filter_by(user_id=current_user.id, thread_id=thread_id).first()
    if commend:
        db.session.delete(commend)
        db.session.commit()
        return jsonify({"commended": False, "count": thread.commend_count()})
    else:
        new_commend = Commend(user_id=current_user.id, thread_id=thread_id)
        db.session.add(new_commend)
        db.session.commit()
        create_thread_commend_notification(thread, current_user)
        return jsonify({"commended": True, "count": thread.commend_count()})

# commend or uncommend a reply
@app.route("/commend/reply/<int:reply_id>", methods=["POST"])
@login_required
def commend_reply(reply_id):
    reply = Reply.query.get_or_404(reply_id)
    commend = Commend.query.filter_by(user_id=current_user.id, reply_id=reply_id).first()
    if commend:
        db.session.delete(commend)
        db.session.commit()
        return jsonify({"commended": False, "count": reply.commend_count()})
    else:
        new_commend = Commend(user_id=current_user.id, reply_id=reply_id)
        db.session.add(new_commend)
        db.session.commit()
        return jsonify({"commended": True, "count": reply.commend_count()})

# commend or uncommend a user
@app.route("/commend/user/<int:user_id>", methods=["POST"])
@login_required
def commend_user(user_id):
    """Commend or uncommend a user. Returns JSON with new commend state and count."""
    if user_id == current_user.id:
        return jsonify({"error": "You cannot commend yourself."}), 400
    user = User.query.get_or_404(user_id)
    commend = Commend.query.filter_by(user_id=current_user.id, user_id_target=user_id).first()
    if commend:
        db.session.delete(commend)
        db.session.commit()
        return jsonify({"commended": False, "count": user.commend_count()})
    else:
        new_commend = Commend(user_id=current_user.id, user_id_target=user_id)
        db.session.add(new_commend)
        db.session.commit()
        return jsonify({"commended": True, "count": user.commend_count()})

# view threads by tag
@app.route("/tag/<string:tag_name>")
def threads_by_tag(tag_name):
    """Display threads associated with a specific tag."""
    tag = Tag.query.filter_by(name=tag_name.lower()).first_or_404()
    page = request.args.get("page", 1, type=int)
    threads = Thread.query.filter(Thread.tags.contains(tag)).order_by(Thread.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template("tag_threads.html", title=f"Tag: {tag.name}", tag=tag, threads=threads)

# mark all notifications as read
@app.route('/notifications/mark_read', methods=['POST'])
@login_required
def mark_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, read=False).update({'read': True})
    db.session.commit()
    return jsonify({'status': 'ok'})

@app.route('/notifications/delete_all', methods=['POST'])
@login_required
def delete_all_notifications():
    Notification.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    # Optionally return JSON for AJAX
    return jsonify({'success': True})

# notification helper functions
def create_reply_notification(reply):
    thread = Thread.query.get(reply.thread_id)
    if thread and thread.user_id != reply.user_id:
        notif = Notification(
            user_id=thread.user_id,
            type='reply',
            message=f'<a href="{url_for("view_thread", thread_id=thread.id)}">Your thread</a> received a new reply.',
        )
        db.session.add(notif)
        db.session.commit()

def create_thread_commend_notification(thread, commender):
    if thread.user_id != commender.id:
        notif = Notification(
            user_id=thread.user_id,
            type='commend',
            message=f'<a href="{url_for("profile", user_id=commender.id)}">{commender.username}</a> commended your thread "<a href="{url_for("view_thread", thread_id=thread.id)}">{thread.title}</a>".',
        )
        db.session.add(notif)
        db.session.commit()

@app.route("/guild")
@login_required
def guild_main():
    if not current_user.guild:
        return redirect(url_for('guild_list'))
    guild = current_user.guild
    members = User.query.filter_by(guild_id=guild.id).all()
    return render_template("guild_main.html", title="Guild", guild=guild, members=members)

@app.route("/guilds")
@login_required
def guild_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    if search:
        guilds = Guild.query.filter(Guild.guild_name.ilike(f"%{search}%")).paginate(page=page, per_page=10)
    else:
        guilds = Guild.query.paginate(page=page, per_page=10)
    return render_template("guild_list.html", title="Guilds", guilds=guilds)

@app.route("/guild/create", methods=["GET", "POST"])
@login_required
def guild_create():
    if current_user.guild:
        flash("You are already in a guild.", "warning")
        return redirect(url_for('guild_main'))
    form = EditGuildForm()
    if form.validate_on_submit():
        guild = Guild(guild_name=form.guild_name.data, content=form.content.data, owner_id=current_user.id)
        db.session.add(guild)
        db.session.commit()
        current_user.guild_id = guild.id
        db.session.commit()
        flash("Guild created!", "success")
        return redirect(url_for('guild_main'))
    return render_template("create_guild.html", title="Create Guild", form=form)

@app.route("/guild/join/<int:guild_id>", methods=["POST"])
@login_required
def guild_join(guild_id):
    if current_user.guild:
        flash("You are already in a guild.", "warning")
        return redirect(url_for('guild_main'))
    guild = Guild.query.get_or_404(guild_id)
    current_user.guild_id = guild.id
    db.session.commit()
    flash(f"You joined {guild.guild_name}!", "success")
    return redirect(url_for('guild_main'))

@app.route("/guild/leave", methods=["POST"])
@login_required
def guild_leave():
    if not current_user.guild:
        flash("You are not in a guild.", "warning")
        return redirect(url_for('guild_list'))
    if current_user.guild.owner_id == current_user.id:
        flash("Owner cannot leave the guild. Transfer ownership first.", "danger")
        return redirect(url_for('guild_main'))
    current_user.guild_id = None
    db.session.commit()
    flash("You left the guild.", "success")
    return redirect(url_for('guild_list'))

@app.route("/guild/edit", methods=["GET", "POST"])
@login_required
def guild_edit():
    guild = current_user.guild
    if not guild or guild.owner_id != current_user.id:
        flash("You are not the owner.", "danger")
        return redirect(url_for('guild_main'))
    form = EditGuildForm(obj=guild)
    if form.validate_on_submit():
        guild.guild_name = form.guild_name.data
        guild.content = form.content.data
        db.session.commit()
        flash("Guild updated.", "success")
        return redirect(url_for('guild_main'))
    return render_template("edit_guild.html", title="Edit Guild", form=form, guild=guild)

@app.route("/guild/transfer", methods=["GET", "POST"])
@login_required
def guild_transfer():
    guild = current_user.guild
    if not guild or guild.owner_id != current_user.id:
        flash("You are not the owner.", "danger")
        return redirect(url_for('guild_main'))
    form = TransferGuildOwnershipForm()
    form.new_owner.choices = [(m.id, m.username) for m in guild.members if m.id != current_user.id]
    if form.validate_on_submit():
        guild.owner_id = form.new_owner.data
        db.session.commit()
        flash("Ownership transferred.", "success")
        return redirect(url_for('guild_main'))
    return render_template("transfer_guild.html", title="Transfer Guild Ownership", form=form, guild=guild)

@app.route("/guild/remove_member/<int:user_id>", methods=["POST"])
@login_required
def guild_remove_member(user_id):
    guild = current_user.guild
    if not guild or guild.owner_id != current_user.id:
        flash("You are not the owner.", "danger")
        return redirect(url_for('guild_main'))
    member = User.query.get_or_404(user_id)
    if member.guild_id != guild.id or member.id == guild.owner_id:
        flash("Invalid operation.", "danger")
        return redirect(url_for('guild_main'))
    member.guild_id = None
    db.session.commit()
    flash("Member removed.", "success")
    return redirect(url_for('guild_main'))

@app.context_processor
def inject_user_guild():
    if current_user.is_authenticated and current_user.guild:
        return dict(user_guild=current_user.guild)
    return dict(user_guild=None)

# 404 error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title="Page Not Found"), 404

# 500 error page
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', title="Server Error"), 500

@app.route("/recover_password", methods=["GET", "POST"])
def recover_password():
    form = PasswordRecoveryForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            hashed_pw = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            user.password = hashed_pw
            db.session.commit()
            flash("Password updated! You can now log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("No account found with that email.", "error")
    return render_template("recover_password.html", form=form, title="Recover Password")