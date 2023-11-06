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
cursor = connection.cursor()


@app.route("/")
def home():
    """Will list out all the user listings and also the listing form"""
    # Check if user is logged in.
    if not "username" in session:
        return redirect("/login")

    return render_template("index.html")


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
            return redirect("/registration")

        # Ensure username and email aren't already taken.
        cursor.execute(f"SELECT username FROM users WHERE username = %s", (username, ))
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

        flash("Successfully signed up!", "success")

        return redirect("/login")
    
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
            return redirect("/login")
        
        # Find if user exists and has matching password.
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            # Log them in.
            session["username"] = user["username"]

            flash("Successfully logged in!", "success")

            return redirect("/")
        
        # Credentials do not match.
        flash("No matching account was found", "error")

        return redirect("/login")

    return render_template("login.html")


@app.route("/submit_listing", methods=["GET", "POST"])
def submit_listing():
    """Submit an item as a listing"""
    # Check if user is logged in.
    if not "username" in session:
        return redirect("/login")
    
    if request.method == "POST":
        username: str = session["username"]

        # TODO Check if the user has already posted 3 items today.
        # today = datetime.today().date()
        # cursor.execute("SELECT items_posted FROM users WHERE username = %s", (username,))
        # items_posted = cursor.fetchone()[0]
        items_posted: int = 2
        if items_posted >= 3:
            flash("You've already posted 3 times today. You can't post more.", "error")

        # TODO Fetch item inputs.
        title = request.form.get("title").strip()
        description = request.form.get("description").strip()
        category = request.form.get("category").strip()
        price = float(request.form.get("price"))
        user_id = 1  # Replace with the actual user's ID

        # TODO Save the listing into the database.
        cursor.execute("INSERT INTO products (title, description, category, price, username) VALUES (%s, %s, %s, %s, %s)",(title, description, category, price,username))
        connection.commit()
        
        flash("Item posted sucessfully.", "success")

        # Redirect to same page, essentially "refreshing" it.
        return redirect("/")
    
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
