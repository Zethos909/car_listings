from flask_app.config.mysqlconnection import connectToMySQL

db = 'car_list_db'

import requests

class Favorites:
    def __init__(self, id, user_id, listing_id):
        self.id = id
        self.user_id = user_id
        self.listing_id = listing_id

    @staticmethod
    def get_listing_favorites(api_listing_id):
        # Make an API call to retrieve favorites associated with the given API listing ID
        api_endpoint = f'https://example.com/api/favorites?listing_id={api_listing_id}'
        response = requests.get(api_endpoint)

        if response.status_code == 200:
            favorites = response.json()
            return favorites
        else:
            return None











