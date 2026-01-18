import mysql.connector
from app.configuration import DbConfiguration
from mysql.connector import Error, IntegrityError
from flask_bcrypt import Bcrypt
from app import app
import datetime
from datetime import datetime, timedelta

bcrypt = Bcrypt(app)


class MemberDatabase:
    def __init__(self, host, port, user, password, database, use_pure=False):
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


class MemberModel:
    def __init__(self, connection):
        try:
            self.connection = connection
            self.cursor = connection.cursor()
        except Exception as err:
            print('Something went wrong! Internet connection or database connection. (member DB)')
            print(f'Error: {err}')

    # ==============================================#
    # =========== CHECKING OPERATIONS ==============#
    # check member login
    def check_login_member(self, email):
        sql = """
              SELECT * \
              FROM users
              WHERE email = %s \
                AND role = 'member' AND status = 'active';"""

        try:
            self.cursor.execute(sql, (email,))
            result = self.cursor.fetchall()
            if result:
                print(f'Gets the member user with email {email}.')
                result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                return True, result
            else:
                print(f'Not get member user {email}.')
                return False, {}
        except Exception as e:
            print(f'Error: {e}')
            return False, f'Error {e}.'

    def is_member_request(self, member_id, edition_id):
        # Added parentheses around the request_types
        sql = """
              SELECT * \
              FROM requests
              WHERE edition_id = %s
                AND member_id = %s
                AND (status = 'pending' OR request_type = 'approved');
              """

        try:
            self.cursor.execute(sql, (edition_id, member_id))
            result = self.cursor.fetchall()
            if result:
                # Convert to list of dictionaries
                result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]
                return True, result
            else:
                return False, []
        except Exception as e:
            print(f'Error: {e}')
            return False, []

    def has_reached_limit(self, member_id, request_type):
        """
        Checks if a member has reached the policy limit for borrowing or reserving.
        Only considers requests with status 'pending' or 'approved'.
        """
        # 1. Determine the policy key based on the request type
        if request_type == 'borrow':
            policy_key = 'allowed_borrow'
        elif request_type == 'reserve':
            policy_key = 'allowed_reserve'
        else:
            return True, "Invalid request type"

        try:
            # 2. Get the limit value from library_policies
            policy_sql = "SELECT policy_value FROM library_policies WHERE policy_key = %s"
            self.cursor.execute(policy_sql, (policy_key,))
            policy_result = self.cursor.fetchone()

            # Default to 3 if policy is missing in DB
            limit = int(policy_result[0]) if policy_result else 3

            # 3. Count active requests for this member
            # We only count 'pending' and 'approved' as they are "active"
            count_sql = """
                        SELECT COUNT(*)
                        FROM requests
                        WHERE member_id = %s
                          AND request_type = %s
                          AND status IN ('pending', 'approved') \
                        """
            self.cursor.execute(count_sql, (member_id, request_type))
            current_count = self.cursor.fetchone()[0]

            # 4. Logic Check
            if current_count >= limit:
                return True, f"Limit reached! You already have {current_count} {request_type} requests active (Pending/Approved)."

            return False, "Under limit"

        except Exception as e:
            print(f"Error checking limit: {e}")
            # Return True on error to be safe (prevents bypass)
            return True, "System error verifying limits."

    # ==============================================#
    # ========== INSERT OPERATIONS =================#
    def create_borrow_request(self, member_id, edition_id):

        sql = """
              INSERT INTO requests
                  (member_id, edition_id, request_type, status, initiated_by)
              VALUES (%s, %s, 'borrow', 'pending', 'member') \
              """

        try:
            self.cursor.execute(sql, (member_id, edition_id))
            self.connection.commit()
            return True

        except Exception as e:
            print(f"Error: {e}")
            self.connection.rollback()
            return False

    def create_reserve_request(self, member_id, edition_id):

        sql = """
              INSERT INTO requests
                  (member_id, edition_id, request_type, status, initiated_by)
              VALUES (%s, %s, 'reserve', 'pending', 'member') \
              """

        try:
            self.cursor.execute(sql, (member_id, edition_id))
            self.connection.commit()
            return True

        except Exception as e:
            print(f"Error: {e}")
            self.connection.rollback()
            return False

    # ==============================================#
    # ========== READ OPERATIONS =================#
    ### 1. Total Books Borrowed (All-time)
    def get_total_borrowed_count(self, member_id):
        sql = "SELECT COUNT(*) as total FROM issues WHERE member_id = %s"
        try:
            self.cursor.execute(sql, (member_id,))
            result = self.cursor.fetchone()
            return True, result[0] if result else 0
        except Exception as e:
            print(f'Error: {e}')
            return False, 0

    ### 2. Currently Borrowed (Books in possession)
    def get_currently_borrowed_count(self, member_id):
        sql = "SELECT COUNT(*) as total FROM issues WHERE member_id = %s AND status = 'borrowed'"
        try:
            self.cursor.execute(sql, (member_id,))
            result = self.cursor.fetchone()
            return True, result[0] if result else 0
        except Exception as e:
            print(f'Error: {e}')
            return False, 0

    ### 3. Available to Borrow (Total available copies in library)
    def get_available_books_count(self):
        sql = "SELECT COUNT(*) as total FROM book_copies WHERE status = 'available'"
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return True, result[0] if result else 0
        except Exception as e:
            print(f'Error: {e}')
            return False, 0

    ### 4. Overdue Books
    def get_overdue_count(self, member_id):
        # Returns count where return_date is null and due_date has passed
        sql = """
              SELECT COUNT(*) as total \
              FROM issues
              WHERE member_id = %s
                AND status = 'borrowed'
                AND due_date < CURDATE()
              """
        try:
            self.cursor.execute(sql, (member_id,))
            result = self.cursor.fetchone()
            return True, result[0] if result else 0
        except Exception as e:
            print(f'Error: {e}')
            return False, 0

    ### 5. Reserved Books
    def get_reserved_count(self, member_id):
        sql = "SELECT COUNT(*) as total FROM requests WHERE member_id = %s AND request_type = 'reserve'"
        try:
            self.cursor.execute(sql, (member_id,))
            result = self.cursor.fetchone()
            return True, result[0] if result else 0
        except Exception as e:
            print(f'Error: {e}')
            return False, 0

    ### 6. In-Library Reading (Active sessions)
    def get_active_reading_sessions_count(self, member_id):
        sql = "SELECT COUNT(*) as total FROM reading_sessions WHERE member_id = %s AND end_time IS NULL"
        try:
            self.cursor.execute(sql, (member_id,))
            result = self.cursor.fetchone()
            return True, result[0] if result else 0
        except Exception as e:
            print(f'Error: {e}')
            return False, 0

    ### 7. Total Reading Hours (All-time)
    def get_total_reading_hours(self, member_id):
        # Calculates sum of hours between start and end time
        sql = """
              SELECT SUM(TIMESTAMPDIFF(HOUR, start_time, end_time)) as total_hours
              FROM reading_sessions
              WHERE member_id = %s \
                AND end_time IS NOT NULL
              """
        try:
            self.cursor.execute(sql, (member_id,))
            result = self.cursor.fetchone()
            return True, result[0] if result and result[0] else 0
        except Exception as e:
            print(f'Error: {e}')
            return False, 0

    ### 8. Monthly Reading Hours
    def get_monthly_reading_hours(self, member_id):
        sql = """
              SELECT SUM(TIMESTAMPDIFF(HOUR, start_time, end_time)) as monthly_hours
              FROM reading_sessions
              WHERE member_id = %s
                  AND end_time IS NOT NULL
                  AND MONTH ( \
                  start_time) = MONTH (CURRENT_DATE ())
                AND YEAR (start_time) = YEAR (CURRENT_DATE ())
              """
        try:
            self.cursor.execute(sql, (member_id,))
            result = self.cursor.fetchone()
            return True, result[0] if result and result[0] else 0
        except Exception as e:
            print(f'Error: {e}')
            return False, 0

    def view_books(self):
        sql = """
              SELECT b.book_id, \
                       b.title, \
                       b.description, \
                       b.created_at, \

                       a.name                       AS author_name, \
                       a.author_id                 AS author_id,     \
                       cgy.name                     AS category_name, \

                       COUNT(DISTINCT e.edition_id) AS editions_count, \
                       COUNT(c.copy_id)             AS copies_count

                FROM books b
                         JOIN authors a ON a.author_id = b.author_id
                         LEFT JOIN categories cgy ON cgy.category_id = b.category_id
                         JOIN editions e ON e.book_id = b.book_id
                         LEFT JOIN book_copies c ON c.edition_id = e.edition_id

                GROUP BY b.book_id
                ORDER BY b.created_at DESC"""

        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            if result:
                result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                return result
            else:
                return {}
        except Exception as e:
            print(f'Error: {e}')
            return False, f'Error {e}.'

    def view_member_requests(self, member_id):
        sql = """
              SELECT r.request_id, \
                     r.request_type, \
                     r.status AS request_status,\
                     r.request_date, \
                     r.decision_date, \
                     r.note, \

                     b.book_id, \
                     b.title AS book_title, \

                     e.edition_id, \
                     e.edition_number, \
                     e.publisher, \
                     e.publication_year

              FROM requests r
                       JOIN editions e ON e.edition_id = r.edition_id
                       JOIN books b ON b.book_id = e.book_id

              WHERE r.member_id = %s
                AND r.status IN ('borrow', 'reserve')

              ORDER BY r.request_date DESC \
              """

        try:
            self.cursor.execute(sql, (member_id,))
            result = self.cursor.fetchall()

            if result:
                result = [
                    dict(zip([key[0] for key in self.cursor.description], row))
                    for row in result
                ]
                return result
            else:
                return {}

        except Exception as e:
            print(f'Error: {e}')
            return False, f'Error {e}.'

    def view_categories(self):
        sql = "SELECT category_id, name FROM categories ORDER BY name ASC"

        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()

            if result:
                return [
                    dict(zip([key[0] for key in self.cursor.description], row))
                    for row in result
                ]
            return {}

        except Exception as e:
            print(f"Error: {e}")
            return False

    def search_books(self, keyword=None, category_id=None):
        sql = """
              SELECT b.book_id, \
                     b.title, \
                     a.name             AS author_name, \
                     c.name             AS category_name, \

                     e.edition_id, \
                     COUNT(cpy.copy_id) AS available_copies

              FROM books b
                       JOIN authors a ON a.author_id = b.author_id
                       LEFT JOIN categories c ON c.category_id = b.category_id
                       JOIN editions e ON e.book_id = b.book_id
                       LEFT JOIN book_copies cpy
                                 ON cpy.edition_id = e.edition_id
                                     AND cpy.status = 'available'
              WHERE 1 = 1 \
              """

        params = []

        if keyword:
            sql += " AND (b.title LIKE %s OR a.name LIKE %s)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        if category_id:
            sql += " AND b.category_id = %s"
            params.append(category_id)

        sql += """
            GROUP BY e.edition_id
            ORDER BY b.title ASC
        """

        try:
            self.cursor.execute(sql, params)
            result = self.cursor.fetchall()

            if result:
                return [
                    dict(zip([key[0] for key in self.cursor.description], row))
                    for row in result
                ]
            return {}

        except Exception as e:
            print(f"Error: {e}")
            return False

    def view_currently_borrowed_books(self, member_id):
        sql = """
              SELECT i.issue_id,
                     b.title                         AS book_title,
                     i.issue_date                    AS borrow_date,
                     i.due_date,
                     DATEDIFF(i.due_date, CURDATE()) AS days_left

              FROM issues i
                       JOIN book_copies bc ON i.copy_id = bc.copy_id
                       JOIN editions e ON bc.edition_id = e.edition_id
                       JOIN books b ON e.book_id = b.book_id

              WHERE i.member_id = %s
                AND i.return_date IS NULL
                AND i.status = 'borrowed'

              ORDER BY i.due_date ASC
              """

        try:
            self.cursor.execute(sql, (member_id,))
            result = self.cursor.fetchall()

            if result:
                return [
                    dict(zip([key[0] for key in self.cursor.description], row))
                    for row in result
                ]
            else:
                return []

        except Exception as e:
            print(f'Error: {e}')
            return False

    def view_member_borrowing_history(self, member_id):
        sql = """
              SELECT i.issue_id,
                     b.title      AS book_title,
                     i.issue_date AS borrow_date,
                     i.due_date,
                     i.return_date,
                     CASE
                         WHEN i.return_date IS NOT NULL THEN 'Returned'
                         WHEN i.due_date < CURDATE() THEN 'Overdue'
                         ELSE 'Borrowed'
                         END      AS status,
                     f.amount     AS fine_amount

              FROM issues i
                       JOIN book_copies bc ON i.copy_id = bc.copy_id
                       JOIN editions e ON bc.edition_id = e.edition_id
                       JOIN books b ON e.book_id = b.book_id
                       LEFT JOIN fines f ON i.issue_id = f.issue_id

              WHERE i.member_id = %s
              ORDER BY i.issue_date DESC
              """

        try:
            self.cursor.execute(sql, (member_id,))
            result = self.cursor.fetchall()

            if result:
                return [
                    dict(zip([key[0] for key in self.cursor.description], row))
                    for row in result
                ]
            else:
                return []

        except Exception as e:
            print(f'Error: {e}')
            return False

    def view_member_reading_sessions(self, member_id):
        sql = """
              SELECT rs.reading_id,
                     rs.start_time,
                     rs.end_time,
                     b.title AS book_title,
                     CASE
                         WHEN rs.end_time IS NULL THEN 'In Use'
                         ELSE 'Finished'
                         END AS status
              FROM reading_sessions rs
                       JOIN book_copies bc ON rs.copy_id = bc.copy_id
                       JOIN editions e ON bc.edition_id = e.edition_id
                       JOIN books b ON e.book_id = b.book_id
              WHERE rs.member_id = %s
              ORDER BY rs.start_time DESC
              """

        try:
            self.cursor.execute(sql, (member_id,))
            result = self.cursor.fetchall()

            if result:
                # Converts rows into a list of dictionaries
                return [
                    dict(zip([key[0] for key in self.cursor.description], row))
                    for row in result
                ]
            else:
                return []  # Return empty list if no records found

        except Exception as e:
            print(f'Error: {e}')
            return False

    def view_member_fines(self, member_id):
        sql = """
              SELECT f.fine_id,
                     f.amount                                               AS fine_amount,
                     f.paid_status                                          AS payment_status,
                     i.due_date,
                     i.return_date,
                     b.title                                                AS book_title,
                  /* Calculate days overdue: use return_date if exists, else use current date */
                     DATEDIFF(IFNULL(i.return_date, CURDATE()), i.due_date) AS days_overdue
              FROM fines f
                       JOIN issues i ON f.issue_id = i.issue_id
                       JOIN book_copies bc ON i.copy_id = bc.copy_id
                       JOIN editions e ON bc.edition_id = e.edition_id
                       JOIN books b ON e.book_id = b.book_id
              WHERE f.member_id = %s
              ORDER BY f.paid_status DESC, i.due_date DESC
              """

        try:
            self.cursor.execute(sql, (member_id,))
            result = self.cursor.fetchall()

            if result:
                return [
                    dict(zip([key[0] for key in self.cursor.description], row))
                    for row in result
                ]
            else:
                return []

        except Exception as e:
            print(f'Error fetching fines: {e}')
            return False

    # ==============================================#
    # ========== UPDATE OPERATIONS =================#
    def cancel_request(self, request_id):
            sql = """
                  UPDATE requests
                  SET status = 'cancelled'
                  WHERE request_id = %s; \
                  """
            try:
                self.cursor.execute(sql, (request_id,))
                self.connection.commit()  # Commit the transaction
                print(f"success happen.")
                return True
            except Exception as e:
                print(f"Error: {e}")
                print(f'there is an error happen.')
                return False

    def update_member_details(self, member_data):
        print("in modal", member_data)
        """
        Update member data
        """
        sql = """
              UPDATE users \
              SET name     = %s, \
                  email = %s
              WHERE user_id = %s; \
              """

        try:
            values = (
                member_data.get('name'),
                member_data.get('email'),  # address is optional
                int(member_data.get('member_id'))
            )

            self.cursor.execute(sql, values)
            self.connection.commit()

            if self.cursor.rowcount == 0:
                return False, 'No member found with that ID or no changes made'

            return True, 'User details updated successfully'

        except Exception as e:
            self.connection.rollback()
            print(f"Error updating member details: {str(e)}")

            # Handle duplicate email/phone errors
            if "Duplicate entry" in str(e) and "email" in str(e):
                return False, 'Email is already in use by another user'
            if "Duplicate entry" in str(e) and "phone" in str(e):
                return False, 'Phone number is already in use by another user'

            return False, f'Database error: {str(e)}'

    # change member password
    def change_member_password(self, password, member_id):
            sql = """
                  UPDATE users
                  SET password = %s
                  WHERE user_id = %s; \
                  """
            try:
                self.cursor.execute(sql, (password, member_id))
                self.connection.commit()  # Commit the transaction
                print(f"success happen.")
                return True
            except Exception as e:
                print(f"Error: {e}")
                print(f'there is an error happen.')
                return False


member_db_configuration = DbConfiguration()


def check_member_model_connection():
    try:
        mysql_connect = MemberDatabase(
            host=member_db_configuration.DB_HOSTNAME,
            port=3307,
            user=member_db_configuration.DB_USERNAME,
            password=member_db_configuration.DB_PASSWORD,
            database=member_db_configuration.DB_NAME,
            use_pure=True
        )
        # Create an instance of the Store class
        mysql_connect.make_connection()
        my_member_model = MemberModel(mysql_connect.connection)

        return True, my_member_model
    except Exception as e:
        print(f'')
        return False, f'Error: {e}.'
