"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session, url_for)
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

@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/users/<user_id>")
def show_user_info(user_id):
    """Show information about user."""

    user = User.query.get(user_id)
    ratings = user.ratings

    return render_template("user_info.html", user=user, ratings=ratings)

@app.route("/movies/<int:movie_id>")
def show_movie_info(movie_id):
    """Show information about a movie."""

    movie = Movie.query.get(movie_id)

    user_id = session.get("user_id")

    if user_id:
            user_rating = Rating.query.filter_by(
                movie_id = movie_id, user_id = user_id).first()
    else:
        user_rating = None

    #Get average rating of movie

    rating_scores = [rating.score for rating in movie.ratings]
    avg_rating = float(sum(rating_scores))/len(rating_scores)

    prediction = None

    #Prediction code: only predict of the user hasn't rated it.

    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(movie)

    return render_template(
        "movie_info.html",
        movie=movie,
        user_rating=user_rating,
        average=avg_rating,
        prediction=prediction
        )

@app.route("/movies/<movie_id>", methods=["POST"])
def rate_movie(movie_id):
    """Rate a movie."""

    user_rating = request.form.get("rating")
 
    user_id = session.get("user_id")
    if not user_id:
        raise Exception("No user logged in.")

    previous_rating = db.session.query(Rating).filter(movie_id == Rating.movie_id, user_id==Rating.user_id).first()

    if previous_rating:
        previous_rating.score = user_rating
        db.session.add(previous_rating)
    else:
        new_rating = Rating(user_id=user_id, movie_id=movie_id, score=user_rating)
        db.session.add(new_rating)

    db.session.commit()

    return redirect("/movies")
    # return redirect("/movies/%s" % movie_id)


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
        user = db.session.query(User).filter_by(email=email).one()
        user_password = user.password
        if password == user_password:
            session["user_id"] = user.user_id
            flash("You are logged in!")

    return redirect(url_for(".show_user_info", user_id=user.user_id))


@app.route("/logout")
def logout():
    """User logout, remove user_id from session"""

    del session["user_id"]

    flash("You are logged out")
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
