import mysql.connector
from app.configuration import DbConfiguration
from mysql.connector import Error, IntegrityError
from flask_bcrypt import Bcrypt
from app import app
import datetime
from datetime import datetime, timedelta
bcrypt = Bcrypt(app)

class UserDatabase:
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


class UserModel:
    def __init__(self, connection):
        try:
            self.connection = connection
            self.cursor = connection.cursor()
        except Exception as err:
            print('Something went wrong! Internet connection or database connection. (user DB)')
            print(f'Error: {err}')


user_db_configuration = DbConfiguration()


def check_user_model_connection():
    try:
        mysql_connect = UserDatabase(
            host=user_db_configuration.DB_HOSTNAME,
            port=3306,
            user=user_db_configuration.DB_USERNAME,
            password=user_db_configuration.DB_PASSWORD,
            database=user_db_configuration.DB_NAME
        )
        # Create an instance of the Store class
        mysql_connect.make_connection()
        my_user_model = UserModel(mysql_connect.connection)

        return True, my_user_model
    except Exception as e:
        print(f'')
        return False, f'Error: {e}.'
