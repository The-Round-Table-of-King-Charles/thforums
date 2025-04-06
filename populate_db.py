# galing sa copilot to add entries sa database, please tinatamad ako

from thforums import app, db
from thforums.models import User, Thread
from flask import Flask
from random import choice
from faker import Faker

fake = Faker()

# Predefined categories
categories = ["General Discussion", "Looking for Adventurers", "Commissions and Quest"]

# Function to populate the database
def populate_threads(num_threads=50):
    with app.app_context():
        # Get a random user to assign as the author
        users = User.query.all()
        if not users:
            print("No users found in the database. Please register a user first.")
            return

        for _ in range(num_threads):
            title = fake.sentence(nb_words=6)
            content = fake.paragraph(nb_sentences=5)
            category = choice(categories)
            author = choice(users)

            thread = Thread(title=title, content=content, category=category, author=author)
            db.session.add(thread)

        db.session.commit()
        print(f"Successfully added {num_threads} threads to the database.")

# Run the script
if __name__ == "__main__":
    populate_threads(num_threads=50)  # Change the number to add more threads