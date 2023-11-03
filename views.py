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
        title = request.form.get("title").strip()
        description = request.form.get("description").strip()
        category = request.form.get("category").strip()
        price = float(request.form.get("price"))
        user_id = 1  # Replace with the actual user's ID
        
        # Check if the user has posted 3 items today
        today = datetime.today().date()
        cursor.execute("SELECT items_posted FROM users WHERE username = %s", (username,))
        items_posted = cursor.fetchone()[0]
        
        if items_posted >=3:
            flash("You've already posted 3 times today. You can't post more.", "error")
        else:
            # Insert the new item into the database
            cursor.execute("INSERT INTO products (title, description, category, price, username) VALUES (%s, %s, %s, %s, %s)",(title, description, category, price,username))
            connection.commit()
            items_posted += 1
            
            #Update the items_posted count in the users table
            cursor.execute("UPDATE users SET items_posted = %s WHERE username = %s", (items_posted, username))
            connection.commit()
            
            flash("Item posted sucessfully.", "success")

    return render_template("post_item.html")

    if __name__ == "__main__":
    app.run(debug=True)
