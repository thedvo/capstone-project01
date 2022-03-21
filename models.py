

DEEFAULT_PROFILE_IMAGE = 'https://i1.sndcdn.com/artworks-000193803962-tla7ov-t500x500.jpg'

class User(db.Model):
    """Users in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    profile_image = db.Column(db.Text, default= DEEFAULT_PROFILE_IMAGE)


class Card(db.Model):
    """Individual Pokemon Trading Card"""

    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)


class Favorites(db.Model):
    """Mapping user favorites to cards."""

    __tablename__ = 'favorites' 

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    card_id = db.Column(db.Integer, db.ForeignKey('card.id', ondelete='cascade'))
    
