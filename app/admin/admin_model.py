import mysql.connector
from app.configuration import DbConfiguration
from mysql.connector import Error, IntegrityError
from flask_bcrypt import Bcrypt
from app import app
import datetime
from datetime import datetime, timedelta
bcrypt = Bcrypt(app)

class AdminDatabase:
    def __init__(self, host, port, user, password, database,use_pure = False):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.use_pure = use_pure

    def make_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                use_pure=self.use_pure
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(e)

    def my_cursor(self):
        return self.cursor


class AdminModel:
    def __init__(self, connection):
        try:
            self.connection = connection
            self.cursor = connection.cursor()
        except Exception as err:
            print('Something went wrong! Internet connection or database connection. (Admin DB)')
            print(f'Error: {err}')

    #==============================================#
    #=========== CHECKING OPERATIONS ==============#

    # check admin login
    def check_login_admin(self, email):
            sql = """
            SELECT * FROM users
            WHERE email = %s and role = 'admin';"""

            try:
                self.cursor.execute(sql, (email,))
                result = self.cursor.fetchall()
                if result:
                    print(f'Gets the admin user with email {email}.')
                    result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                    return True, result
                else:
                    print(f'Not get admin user {email}.')
                    return False, {}
            except Exception as e:
                print(f'Error: {e}')
                return False, f'Error {e}.'

    # check if email already exist
    def check_email_exist(self, email,user_id = None):
        if user_id is not None:
            sql = """
                SELECT * FROM users
                WHERE email = %s AND user_id != %s;"""
            values = (email, user_id)
        else:
            sql = """
                SELECT * FROM users
                WHERE email = %s"""
            values = (email,)

        try:
            self.cursor.execute(sql, values)
            result = self.cursor.fetchall()
            if result:
                print(f'Gets this email {email}.')
                result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                return True, result
            else:
                print(f'Not get this email {email}.')
                return False, {}
        except Exception as e:
            print(f'Error: {e}')
            return False, f'Error {e}.'

    # check policy_key if exits or not
    def check_policy_key_exist(self, policy_key,policy_id = None):
        if policy_id is not None:
            query = "SELECT policy_id FROM library_policies WHERE policy_key = %s AND policy_id != %s"
            values = (policy_key,policy_id)
        else:
            query = "SELECT policy_id FROM library_policies WHERE policy_key = %s"
            values = (policy_key,)
        self.cursor.execute(query, values)
        return (self.cursor.fetchone() is not None), None

    #==============================================#
    #========== INSERT OPERATIONS =================#

    # insert admin data
    def add_admin(self, name, email, password):
            try:
                query = """
                INSERT INTO users (name, email,password)
                VALUES (%s, %s, %s)
                          """
                self.cursor.execute(query, (name, email, password))
                self.connection.commit()
                return True, 'Admin registered successfully.'
            except Exception as e:
                self.connection.rollback()
                print('Database insert error:', str(e))
                return False, str(e)

    # insert librarian data
    def add_librarian(self, name, email, password):
        try:
            query = """
                    INSERT INTO users (name, email,password,role)
                    VALUES (%s, %s, %s, 'librarian')
                              """
            self.cursor.execute(query, (name, email, password))
            self.connection.commit()
            return True, 'Librarian registered successfully.'
        except Exception as e:
            self.connection.rollback()
            print('Database insert error:', str(e))
            return False, str(e)

    # insert member data
    def add_member(self, name, email, password, membership_type, start_date, end_date):
        try:
            query = """
                INSERT INTO users (
                    name,
                    email,
                    password,
                    role,
                    membership_type,
                    membership_status,
                    membership_start,
                    membership_end
                )
                VALUES (%s, %s, %s, 'member', %s, 'active', %s, %s)
            """
            self.cursor.execute(
                query,
                (name, email, password, membership_type, start_date, end_date)
            )
            self.connection.commit()
            return True, 'Member registered successfully.'
        except Exception as e:
            self.connection.rollback()
            print('Database insert error:', str(e))
            return False, str(e)

    # insert policy data
    def add_policy(self, name, key, value, description,user_id):
        query = """
            INSERT INTO library_policies
            (policy_name, policy_key, policy_value, description, created_by)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(query, (
                name, key, value, description, user_id
            ))
            self.connection.commit()
            return True, "Policy registered successfully."
        except Exception as e:
            self.connection.rollback()
            return False, str(e)

    # ==============================================#
    # ========== READ OPERATIONS =================#

    # READ ALL LIBRARIANS FROM USERS TABLE
    def get_all_admins(self):
        sql = """
                    SELECT * FROM users 
                    WHERE role = 'admin';"""

        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            if result:
                print('Gets Admins.')
                result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                return True, result
            else:
                print('Not get any admins.')
                return False, {}
        except Exception as e:
            print(f'Error: {e}')
            return False, f'Error {e}.'

    # READ ALL LIBRARIANS FROM USERS TABLE
    def get_all_librarians(self):
        sql = """
                SELECT * FROM users 
                WHERE role = 'librarian';"""

        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            if result:
                print('Gets librarians.')
                result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                return True, result
            else:
                print('Not get any librarians.')
                return False, {}
        except Exception as e:
            print(f'Error: {e}')
            return False, f'Error {e}.'

    # READ ALL MEMBERS FROM USERS TABLE
    def get_all_members(self):
            sql = """
                    SELECT * FROM users 
                    WHERE role = 'member';"""

            try:
                self.cursor.execute(sql)
                result = self.cursor.fetchall()
                if result:
                    print('Gets Members.')
                    result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                    return True, result
                else:
                    print('Not get any Members.')
                    return False, {}
            except Exception as e:
                print(f'Error: {e}')
                return False, f'Error {e}.'

    # READ ALL POLICIES
    def get_all_policies(self):
            sql = """
                    SELECT
                        p.policy_id,
                        p.policy_name,
                        p.policy_key,
                        p.policy_value,
                        p.description,
                    
                        u1.name AS created_by,
                        u2.name AS updated_by,
                    
                        p.created_at,
                        p.updated_at
                    
                    FROM library_policies p
                    
                    LEFT JOIN users u1
                        ON p.created_by = u1.user_id
                    
                    LEFT JOIN users u2
                        ON p.updated_by = u2.user_id
                    
                    ORDER BY p.policy_id DESC;
