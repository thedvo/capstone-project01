"""Card View tests."""

# run these tests with:
# python -m unittest test_card_views.py

import os
from unittest import TestCase

from models import db, connect_db, Card

os.environ['DATABASE_URL'] = "postgresql:///pokemon-tcg-test"

from app import app, CURR_USER_KEY

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class CardViewTestCase(TestCase):
    """Test views for cards."""

    def setUp(self):
        """Create test client, add sample data."""

        Card.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any foul transaction."""

        db.session.rollback()
    
#######################################################################
# SHOW CARD SEARCH RESULTS
    
    def test_show_valid_search_results(self):
        """Show valid card results from a user's search input"""

        with self.client as client:
            res = client.get('/cards?pokemon-search=pikachu', 
                             follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            # should show heading indicating number of results for that search
            self.assertIn("Search results for ", str(res.data))


    def test_show_invalid_card_result(self):
        """Try to route to a card that doesn't exist in database"""
        with self.client as client:
           
            res = client.get('/cards/101341',
                             follow_redirects = True)

            self.assertEqual(res.status_code, 200)
            # redirects to home page since invalid search.
            self.assertIn("Pokemon TCG Search", str(res.data))
            self.assertIn("This is not produced, endorsed, supported, or affiliated with Nintendo or The Pokemon Company.", str(res.data))


# #######################################################################
# # SHOW AN INDIVIDUAL CARD'S DETAILS
    
    def test_show_message(self):
        """Show the details for a valid individual card"""

        with self.client as client:

            res = client.get(f'/cards/swshp-SWSH020')

            self.assertEqual(res.status_code, 200)
            self.assertIn("Flip a coin until you get tails. This attack does 30 damage for each heads.", str(res.data))


    def test_show_invalid_message(self):
        """Try to route to a card that doesn't exist in database"""
        with self.client as client:
            
            res = client.get('/cards/1234',
                             follow_redirects = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Invalid search. Please try something else", str(res.data))

# #######################################################################
# Test Invalid Routes (404, 405 errors)

    def test_invalid_route_404(self):
        """Try to route to a page that doesn't exist in the app"""

        with self.client as client:
            res = client.get('/1234',
                             follow_redirects = True)

        self.assertEqual(res.status_code, 404)
        self.assertIn("PAGE NOT FOUND", str(res.data))

    def test_invalid_route_405(self):
        """Try to route a method which is not allowed"""

        with self.client as client:
            res = client.get('/cards/1241/favorite',
                             follow_redirects = True)

        self.assertEqual(res.status_code, 405)

        # Method not allowed since card (id 1241) does not exist in the database
        self.assertIn("405", str(res.data))
        self.assertIn("METHOD NOT ALLOWED", str(res.data))
        self.assertIn("Nice Try...", str(res.data))

    
