from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config["SECRET_KEY"] = 'aa56904776ed5bafe4537348b65e1bf5'

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

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home", posts=posts)
    
@app.route("/about")
def about():
    return render_template("about.html", title="About")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "charles@gmail.com" and form.password.data == "password":
            flash(f"Logged in successfully", "success")
            return redirect(url_for("home"))
        else:
            flash(f"Wrong credentials", "error")
    return render_template("login.html", title="Login", form=form)
    
@app.route("/register", methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created successfully", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)
    
if __name__ == "__main__":
    app.run(debug=True)