"""

            try:
                self.cursor.execute(sql)
                result = self.cursor.fetchall()
                if result:
                    print('Gets Policies.')
                    result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                    return True, result
                else:
                    print('Not get any Policies.')
                    return False, {}
            except Exception as e:
                print(f'Error: {e}')
                return False, f'Error {e}.'


    #==============================================#
    #========== UPDATE OPERATIONS =================#

    #update admin and librarian details
    def update_user(self, name, email,status,user_id):
            sql = """
                   UPDATE users 
                   SET name = %s , email = %s , status = %s 
                   WHERE user_id = %s;
                  """
            try:
                self.cursor.execute(sql, (name, email,status,user_id))
                self.connection.commit()  # Commit the transaction
                print(f"User updated successfully.")
                return True,f'User updated successfully.'""
            except Exception as e:
                print(f"Error: {e}")
                print(f'there is an error happen.')
                return False,f"Error {e}."

    # update member details
    def update_member(self, name,email,membership_type,start_date,end_date,status,user_id):
        sql = """
                       UPDATE users 
                       SET name = %s , 
                       email = %s ,
                       membership_type = %s,
                       membership_start = %s,
                       membership_end = %s,
                       status = %s 
                       WHERE user_id = %s;
                      """
        try:
            self.cursor.execute(sql, (name, email,membership_type,start_date,end_date,status, user_id))
            self.connection.commit()  # Commit the transaction
            print(f"Member updated successfully.")
            return True, f'Member updated successfully.'""
        except Exception as e:
            print(f"Error: {e}")
            print(f'there is an error happen.')
            return False, f"Error {e}."

    #update user password
    def update_user_password(self, password, user_id):
            sql = """
                   UPDATE users 
                   SET password = %s 
                   WHERE user_id = %s;
                  """
            try:
                self.cursor.execute(sql, (password,user_id))
                self.connection.commit()  # Commit the transaction
                print(f"User password updated successfully.")
                return True,f'User password updated successfully.'""
            except Exception as e:
                print(f"Error: {e}")
                print(f'there is an error happen.')
                return False,f"Error {e}."

    # update policy details
    def update_policy(self, policy_name, policy_key, policy_value, description, user_id):
        sql = """
               UPDATE library_policies 
               SET policy_name = %s , 
               policy_key = %s ,
               policy_value = %s,
               description = %s,
               updated_by = %s;
              """
        try:
            self.cursor.execute(sql, (policy_name, policy_key, policy_value, description,user_id))
            self.connection.commit()  # Commit the transaction
            print(f"Member updated successfully.")
            return True, f'Member updated successfully.'""
        except Exception as e:
            print(f"Error: {e}")
            print(f'there is an error happen.')
            return False, f"Error {e}."

admin_db_configuration = DbConfiguration()


def check_admin_model_connection():
    try:
        mysql_connect = AdminDatabase(
            host=admin_db_configuration.DB_HOSTNAME,
            port=3307,
            user=admin_db_configuration.DB_USERNAME,
            password=admin_db_configuration.DB_PASSWORD,
            database=admin_db_configuration.DB_NAME,
            use_pure = True
        )
        # Create an instance of the Store class
        mysql_connect.make_connection()
        my_admin_model = AdminModel(mysql_connect.connection)

        return True, my_admin_model
    except Exception as e:
        print(f'')
        return False, f'Error: {e}.'
