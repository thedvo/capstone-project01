"""User model tests."""

# run these tests with:
#    python -m unittest test_user_model.py

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Card, Favorite

# testing database
# set this before importing the app
os.environ['DATABASE_URL'] = "postgresql:///pokemon-tcg-test"

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test User Model"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Card.query.delete()
        Favorite.query.delete()

        user1 = User.signup(
                "testuser", 
                "password",
                "test@test.com")
        user1.id = 10

        user2 = User.signup(
                "testuser2", 
                "password",
                "test2@test.com")
        user2.id = 20

        db.session.commit()

        user1 = User.query.get(user1.id)
        user2 = User.query.get(user2.id)

        self.user1  = user1
        self.user1_id = user1.id

        self.user2 = user2
        self.user2_id = user2.id

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any foul transaction."""

        db.session.rollback()

######################################################################
# TEST USER MODEL

    def test_user_model(self):
        """Check if user model works"""

        u = User(
            username="testuser3",
            password="password",
            email="test@test.com",
            profile_image=None
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(len(u.favorites), 0)

######################################################################
# USER SIGNUP TESTS (valid form inputs)

    def test_create_user_valid(self):
        """Successfully create new user given valid credentials"""

        new_user = User.signup("testuser4", 
                               "password",
                               "test4@test.com")
        user_id = 40
        new_user.id = user_id

        db.session.commit()

        new_user = User.query.get(new_user.id)
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.username, "testuser4")
        self.assertEqual(new_user.email, "test4@test.com")
        self.assertNotEqual(new_user.password, "password")
        # reason we test for not equal is because it should be encrypted

######################################################################
# USER SIGNUP TESTS (invalid form inputs)

    def test_create_user_with_invalid_username(self):
        """Tests if user creation fails if username validation fails."""

        invalid_user = User.signup(None,                           
                                  "password", 
                                  "test@test.com")
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_create_user_with_invalid_email(self):
        """Testing if validation checks if there is a valid email inputted"""
        invalid = User.signup("test", 
                              "password", 
                               None)
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_create_user_with_invalid_password(self):
        """Testing if validation checks if there is a valid password inputted"""

        with self.assertRaises(ValueError) as context:
            User.signup("test", 
                        "", # invalid password. Must be at least 6 characters 
                        "test@test.com")

######################################################################
# AUTHENTICATION TESTS

    def test_authentication(self):
        """Successful return given valid username and password"""
        user = User.authenticate(self.user1.username, "password")
        
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.user1_id)


    def test_invalid_username(self):
        """Failure given invalid username"""
        
        self.assertFalse(User.authenticate("invalid_username", "password"))


    def test_invalid_password(self):
        """Failure given invalid password"""
        
        self.assertFalse(User.authenticate(self.user1.username, "wrongpassword"))

