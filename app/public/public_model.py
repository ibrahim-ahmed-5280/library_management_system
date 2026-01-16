import mysql.connector
from app.configuration import DbConfiguration
from mysql.connector import Error, IntegrityError
from flask_bcrypt import Bcrypt
from app import app
import datetime
from datetime import datetime, timedelta
bcrypt = Bcrypt(app)

class PublicDatabase:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def make_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(e)

    def my_cursor(self):
        return self.cursor


class PublicModel:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor(dictionary=True)

    def fetch_one(self, query, params=()):
            self.cursor.execute(query, params)
            return self.cursor.fetchone()

    def fetch_all(self, query, params=()):
            self.cursor.execute(query, params)
            return self.cursor.fetchall()

    def total_members(self):
        row = self.fetch_one("""
                             SELECT COUNT(*) AS total
                             FROM users
                             WHERE role = 'member'
                             """)
        return row['total'] if row else 0

    def total_books(self):
        row = self.fetch_one("SELECT COUNT(*) AS total FROM books")
        return row['total'] if row else 0

    def total_copies(self):
        row = self.fetch_one("SELECT COUNT(*) AS total FROM book_copies")
        return row['total'] if row else 0

    def total_categories(self):
        row = self.fetch_one("SELECT COUNT(*) AS total FROM categories")
        return row['total'] if row else 0



public_db_configuration = DbConfiguration()


def check_public_model_connection():
    try:
        mysql_connect = PublicDatabase(
            host=public_db_configuration.DB_HOSTNAME,
            port=3307,
            user=public_db_configuration.DB_USERNAME,
            password=public_db_configuration.DB_PASSWORD,
            database=public_db_configuration.DB_NAME
        )
        # Create an instance of the Store class
        mysql_connect.make_connection()
        my_public_model = PublicModel(mysql_connect.connection)

        return True, my_public_model
    except Exception as e:
        print(f'')
        return False, f'Error: {e}.'
