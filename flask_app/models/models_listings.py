from flask_app.config.mysqlconnection import connectToMySQL
from flask import session
db='car_list_db'

from flask import session

class Listings:
    @classmethod
    def create_listing(cls, make, model):
        query = "INSERT INTO listings (make, model, user_id) VALUES (%(make)s, %(model)s, %(user_id)s);"
        data = {
            'make': make,
            'model': model,
            'user_id': session.get('user_id')  # Assuming user_id is stored in the session
        }
        mysql = connectToMySQL('car_list_db')
        mysql.query_db(query, data)

    @classmethod
    def get_user_wishlist(cls, user_id):
        query = "SELECT make, model FROM listings WHERE user_id = %(user_id)s;"
        data = {'user_id': user_id}
        mysql = connectToMySQL('car_list_db')
        wishlist = mysql.query_db(query, data)
        return wishlist


@classmethod
def update_wishlist(cls, listings_id, new_make, new_model):
    mysql = connectToMySQL('car_list_db')
    query = "UPDATE listings SET make = %(make)s, model = %(model)s WHERE id = %(listings_id)s;"
    data = {
        'make': new_make,
        'model': new_model,
        'listings_id': listings_id
    }
    mysql.query_db(query, data)


