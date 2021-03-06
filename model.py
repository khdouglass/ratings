"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
from correlation import pearson

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def similarity(self, other):
        """Return Pearson rating for user compared to other user."""

        user_ratings = {}
        paired_ratings = []

        for rating in self.ratings:
            user_ratings[rating.movie_id] = rating

        for rating in other.ratings:
            user_rate = user_ratings.get(rating.movie_id)
            if user_rate:
                paired_ratings.append( (user_rate.score, rating.score) )

        if paired_ratings:
            return pearson(paired_ratings)

        else:
            return 0.0

    def predict_rating(self, movie):
        """Predict a user's rating of a movie."""

        #list of movie's rating objects
        other_ratings = movie.ratings
       
        similarities = [
            (self.similarity(r.user), r)
            for r in other_ratings
        ]

        #sorting that list so most similar user is first
        similarities.sort(reverse=True)

        similarities = [(sim, r) for sim, r in similarities
                        if sim > 0]

        if not similarities:
            return None
        
        numerator = sum([r.score * sim for sim, r in similarities])
        denominator = sum([sim for sim, r in similarities])

        return numerator / denominator


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class Movie(db.Model):
    """ Movie info in ratings website."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.String(180), nullable=True)


class Rating(db.Model):
    """Movie rating info from users."""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", backref=db.backref("ratings", order_by=rating_id))
    movie = db.relationship("Movie", backref=db.backref("ratings", order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        rating_info = "<Rating rating_id=%s movie_id=%s user_id=%s score=%s>"
        return rating_info % (self.rating_id, self.movie_id, self.user_id,
                    self.score)
# Put your Movie and Rating model classes here.


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
