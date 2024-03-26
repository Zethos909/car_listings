from flask_app import app
from flask import render_template, request, redirect, url_for, flash, session, get_flashed_messages
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.models_users import User
from flask_app.models.models_listings import Listings
from flask_app.models.models_favorites import Favorites
from werkzeug.security import check_password_hash
from functools import wraps
import requests
from flask import request
from flask import jsonify, request, session
from flask_app import app
from flask_app.models.models_favorites import Favorites


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to log in to access this page", "login_error")
            return redirect(url_for('main_page'))  # Redirect to the login page
        return view_func(*args, **kwargs)
    return wrapped_view

@app.route('/dashboard')
@login_required
def dashboard():
    # API endpoint and API key
    api_endpoint = 'https://auto.dev/api/listings'
    api_key = 'ZrQEPSkKcmRnZXJtYW45OUBnbWFpbC5jb20='

    # Extract make and model query parameters from the request
    make = request.args.get('make')
    model = request.args.get('model')

    # Construct the query parameters for the API call
    params = {'apikey': api_key}
    if make:
        params['make'] = make
    if model:
        params['model'] = model

    # Make the API call with the constructed query parameters
    response = requests.get(api_endpoint, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Process the JSON data
        data = response.json()
        # Render the HTML template with the data
        return render_template('dashboard.html', data=data)
    else:
        return 'Error: Unable to fetch data from the API'


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        # Perform logout when the form is submitted
        session.pop('user_id', None)
        session.pop('first_name', None)
        session.pop('last_name', None)
        session.pop('email', None)
        flash("You have been logged out", "success")
        return redirect(url_for('main_page'))
    else:
        # Redirect to main_page if the logout page is accessed directly via GET
        return redirect(url_for('main_page'))


@app.route('/')
def index():
    return redirect('/main_page')

@app.route('/main_page')
def main_page():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/register', methods=['POST'])
def register():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    if len(first_name) < 2:
        flash("First name must be at least 2 characters", "register_error")
    if len(last_name) < 2:
        flash("Last name must be at least 2 characters", "register_error")
    if User.find_by_email(email):
        flash("Invalid email format or email already exists", "register_error")
    if len(password) < 8:
        flash("Password must be at least 8 characters", "register_error")
    if password != confirm_password:
        flash("Password and confirmation do not match", "register_error")
    if '_flashes' in session:
        return redirect(url_for('main_page'))
    User.create_user(first_name, last_name, email, password)
    flash("Registration successful!", "success")
    return redirect(url_for('main_page'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = User.find_by_email(email)
    if user:
        if check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['first_name'] = user.first_name
            session['last_name'] = user.last_name
            session['email'] = user.email
            flash(f"Logged in as {user.first_name} {user.last_name}", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password", "login_error")
            return redirect(url_for('main_page'))
    else:
        flash("Account does not exist. Please register first.", "login_error")
        return redirect(url_for('main_page'))

@app.route('/listing/<int:listing_id>')  # Update route
def view_listing(listing_id):  # Update function name
    if 'user_id' not in session:
        flash("You need to log in to access this page", "login_error")
        return redirect(url_for('main_page'))
    session_user_id = session['user_id']
    first_name = session['first_name']
    last_name = session['last_name']
    listing = Listings.get_listing_by_id(listing_id)  # Update to match the new model name
    if not listing:
        flash("Listing not found", "error")
        return redirect(url_for('dashboard'))
    favorites = Favorites.get_favorites(listing_id)  # Update to match the new model name
    favorite_users = []
    for favorite_info in favorites:
        if 'first_name' in favorite_info and 'last_name' in favorite_info:
            favorite_users.append(favorite_info)
    return render_template('view_listing.html', listing=listing, user_id=session_user_id, first_name=first_name, last_name=last_name, favorite_users=favorite_users)  # Update template name and variable names

@app.route('/account/<int:user_id>', methods=['POST'])
def update_account(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        flash("You need to log in to access this page", "login_error")
        return redirect(url_for('main_page'))
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    if len(first_name) < 2:
        flash("First name must be at least 2 characters", "error")
        return redirect(url_for('account'))  # Changed endpoint to 'account'
    if len(last_name) < 2:
        flash("Last name must be at least 2 characters", "error")
        return redirect(url_for('account'))  # Changed endpoint to 'account'
    if not User.is_valid_email(email):
        flash("Invalid email address", "error")
        return redirect(url_for('account'))  # Changed endpoint to 'account'
    if email != session['email'] and User.find_by_email(email):
        flash("Email address already exists", "error")
        return redirect(url_for('account'))  # Changed endpoint to 'account'
    User.update_user(user_id, first_name, last_name, email)
    flash("Account information updated successfully", "success")
    session['first_name'] = first_name  # Update session data
    session['last_name'] = last_name    # Update session data
    session['email'] = email            # Update session data
    return redirect(url_for('account'))  # Changed endpoint to 'account'




@app.route('/account', methods=['GET', 'POST'])
@login_required  # Apply login_required decorator
def account():
    if 'user_id' not in session:
        flash("You need to log in to access this page", "login_error")
        return redirect(url_for('main_page'))

    # Retrieve user information from session
    user_id = session['user_id']
    first_name = session['first_name']
    last_name = session['last_name']
    email = session['email']

    # Retrieve full user object from database based on user_id
    user = User.find_by_id(user_id)

    if request.method == 'POST':
        # Handle form submission
        # You can perform any necessary form processing here
        pass

    # Pass user information to the template
    return render_template('view_account.html', user=user, first_name=first_name, last_name=last_name, email=email)

@app.route('/favorites', methods=['GET', 'POST'])
@login_required
def favorites():
    if request.method == 'POST':
        # Handle favoriting a listing
        listing_id = request.form.get('listing_id')
        if listing_id:
            print("Listing ID:", listing_id)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'No listing ID provided'})
    else:
        # Handle API listing ID call
        api_listing_id = request.args.get('api_listing_id')
        if api_listing_id:
            # Get favorites for the given API listing ID using the Favorites class method
            favorites = Favorites.get_listing_favorites(api_listing_id)
            if favorites:
                return render_template('view_favorites.html', favorites=favorites)
            else:
                return "Failed to retrieve favorites for the listing ID."
        else:
            return "User not logged in"

@app.route('/favorite/<int:listing_id>', methods=['POST'])
@login_required
def favorite_listing(listing_id):
    print("Listing ID:", listing_id)
    return jsonify({'success': True})

from flask import request, redirect, url_for, session, render_template
from flask_app.config.mysqlconnection import connectToMySQL

from flask import session

from flask import render_template, request, redirect, url_for, session
from flask_app import app
from flask_app.models.models_listings import Listings

@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    if request.method == 'POST':
        # Retrieve make and model from the form data
        make = request.form.get('make')
        model = request.form.get('model')
        
        # Call create_listing to insert the new listing into the database
        Listings.create_listing(make, model)

        # Redirect to the wishlist page after submission
        return redirect(url_for('wishlist'))
    else:
        # Render the wishlist.html template for GET requests
        return render_template('wishlist.html')

@app.route('/view_wishlist', methods=['GET'])
def view_wishlist():
    user_id = session.get('user_id')
    wishlist = Listings.get_user_wishlist(user_id)
    return render_template('view_wishlist.html', wishlist=wishlist)

@app.route('/modify_wishlist/<int:listing_id>', methods=['GET', 'POST'])
def modify_wishlist(listing_id):
    if request.method == 'POST':
        # Get the new make and model from the form
        new_make = request.form.get('make')
        new_model = request.form.get('model')

        # Update the wishlist for the specified listing_id
        Listings.update_wishlist(listing_id, new_make, new_model)

        # Redirect to the view wishlist page
        return redirect(url_for('view_wishlist'))
    else:
        # Retrieve the current make and model of the car with the given listing_id
        current_listing = Listings.get_listing_by_id(listing_id)
        current_make = current_listing['make']
        current_model = current_listing['model']

        # Render the modify wishlist form with the current make and model pre-filled
        return render_template('modify_wishlist.html', listing_id=listing_id, current_make=current_make, current_model=current_model)
























