from flask import Flask, request, render_template, redirect, flash
from werkzeug.security import generate_password_hash
from mysql.connector import connection

app = Flask(__name__)
app.config["TESTING"] = True
app.config["SECRET_KEY"] = "placeholder"

connection = connection.MySQLConnection(
    user="root", password="", host="127.0.0.1", database="signup"
)
cursor = connection.cursor()


@app.route("/")
def home():
    # For now.
    return redirect("/registration")


@app.route("/registration", methods=["GET", "POST"])
def registration():
    """User account creation"""
    
    # Form submission.
    if request.method == "POST":
        
        # Get and cleanse registration data.
        first_name = request.form.get("firstName").strip()
        last_name = request.form.get("lastName").strip()
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        confirm_password = request.form.get("confirmPassword").strip()

        # Ensure username and email aren't already taken.
        cursor.execute(f"SELECT username FROM users WHERE username = %s", (username, ))
        if cursor.fetchall():
            flash("Username already taken!", "error")
            return render_template("signup.html"), 400
        
        cursor.execute(f"SELECT email FROM users WHERE email = '{email}'")
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
            "INSERT INTO users (username, firstName, lastName, email, password) VALUES (%s, %s, %s, %s, %s)",
            (username, first_name, last_name, email, hashed_password)
        )
        connection.commit()

        flash("Successfully signed up!", "success")

        return redirect("/login")
    
    return render_template("signup.html")


# TODO
@app.route("/login", methods=["GET", "POST"])
def login():
    """User login to account"""

    if request.method == "POST":

        ...  # TODO

    return render_template("login.html")

