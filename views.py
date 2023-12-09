import random
import datetime

from flask import Flask, request, render_template, redirect, flash, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from mysql.connector import connection

from phase_3_queries import *

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


### VIEWS ###


@app.route("/")
def home():
    """Will list out all the user listings and also the listing form"""
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    # Insert the pre-defined categories as a list of options.
    cursor.execute("SELECT category_name FROM categories")
    categories: list[str] = [row["category_name"] for row in cursor.fetchall()]

    # Get user-selected category, if selected. Default is all.
    search_category: str = None
    query = None
    if request.args.get("category") in categories:
        search_category = request.args.get("category")

        # Query for the listings with a specific category.
        query = """
            SELECT 
                users.username AS author,
                items.item_id,
                items.title,
                items.description,
                items.price,
                items.created_at,
                categories.category_name AS category
            FROM items
            INNER JOIN item_categories
            INNER JOIN categories
            INNER JOIN users
            ON
                items.item_id = item_categories.item_id AND
                item_categories.category_id = categories.category_id AND
                users.user_id = items.author_id
            WHERE categories.category_name = %s
            ORDER BY created_at DESC;
        """
        cursor.execute(query, (search_category,))
    else:
        # Query for all listings, no specific category.
        query = """
            SELECT 
                users.username AS author,
                items.item_id,
                items.title,
                items.description,
                items.price,
                items.created_at,
                categories.category_name AS category
            FROM items
            INNER JOIN item_categories
            INNER JOIN categories
            INNER JOIN users
            ON
                items.item_id = item_categories.item_id AND
                item_categories.category_id = categories.category_id AND
                users.user_id = items.author_id
            ORDER BY created_at DESC;
        """
        cursor.execute(query)

    listings = cursor.fetchall()

    cursor.execute("SELECT * FROM users;")
    all_users = cursor.fetchall()

    return render_template("index.html",
                           all_users=all_users,
                           username=session["username"],
                           search_category=search_category,
                           categories=categories,
                           listings=listings)


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
        cursor.execute(
            "SELECT username FROM users WHERE username = %s", (username, ))
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
        cursor.execute(
            "SELECT user_id FROM users WHERE username = %s", (username,))
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


@app.route("/submit_listing/", methods=["GET", "POST"])
def submit_listing():
    """Submit an item as a listing"""
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    if request.method == "POST":
        username: str = session["username"]
        user_id: int = session["user_id"]

        # Check if the user has already posted 3 items today.
        query = """
            SELECT items.created_at
            FROM items
            WHERE items.author_id = %s
            ORDER BY created_at DESC
            LIMIT 3;
        """
        cursor.execute(query, (user_id,))
        if has_reached_max_posts(cursor.fetchall()):
            flash("You have reached the limit for posting items for today", "error")
            return redirect("/")

        # Fetch item inputs.
        title = request.form.get("title").strip()
        description = request.form.get("description").strip()
        category = request.form.get("category").strip()
        price = float(request.form.get("price"))

        # Get ID from selected category.
        cursor.execute(
            "SELECT category_id FROM categories WHERE category_name = %s", (category,))
        category_id: int = cursor.fetchone()["category_id"]

        # Save item listing.
        insert_item(user_id, title, description, price, category_id)

        # Commit changes.
        connection.commit()

        flash("Item posted sucessfully.", "success")

        return redirect("/")

    # Insert the pre-defined categories as a list of options.
    cursor.execute("SELECT category_name FROM categories")
    categories: list[str] = [row["category_name"] for row in cursor.fetchall()]

    return render_template("post_listing.html", categories=categories)


@app.route("/submit_review/item_id=<item_id>/", methods=["POST"])
def submit_review(item_id: int):
    """Submit review for an item"""
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    user_id: int = session["user_id"]

    # Get and cleanse form data.
    rating = request.form.get("rating").strip()
    review = request.form.get("review").strip()

    # Check if the user has already posted 3 items today.
    query = """
        SELECT reviews.created_at
        FROM reviews INNER JOIN items
        ON reviews.item_id = items.item_id
        WHERE reviews.author_id = %s
        ORDER BY created_at DESC
        LIMIT 3;
    """
    cursor.execute(query, (user_id,))
    if has_reached_max_posts(cursor.fetchall()):
        flash("You have reached the maximum posts for today", "error")
        return redirect("/")

    # Create and save review into database.
    cursor.execute(
        "INSERT INTO reviews (author_id, item_id, rating, description) VALUES (%s, %s, %s, %s)",
        (user_id, item_id, rating, review)
    )

    # Commit the changes.
    connection.commit()

    # Return to individual item listing, where they will see the reviews under it.
    return redirect(f"/listing/id={item_id}")


