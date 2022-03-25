from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Card, Favorite
from forms import AddUserForm, LoginForm, EditUserForm
import requests
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

API_BASE_URL = 'https://api.pokemontcg.io/v2/cards'
CURR_USER_KEY = "current_user"

############################################################################################
# POKEMON TCG API ROUTES - CARDS

def request_cards(pokemon):
    """Return the dictionary containing the Pokemon card info"""

    url = f'{API_BASE_URL}/?q=name:{pokemon}'
    response = requests.get(url)
    data = response.json()

    data = data['data']
  
    return {"data": data}


@app.route('/cards/')
def get_pokemon_cards():
    """Handle form submission; return form; show cards related to search query"""

    pokemon = request.args.get('pokemon-search')
    card = request_cards(pokemon)

    return render_template('card/cards.html', cards = card)


@app.route('/cards/<id>')
def get_card_details(id):
    """Display details for an individual card"""

    url= f'{API_BASE_URL}/{id}'
    response = requests.get(url)
    data = response.json()

    data = data['data']
   
    card = {"data": data}

    return render_template('card/card_detail.html', card = card)


############################################################################################
# USER SESSION 
 
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
############################################################################################
# HOMEPAGE ROUTES

@app.route('/')
def homepage():
    """Show homepage:

    - anonymous users: show sign up landing page
    - logged in: show main search page
    """

    url = f'{API_BASE_URL}/?q=name:m'
    response = requests.get(url)
    data = response.json()

    one = data['data'][0]
    two = data['data'][1]
    three = data['data'][4]
    four = data['data'][5]
    five = data['data'][9]

    cards = {"card1": one}, {"card2": two}, {"card3": three}, {"card4": four}, {"card5": five}

    return render_template('home.html', cards=cards, isIndex=True)
    
############################################################################################
# SIGNUP/LOGIN/LOGOUT ROUTES

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

############################################################################################
# USER ROUTES 

@app.route('/users')
def show_user_profile():
    """Show user profile."""

    user_id = g.user.id

    # retrieve the user's favorite cards to display on their profile;
    favorites = (Favorite
                .query
                .filter(Favorite.user_id == g.user.id)
                .limit(100)
                .all())

    
    return render_template('user/user.html', favorites=favorites)


@app.route('/users/profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile details for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    user = g.user
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):

            user.username = form.username.data
            user.email = form.email.data
            user.profile_image = form.profile_image.data or User.profile_image.default.arg

            db.session.commit()

            flash("Profile successfully updated.", "success")

            return redirect(f"/users/{user.id}")
        
        flash("Wrong password, please try again.", 'danger')

    return render_template('user/edit_user.html', form=form, user_id=user.id)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()


    flash('User has been deleted.' , "success")
    return redirect("/signup")
    



############################################################################################
# FAVORITE ROUTES 






############################################################################################
# ERROR HANDLERS

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_handlers/404.html'), 404


# https://stackoverflow.com/questions/24956894/sql-alchemy-queuepool-limit-overflow
# sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached, connection timed out, timeout 30.00 (Background on this error at: https://sqlalche.me/e/14/3o7r)

# https://stackoverflow.com/questions/57844921/good-practice-to-avoid-sqlalchemy-exc-timeouterror-queuepool-limit-of-size-5-ov

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()