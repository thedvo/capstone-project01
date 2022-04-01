"""User View tests."""

# run these tests like:
# python -m unittest test_user_views.py

import os
from unittest import TestCase
from models import db, connect_db, User, Card, Favorite

os.environ['DATABASE_URL'] = "postgresql:///pokemon-tcg-test"

from app import app, CURR_USER_KEY

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for Users."""
    
    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()
    
        self.testuser = User.signup("testuser",
                                    "password",
                                    "test@test.com")
        self.testuser_id = 10
        self.testuser.id = self.testuser_id

        db.session.commit()

    def tearDown(self):
        """Clean up any foul transaction."""

        db.session.rollback()

###########################################################################
# USER ROUTES

    def test_show_user_profile(self):
        """Show User Profile if user is logged in"""

        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser_id

            res = client.get("/user")

            self.assertEqual(res.status_code, 200)
            self.assertIn("testuser", str(res.data))
    
    def test_show_user_profile_invalid(self):
        """Redirect to home if user is not logged in"""
        with self.client as client:
            res = client.get("/user", 
                            follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Pokemon TCG Search", str(res.data))
            # Should redirect to home if user is not logged in and tries to access their user profile
    
###########################################################################
# SET UP FAVORITES

    def setup_favorites(self):
        """set up cards and favorites to use in tests"""
        pokemon_card = Card(id = "one", 
                           name = "pikachu")

        pokemon_card2 = Card(id = "two",
                           name = "charmander")
       
        db.session.add_all([pokemon_card, pokemon_card2])
        db.session.commit()

        favorite = Favorite(card_id = "one", 
                            user_id = self.testuser.id)
                      
        db.session.add(favorite)
        db.session.commit()

# ###########################################################################
# FAVORITE ROUTES

    def test_favorite_card(self):
        """Testing to see if adding favorite to model worked"""

        self.setup_favorites()
       
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser_id

            # make post request to favorite a card
            res = client.post("/cards/two/favorite",
                              follow_redirects=True)

        favorites = Favorite.query.filter(Favorite.card_id=="two").all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(favorites), 1)
        self.assertEqual(favorites[0].user_id, self.testuser_id)

    
    def test_remove_favorite(self):
        """Removing a card from user's favorites."""
        self.setup_favorites()

        # Here we'll check to see if the card is favorited by the user. If it is, then we can unfavorite it. 

        # get the favorited card 
        card = Card.query.filter(Card.name=="pikachu").one()
        self.assertIsNotNone(card)
        
        # query the card which is favorited by the logged in user
        favorite_card = Favorite.query.filter(Favorite.user_id==self.testuser.id and Favorite.card_id==card.id).one()

        # check if there is a favorite
        self.assertIsNotNone(favorite_card)

        
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser_id

            # we will make another post request to favorite that card so we can unfavorite it. 
            res = client.post(f"/cards/{card.id}/favorite", 
                              follow_redirects=True)

            favorites = Favorite.query.filter(Favorite.card_id==card.id).all()

            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(favorites), 0)


    def test_favorite_card_as_unauthorized_user(self):
        """Trying to favorite a card while not signed in"""
        self.setup_favorites()

        # select a card
        card = Card.query.filter(Card.name=="charmander").one()
        self.assertIsNotNone(card)

        # count the number of likes there are
        favorite_count = Favorite.query.count()

        # make a post request to favorite the selected card
        with self.client as client:
            res = client.post(f"/cards/{card.id}/favorite",           
                              follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Please login to favorite a card.", str(res.data))
            # access unauthorized since user is not logged in
            
            self.assertEqual(favorite_count, Favorite.query.count())
            # number of favorites in the table should not change since the user is unauthorized to make this request




