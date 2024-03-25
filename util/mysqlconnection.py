import MySQLdb

def connect_to_mysql():
    # Database configuration
    host = 'localhost'
    user = 'root'
    password = 'root'
    database = 'car_list_db'

    try:
        # Connect to the database
        conn = MySQLdb.connect(host=host, user=user, password=password, database=database)
        print("Connection successful!")
        return conn
    except MySQLdb.Error as e:
        print("Error connecting to the database:", e)
        return None

def close_mysql_connection(conn):
    try:
        # Close the connection
        conn.close()
        print("Connection closed successfully!")
    except MySQLdb.Error as e:
        print("Error closing the database connection:", e)