@app.route("/listing/id=<listing_id>")
def view_listing(listing_id: int):
    """View an individual listing"""
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    # Query for the listings, getting the author and the category.
    query = """
        SELECT 
            users.username AS author,
            items.item_id,
            items.title,
            items.description,
            items.price,
            items.created_at,
            categories.category_name AS category
        FROM items
        INNER JOIN item_categories
        INNER JOIN categories
        INNER JOIN users
        ON
            items.item_id = item_categories.item_id AND
            item_categories.category_id = categories.category_id AND
            users.user_id = items.author_id
        WHERE items.item_id = %s
        ORDER BY created_at DESC;
    """
    cursor.execute(query, (listing_id,))
    listing = cursor.fetchone()

    if not listing:
        flash("Item does not exist", "error")
        return redirect("/")

    # Insert reviews to be seen under the item.
    query = """
        SELECT users.username, reviews.rating, reviews.description, reviews.created_at
        FROM users INNER JOIN items INNER JOIN reviews
        ON users.user_id = reviews.author_id AND items.item_id = reviews.item_id
        WHERE reviews.item_id = %s
        ORDER BY created_at DESC;
    """

    cursor.execute(query, (listing_id,))
    reviews = cursor.fetchall()

    return render_template("listing.html", listing=listing, reviews=reviews, ratings=["excellent", "good", "fair", "poor"])


### UTILITIES ###


def insert_item(author_id: int, title: str, description: str, price: float, category_id: int) -> None:
    """General function that helps with inserting an item along with its belonging category"""
    # Insert item.
    cursor.execute("INSERT IGNORE INTO items (author_id, title, description, price) VALUES (%s, %s, %s, %s)",
                   (author_id, title, description, price))

    # Fetch item's ID after being generated from insertion.
    cursor.execute("SELECT LAST_INSERT_ID()")
    item_id = cursor.fetchone()["LAST_INSERT_ID()"]

    # Create an item-category connection, binding an item to a category.
    cursor.execute(
        "INSERT IGNORE INTO item_categories (item_id, category_id) VALUES (%s, %s)", (item_id, category_id))


def has_reached_max_posts(query: list[dict]) -> bool:
    """General function that helps with checking if user has posted 3 times the past day.

    Either for items or reviews on an item.
    """
    num_posted_today: int = 0
    for row in query:
        date = row["created_at"]
        # Check if earlier.
        if date < datetime.datetime.now():
            num_posted_today += 1

    return num_posted_today >= 3


@app.route("/initialize", methods=["POST"])
def initialize():
    """Initialize the database tables if not already exists, as per the instructions"""
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

        -- A user's favorite seller.
        CREATE TABLE IF NOT EXISTS favorite_users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            favorite_user_id INT NOT NULL,
            FOREIGN KEY (favorite_user_id) REFERENCES users(user_id)
        );

        -- A user's favorite item.
        CREATE TABLE IF NOT EXISTS favorite_items (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            favorite_item_id INT NOT NULL,
            FOREIGN KEY (favorite_item_id) REFERENCES items(item_id)
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

        -- Make admin
        INSERT IGNORE INTO users (user_id, username, password, first_name, last_name, email)
        VALUES (1, 'admin', 'admin', 'Max', 'Caulfield', 'admin@gmail.com');

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
        {'title': 'Shoes', 'description': 'Running shoes for everyday workout', 'price': 49.99},
        {'title': 'Book', 'description': 'A thrilling novel about adventure', 'price': 14.99},
        {'title': 'Headphones', 'description': 'Noise-cancelling headphones', 'price': 99.99}
    ]

    # Get all available category IDs from the categories table
    cursor.execute("SELECT category_id FROM categories")
    categories = cursor.fetchall()
    category_ids: list[int] = [category["category_id"]
                               for category in categories]

    for item in dummy_items:
        # Insert item with an assigned category.
        random_category_id = random.choice(category_ids)
        insert_item(1, item["title"], item["description"],
                    item["price"], random_category_id)

    # Commit the changes
    connection.commit()

    flash("Database successfully initialized!", "success")

    return redirect("/")


@app.route("/lmao")
def lma0():
    return render_template("lmao.html")


### PHASE 3 QUERIES ###


# Query-1 View
@app.route("/query-1", methods=["GET", "POST"])
def query_1():
    """List the most expensive items in each category"""
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    cursor.execute(QUERY_1)
    items = cursor.fetchall()

    cursor.execute("SELECT * FROM users;")
    all_users = cursor.fetchall()

    return render_template("phase_3_queries/query-1.html", items=items, all_users=all_users)


# Query-2 View
@app.route("/query-2", methods=["GET", "POST"])
def query_2():
    """
    List the users who posted at least two items that were posted on the same day, one has a category
    of X, and another has a category of Y
    """
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    cursor.execute("SELECT * FROM categories;")
    categories = cursor.fetchall()

    category_1 = None
    category_2 = None
    selected_users = None

    cursor.execute("SELECT * FROM users;")
    all_users = cursor.fetchall()

    if request.method == "POST":
        category_1 = request.form.get("category-1")
        category_2 = request.form.get("category-2")

        cursor.execute(QUERY_2, (category_1, category_2))
        selected_users = cursor.fetchall()

        return render_template("phase_3_queries/query-2.html", category_1=category_1, category_2=category_2, categories=categories, selected_users=selected_users, all_users=all_users)

    return render_template("phase_3_queries/query-2.html", category_1=category_1, category_2=category_2, categories=categories, selected_users=selected_users, all_users=all_users)


