from flask import Flask, render_template, url_for

app = Flask(__name__)

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
    
if __name__ == "__main__":
    app.run(debug=True)