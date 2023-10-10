from flask import Flask, request, render_template, redirect, flash

app = Flask(__name__)


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

