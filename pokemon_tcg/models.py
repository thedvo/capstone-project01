from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

DEEFAULT_PROFILE_IMAGE = 'https://i1.sndcdn.com/artworks-000193803962-tla7ov-t500x500.jpg'

def connect_db(app):
    """Connect database to provided Flask app."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """Users in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    profile_image = db.Column(db.Text, default= DEEFAULT_PROFILE_IMAGE)
    datetime_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}, {self.datetime_created}>"
    
    favorites = db.relationship(
        'Card',
        secondary="favorites"
    )

    @classmethod
    def signup(cls, username, password, email):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            email=email
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False



class Card(db.Model):
    """Individual Pokemon Trading Card"""

    __tablename__ = 'cards'

    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Card #{self.id}: {self.name}>"



class Favorite(db.Model):
    """Mapping user favorites to cards."""

    __tablename__ = 'favorites' 

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    card_id = db.Column(db.Text, db.ForeignKey('cards.id', ondelete='cascade'), primary_key=True)

    def __repr__(self):
        return f"<Favorites | User {self.user_id} | Card {self.card_id}>"
    
