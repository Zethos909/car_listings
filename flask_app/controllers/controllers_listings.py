from flask_app import app
from flask import render_template, request, redirect, url_for, flash, session, get_flashed_messages
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.models_users import User
from flask_app.models.models_listings import Listings
from flask_app.models.models_favorites import Favorites
from werkzeug.security import check_password_hash
from functools import wraps
import requests
from flask import jsonify


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to log in to access this page", "login_error")
            return redirect(url_for('main_page'))
        return view_func(*args, **kwargs)
    return wrapped_view

@app.route('/dashboard')
@login_required
def dashboard():
    api_endpoint = 'https://auto.dev/api/listings'
    api_key = 'ZrQEPSkKcmRnZXJtYW45OUBnbWFpbC5jb20='
    make = request.args.get('make')
    model = request.args.get('model')
    params = {'apikey': api_key}
    if make:
        params['make'] = make
    if model:
        params['model'] = model
    response = requests.get(api_endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        return render_template('dashboard.html', data=data)
    else:
        return 'Error: Unable to fetch data from the API'


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.pop('user_id', None)
        session.pop('first_name', None)
        session.pop('last_name', None)
        session.pop('email', None)
        flash("You have been logged out", "success")
        return redirect(url_for('main_page'))
    else:
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

@app.route('/listing/<int:listing_id>')
def view_listing(listing_id):
    if 'user_id' not in session:
        flash("You need to log in to access this page", "login_error")
        return redirect(url_for('main_page'))
    session_user_id = session['user_id']
    first_name = session['first_name']
    last_name = session['last_name']
    listing = Listings.get_listing_by_id(listing_id)
    if not listing:
        flash("Listing not found", "error")
        return redirect(url_for('dashboard'))
    favorites = Favorites.get_favorites(listing_id)
    favorite_users = []
    for favorite_info in favorites:
        if 'first_name' in favorite_info and 'last_name' in favorite_info:
            favorite_users.append(favorite_info)
    return render_template('view_listing.html', listing=listing, user_id=session_user_id, first_name=first_name, last_name=last_name, favorite_users=favorite_users)

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
        return redirect(url_for('account'))
    if len(last_name) < 2:
        flash("Last name must be at least 2 characters", "error")
        return redirect(url_for('account'))
    if not User.is_valid_email(email):
        flash("Invalid email address", "error")
        return redirect(url_for('account'))
    if email != session['email'] and User.find_by_email(email):
        flash("Email address already exists", "error")
        return redirect(url_for('account'))
    User.update_user(user_id, first_name, last_name, email)
    flash("Account information updated successfully", "success")
    session['first_name'] = first_name
    session['last_name'] = last_name
    session['email'] = email
    return redirect(url_for('account'))




@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if 'user_id' not in session:
        flash("You need to log in to access this page", "login_error")
        return redirect(url_for('main_page'))
    user_id = session['user_id']
    first_name = session['first_name']
    last_name = session['last_name']
    email = session['email']
    user = User.find_by_id(user_id)
    if request.method == 'POST':
        pass
    return render_template('view_account.html', user=user, first_name=first_name, last_name=last_name, email=email)

@app.route('/favorites', methods=['GET', 'POST'])
@login_required
def favorites():
    if request.method == 'POST':
        listing_id = request.form.get('listing_id')
        if listing_id:
            print("Listing ID:", listing_id)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'No listing ID provided'})
    else:
        api_listing_id = request.args.get('api_listing_id')
        if api_listing_id:
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

@app.route('/wishlist', methods=['GET', 'POST'])
@login_required
def wishlist():
    if request.method == 'POST':
        make = request.form.get('make')
        model = request.form.get('model')
        Listings.create_listing(make, model)
        return redirect(url_for('wishlist'))
    else:
        return render_template('wishlist.html')

@app.route('/view_wishlist', methods=['GET'])
@login_required
def view_wishlist():
    user_id = session.get('user_id')
    wishlist = Listings.get_user_wishlist(user_id)
    return render_template('view_wishlist.html', wishlist=wishlist)


@app.route('/modify_wishlist/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def modify_wishlist(listing_id):
    if request.method == 'POST':
        new_make = request.form.get('make')
        new_model = request.form.get('model')
        Listings.update_wishlist(listing_id, new_make, new_model)
        return redirect(url_for('view_wishlist'))
    else:
        current_listing = Listings.get_user_wishlist(session.get('user_id'))
        current_listing = [listing for listing in current_listing if listing['id'] == listing_id]
        if current_listing:
            current_listing = current_listing[0]
            current_make = current_listing['make']
            current_model = current_listing['model']
            return render_template('modify_wishlist.html', listing_id=listing_id, current_make=current_make, current_model=current_model)
        else:
            flash('Listing not found', 'error')
            return redirect(url_for('view_wishlist'))

@app.route('/delete_listing/<int:listing_id>', methods=['POST'])
@login_required
def delete_listing(listing_id):
    Listings.delete_listing(listing_id)
    return redirect(url_for('view_wishlist'))





















