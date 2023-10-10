from flask import Flask, request, render_template, redirect, flash
from mysql.connector import connection

app = Flask(__name__)

connection = connection.MySQLConnection(
    user="root", password="", host="127.0.0.1", database="signup"
)


@app.route("/")
def home():
    # For now.
    return redirect("/registration")


@app.route("/registration", methods=["GET", "POST"])
def registration():
    """User account creation"""
    
    # Form submission.
    if request.method == "POST":
        
        ...

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