# Query-3 View
@app.route("/query-3", methods=["GET", "POST"])
def query_3():
    """
    List all the items posted by user X, such that all the comments are "Excellent" or "good" for
    these items. User X is arbitrary and will be determined by the instructor.
    """
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    cursor.execute("SELECT * FROM users;")
    all_users = cursor.fetchall()

    items = None

    cursor.execute("SELECT * FROM users;")
    users = cursor.fetchall()

    username = None

    if request.method == "POST":
        username = request.form.get("user")
        print(username)

        cursor.execute(QUERY_3, (username,))
        items = cursor.fetchall()

        return render_template("phase_3_queries/query-3.html", username=username, users=users, items=items, all_users=all_users)

    return render_template("phase_3_queries/query-3.html", username=username, users=users, items=items, all_users=all_users)


# Query-4 View
@app.route("/query-4", methods=["GET", "POST"])
def query_4():
    """
    List the users who posted the most number of items on a specific date like 5/1/2023; if there is
    a tie, list all the users who have a tie. The specific date can be hard coded into your SQL select
    query or given by the user. 
    """
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    HARDCODED_DATE = "2023-12-04"

    cursor.execute("SELECT * FROM users;")
    all_users = cursor.fetchall()

    cursor.execute(QUERY_4, (HARDCODED_DATE,))
    selected_users = cursor.fetchall()

    return render_template("phase_3_queries/query-4.html", hardcoded_date=HARDCODED_DATE, all_users=all_users, selected_users=selected_users)


# Query-5 View
@app.route("/query-5", methods=["GET", "POST"])
def query_5():
    """
    List the other users who are favorited by both users X, and Y. Usernames X and Y will be
    selected from dropdown menus by the instructor.
    """
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    cursor.execute("SELECT * FROM users;")
    all_users = cursor.fetchall()

    user_likers = all_users
    favorites = None

    cursor.execute(QUERY_5_LIKERS)
    liker_pairs = cursor.fetchall()

    if request.method == "POST":
        user_1 = request.form.get("user-1")
        user_2 = request.form.get("user-2")

        cursor.execute(QUERY_5, (user_1, user_2))
        favorites = cursor.fetchall()

        return render_template("phase_3_queries/query-5.html", user_1=user_1, user_2=user_2, favorites=favorites, liker_pairs=liker_pairs, user_likers=user_likers, all_users=all_users)

    return render_template("phase_3_queries/query-5.html", liker_pairs=liker_pairs, user_likers=user_likers, all_users=all_users)


# Query-6 View
@app.route("/query-6", methods=["GET", "POST"])
def query_6():
    """
    Display all the users who never posted any "excellent" items: an item is excellent if at least
    three reviews are excellent. 
    """
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    cursor.execute(QUERY_6)
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM users;")
    all_users = cursor.fetchall()

    return render_template("phase_3_queries/query-6.html", users=users, all_users=all_users)


# Query-7 View
@app.route("/query-7", methods=["GET", "POST"])
def query_7():
    """Display all the users who never posted a "poor" review"""
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    cursor.execute(QUERY_7)
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM users;")
    all_users = cursor.fetchall()

    return render_template("phase_3_queries/query-7.html", users=users, all_users=all_users)


# Query-8 View
@app.route("/query-8", methods=["GET", "POST"])
def query_8():
    """Display all the users who posted some reviews, but each of them is "poor"""
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    cursor.execute(QUERY_8)
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM users;")
    all_users = cursor.fetchall()

    return render_template("phase_3_queries/query-8.html", users=users, all_users=all_users)


# Query-9 View
@app.route("/query-9", methods=["GET", "POST"])
def query_9():
    """Display those users such that each item they posted so far never received any "poor" reviews"""
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    cursor.execute(QUERY_9)
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM users;")
    all_users = cursor.fetchall()

    return render_template("phase_3_queries/query-9.html", users=users, all_users=all_users)


# Query-10 View
@app.route("/query-10", methods=["GET", "POST"])
def query_10():
    """
    List a user pair (A, B) such that they always gave each other "excellent" reviews for every single
    item they posted. 
    """
    if not "username" in session:
        flash("You must be logged in to perform this", "error")
        return redirect("/login")

    cursor.execute(QUERY_10)
    user_pairs = cursor.fetchall()

    cursor.execute("SELECT * FROM users;")
    all_users = cursor.fetchall()

    return render_template("phase_3_queries/query-10.html", user_pairs=user_pairs, all_users=all_users)


if __name__ == "__main__":
    app.run(debug=True)
