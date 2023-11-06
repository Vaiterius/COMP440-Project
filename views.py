import random
from datetime import datetime

from flask import Flask, request, render_template, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from mysql.connector import connection

app = Flask(__name__)
app.config["TESTING"] = True
app.config["SECRET_KEY"] = "placeholder"

connection = connection.MySQLConnection(
    user="root", password="", host="127.0.0.1", database="comp440_project"
)

# `dictionary=True` allows queries to return in an easier format:
# e.g. {"username": "foo", "email": "bar", ...}
# instead of ("foo", "bar", ...)
cursor = connection.cursor(dictionary=True)


@app.route("/")
def home():
    """Will list out all the user listings and also the listing form"""
    # Check if user is logged in.
    if not "username" in session:
        return redirect("/login")
    
    # Query for the listings.
    cursor.execute("SELECT * FROM items")
    listings = cursor.fetchall()

    return render_template("index.html", username=session["username"], listings=listings)


@app.route("/registration", methods=["GET", "POST"])
def registration():
    """User account creation"""

    # Forget any cookies.
    # Cookies are for keeping the user logged in.
    session.clear()
    
    # Form submission.
    if request.method == "POST":
        
        # Get and cleanse registration data.
        first_name = request.form.get("firstName").strip()
        last_name = request.form.get("lastName").strip()
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        confirm_password = request.form.get("confirmPassword").strip()

        # Ensure all fields have been entered.
        if not (
            first_name and last_name and username
            and email and password and confirm_password
        ):
            flash("All fields must be filled in!", "error")
            return redirect("/registrtation")

        # Ensure username and email aren't already taken.
        cursor.execute("SELECT username FROM users WHERE username = %s", (username, ))
        if cursor.fetchall():
            flash("Username already taken!", "error")
            return render_template("signup.html"), 400
        
        cursor.execute(f"SELECT email FROM users WHERE email = %s", (email,))
        if cursor.fetchall():
            flash("Email already taken!", "error")
            return render_template("signup.html"), 400

        # Ensure passwords match.
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template("signup.html"), 400
        
        hashed_password = generate_password_hash(password)
        
        # Create user.
        cursor.execute(
            "INSERT INTO users (username, first_name, last_name, email, password) VALUES (%s, %s, %s, %s, %s)",
            (username, first_name, last_name, email, hashed_password)
        )
        connection.commit()

        # Log in user by adding them to the session.
        session["username"] = username
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        session["user_id"] = cursor.fetchone()["user_id"]

        flash("Successfully signed up!", "success")

        return redirect("/")
    
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login to account"""

    # Forget any cookies.
    session.clear()

    if request.method == "POST":

        # Get and cleanse login data.
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()

        # Ensure both email and password have been entered in.
        if not email or not password:
            flash("All fields must be filled in!", "error")
            return render_template("login.html")
        
        # Find if user exists and has matching password.
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

        user = cursor.fetchone()

        if not user:  # Empty result.
            # Credentials do not match.
            flash("No matching account was found", "error")

            return redirect("/login")
        
        if user and check_password_hash(user["password"], password):
            # Log them in.
            session["username"] = user["username"]
            session["user_id"] = user["user_id"]

            flash("Successfully logged in!", "success")

            return redirect("/")

    return render_template("login.html")


# @app.route("/submit_listing", methods=["GET", "POST"])
# def submit_listing():
#     """Submit an item as a listing"""
#     # Check if user is logged in.
#     if not "username" in session:
#         return redirect("/login")
    
#     if request.method == "POST":
#         username: str = session["username"]

#         # TODO Check if the user has already posted 3 items today.
#         # today = datetime.today().date()
#         # cursor.execute("SELECT items_posted FROM users WHERE username = %s", (username,))
#         # items_posted = cursor.fetchone()[0]
#         items_posted: int = 2
#         if items_posted >= 3:
#             flash("You've already posted 3 times today. You can't post more.", "error")

#         # TODO Fetch item inputs.
#         title = request.form.get("title").strip()
#         description = request.form.get("description").strip()
#         category = request.form.get("category").strip()
#         price = float(request.form.get("price"))
#         user_id = 1  # Replace with the actual user's ID

#         # TODO Save the listing into the database.
#         cursor.execute("INSERT INTO products (title, description, category, price, username) VALUES (%s, %s, %s, %s, %s)",(title, description, category, price,username))
#         connection.commit()
        
#         flash("Item posted sucessfully.", "success")

#         # Redirect to same page, essentially "refreshing" it.
#         return redirect("/")
    
#     return redirect("/")


@app.route("/initialize", methods=["POST"])
def initialize():
    """Initialize the database tables if not already exists, as per the instructions"""
    # Make sure a user is logged in before they can execute this.
    # Check if user is logged in.
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    # SQL statements to create tables
    create_tables_query = """
        CREATE DATABASE IF NOT EXISTS comp440_project;
        USE comp440_project;

        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(255) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS items (
            item_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            title VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS categories (
            category_id INT AUTO_INCREMENT PRIMARY KEY,
            category_name VARCHAR(50) UNIQUE
        );

        CREATE TABLE IF NOT EXISTS item_categories (
            item_id INT,
            category_id INT,
            PRIMARY KEY (item_id, category_id),
            FOREIGN KEY (item_id) REFERENCES items(item_id),
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        );

        CREATE TABLE IF NOT EXISTS reviews (
            review_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            item_id INT,
            rating ENUM("excellent", "good", "fair", "poor") NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (item_id) REFERENCES items(item_id)
        );

        -- Pre-defined categories
        INSERT IGNORE INTO categories (category_name) 
        VALUES 
            ('Electronics'),
            ('Fashion'),
            ('Home & Garden'),
            ('Toys & Games'),
            ('Books & Media'),
            ('Collectibles'),
            ('Sports & Outdoors'),
            ('Automotive'),
            ('Health & Beauty'),
            ('Crafts & DIY'),
            ('Business & Industrial'),
            ('Hobbies'),
            ('Musical Instruments'),
            ('Art'),
            ('Pets');

    """

    # Execute the above SQL statements
    cursor.execute(create_tables_query, multi=True)

    # Dummy item details
    dummy_items = [
        ("Laptop", "Brand new laptop, great for gaming", 999.99),
        ("Coffee Maker", "High-quality coffee machine for home use", 49.99),
        ("Yoga Mat", "Premium yoga mat, eco-friendly material", 29.99),
        ("Bluetooth Speaker", "Portable speaker with excellent sound quality", 79.99),
        ("Gardening Tools", "Set of essential tools for gardening enthusiasts", 39.99),
    ]

    # Get all available category IDs from the categories table
    cursor.execute("SELECT category_id FROM categories")
    categories = cursor.fetchall()
    category_ids = [category["category_id"] for category in categories]

    # Get current session user id to upload as author.
    user_id: int = session["user_id"]

    for item in dummy_items:
        # Insert item details into the items table
        cursor.execute("INSERT IGNORE INTO items (author_id, title, description, price) VALUES (%s, %s, %s, %s)", (user_id, item['title'], item['description'], item['price']))

        # Get the last inserted item_id
        cursor.execute("SELECT LAST_INSERT_ID()")
        item_id = cursor.fetchone()["item_id"]

        # Assign a random category to the item
        random_category_id = random.choice(category_ids)
        cursor.execute("INSERT IGNORE INTO item_categories (item_id, category_id) VALUES (%s, %s)", (item_id, random_category_id))

    # Commit the changes
    connection.commit()

    if cursor.rowcount > 0:
        flash("Database successfully initialized!", "success")
    else:
        flash("No initialization needed", "info")

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
