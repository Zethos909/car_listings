from flask_app.config.mysqlconnection import connectToMySQL
from werkzeug.security import generate_password_hash, check_password_hash

db = "car_list_db"

class User:
    def __init__(self, id, first_name, last_name, email, password, created_at, updated_at ):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def create_user(cls, first_name, last_name, email, password):
        password_hash = generate_password_hash(password)
        query = """
                INSERT INTO user (first_name, last_name, email, password)
                VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password_hash)s)
                """
        data = {
            'first_name' : first_name,
            'last_name' : last_name,
            'email' : email,
            'password_hash': password_hash
        }
        mysql = connectToMySQL(db)
        mysql.query_db(query, data)

    @classmethod
    def find_by_id(cls, user_id):
        query = """
                SELECT * FROM user WHERE id = %(id)s
                """
        data = {
            'id' : user_id
        }
        mysql = connectToMySQL(db)
        result = mysql.query_db(query, data)
        return cls(**result[0]) if result else None

    @classmethod
    def find_by_email(cls, email):
        query = """
                SELECT * FROM user WHERE email = %(email)s
                """
        data = {
            'email': email
        }
        mysql = connectToMySQL(db)
        result = mysql.query_db(query, data)
        if result and result[0]:
            return cls(**result[0])
        else:
            return None


    @classmethod
    def update_user(cls, user_id, first_name, last_name, email):
        query = """
                UPDATE user
                SET first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s, updated_at = NOW()
                WHERE id = %(user_id)s
                """
        data = {
            'user_id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email
        }
        mysql = connectToMySQL(db)
        mysql.query_db(query, data)

    @staticmethod
    def is_valid_email(email):
        return '@' in email and '.' in email
