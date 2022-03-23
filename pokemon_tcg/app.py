from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Card, Favorite
from forms import AddUserForm, LoginForm
import os
import re

app = Flask(__name__)

uri = os.environ.get('DATABASE_URL', 'postgresql:///pokemon_tcg')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)


app.config['SQLALCHEMY_DATABASE_URI'] = uri

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False 
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

CURR_USER_KEY = "current_user"


##############################################################################
# ERROR HANDLERS
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
##############################################################################

@app.before_request   # This function is run before each request. 
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
        # if there is currently a logged in user, query that user 
        # A common use for 'g' is to manage resources during a request. The g name stands for “global”, but that is referring to the data being global within a context.
        # Use the session or a database to store data across requests. The application context is a good place to store common data during a request.

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def homepage():
    """Show homepage:

    - anonymous users: show sign up landing page
    - logged in: show main search page
    """
    return render_template('home.html')
    

@app.route('/welcome')
def welcome():
    """Landing page for new users"""

    if g.user:
        flash("Welcome back!", "success")
        return redirect('/')

    else:
        return render_template('home-anon.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the username is already taken,flash message and re-present form.
    """

    if g.user:
        flash("Already logged in. If you would like to make a new account, please logout of the current account.", "danger")
        return redirect("/")

    form = AddUserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash("Username already taken. Please try a different username.", 'danger')
            return render_template('user/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('user/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    if g.user: 
        flash("You are already currently logged in.", "danger")
        return redirect("/")

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('user/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    if not g.user:
        flash("You need to log in or sign up for an account.", "danger")
        return redirect("/")

    do_logout() # this method is defined above

    flash(f"You have successfully logged out.", "success")
    return redirect("/login")
