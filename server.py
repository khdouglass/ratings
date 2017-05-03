"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    # a = jsonify([1,3])
    # return a

    return render_template("homepage.html")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route("/register")
def register_form():

    return render_template("register_form.html")

@app.route("/register", methods=["POST"])
def register_process():
    """Process registration information"""

    email = request.form.get("email")
    print email
    
    password = request.form.get("password")
    
    emails = db.session.query(User.email).all()

    if email not in emails:
        new_user = User(email=email, password=password)
    print new_user
    db.session.add(new_user)
    db.session.commit()


    return redirect("/")
@app.route("/login")
def login():

    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_submission():

    email = request.form.get("email")
    print type(email)
    password = request.form.get("password")
    print password

    emails = db.session.query(User.email).all()
    print type(emails[0])
    
    if (email,) in emails:
        print "yes"
        user = db.session.query(User).filter_by(email=email).one()
        user_password = user.password 
        if password == user_password:
            session["user_id"] = user.user_id
            print user_password    
            flash("You are logged in!")

    
    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host='0.0.0.0')
