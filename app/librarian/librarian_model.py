import mysql.connector
from mysql.connector import IntegrityError
from app.configuration import DbConfiguration
from flask_bcrypt import Bcrypt
from app import app

bcrypt = Bcrypt(app)


# ===================== DATABASE CONNECTION ===================== #

class LibrarianDatabase:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def make_connection(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return self.connection


# ===================== MODEL ===================== #

class LibrarianModel:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor(dictionary=True)

    # ================= COMMON HELPERS ================= #

    def fetch_one(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def insert(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.lastrowid
        except IntegrityError:
            self.connection.rollback()
            raise

    # ================= AUTH ================= #

    def check_login_librarian(self, email):
        query = """
            SELECT *
            FROM users
            WHERE email = %s AND role = 'librarian' AND status = 'active'
            LIMIT 1
        """
        user = self.fetch_one(query, (email,))
        return user

    # ================= READ ================= #

    def read_categories(self):
        return self.fetch_all("SELECT * FROM categories")

    def read_books(self):
        return self.fetch_all("SELECT * FROM books")

    def read_editions(self):
        return self.fetch_all("SELECT * FROM editions")



    # ================= AUTHORS ================= #

    def get_author_id_by_name(self, name):
        query = "SELECT author_id FROM authors WHERE name = %s LIMIT 1"
        row = self.fetch_one(query, (name,))
        return row["author_id"] if row else None

    def insert_author(self, name):
        query = "INSERT INTO authors (name) VALUES (%s)"
        return self.insert(query, (name,))

    # ================= BOOKS ================= #
    def read_books_manage(self):
        query = """
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
                         LEFT JOIN editions e ON e.book_id = b.book_id
                         LEFT JOIN book_copies c ON c.edition_id = e.edition_id

                GROUP BY b.book_id
                ORDER BY b.created_at DESC \
                """
        return self.fetch_all(query)

    def book_exists(self, title, author_id, category_id):
        query = """
            SELECT book_id
            FROM books
            WHERE title = %s
              AND author_id = %s
              AND category_id = %s
            LIMIT 1
        """
        return self.fetch_one(query, (title, author_id, category_id))

    def insert_book(self, title, author_id, category_id, description):
        query = """
            INSERT INTO books (title, author_id, category_id, description)
            VALUES (%s, %s, %s, %s)
        """
        return self.insert(query, (title, author_id, category_id, description))

    # Update book data
    def update_book(self, book_id, title, author_id, category_id):
        query = """
                UPDATE books
                SET title=%s, \
                    author_id=%s, \
                    category_id=%s
                WHERE book_id = %s \
                """
        self.cursor.execute(query, (title, author_id, category_id, book_id))
        self.connection.commit()  # 🔴 THIS WAS MISSING
        return self.cursor.rowcount



    #================ Editions ====================#
    def insert_edition(self, book_id, edition_number, publisher, publication_year):
        query = """
            INSERT INTO editions (book_id, edition_number, publisher, publication_year)
            VALUES (%s, %s, %s, %s)
        """
        return self.insert(query, (book_id, edition_number, publisher, publication_year))

    def read_editions_manage(self):
        query = """
                SELECT e.edition_id, \
                       e.edition_number, \
                       e.publisher, \
                       e.publication_year, \
                       e.created_at, \

                       b.book_id, \
                       b.title          AS book_title, \

                       a.author_id, \
                       a.name           AS author_name, \

                       cgy.category_id, \
                       cgy.name         AS category_name, \

                       COUNT(c.copy_id) AS copies_count

                FROM editions e
                         JOIN books b
                              ON b.book_id = e.book_id
                         JOIN authors a
                              ON a.author_id = b.author_id
                         LEFT JOIN categories cgy
                                   ON cgy.category_id = b.category_id
                         LEFT JOIN book_copies c
                                   ON c.edition_id = e.edition_id

                GROUP BY e.edition_id
                ORDER BY e.created_at DESC \
                """
        return self.fetch_all(query)

    def edition_exists_update(self, edition_number, edition_id):
        query = """
                SELECT edition_id
                FROM editions
                WHERE edition_number = %s
                  AND edition_id != %s
                    LIMIT 1 \
                """
        self.cursor.execute(query, (edition_number, edition_id))
        return self.cursor.fetchone() is not None

    def update_edition(self, edition_id, edition_number, publisher, publication_year):
        query = """
        UPDATE editions
        SET edition_number = %s,
            publisher = %s,
            publication_year = %s
        WHERE edition_id = %s
    """
        self.cursor.execute(query, (
            edition_number,
            publisher if publisher else None,
            publication_year,
            edition_id
        ))
        self.connection.commit()
        return self.cursor.rowcount > 0

    #=============== copies ======================#
    def insert_copies(self, edition_id, count):
        query = "INSERT INTO book_copies (edition_id) VALUES (%s)"
        for _ in range(int(count)):
            self.insert(query, (edition_id,))

    def read_copies_manage(self):
        query = """
                SELECT c.copy_id, \
                       c.status, \
                       c.created_at, \

                       e.edition_id, \
                       e.edition_number, \
                       e.publisher, \
                       e.publication_year, \

                       b.book_id, \
                       b.title  AS book_title, \

                       a.name   AS author_name, \
                       cgy.name AS category_name

                FROM book_copies c
                         JOIN editions e ON e.edition_id = c.edition_id
                         JOIN books b ON b.book_id = e.book_id
                         JOIN authors a ON a.author_id = b.author_id
                         LEFT JOIN categories cgy ON cgy.category_id = b.category_id

                ORDER BY c.created_at DESC \
                """
        return self.fetch_all(query)

    def update_status(self, copy_id, status):
        query = """
                UPDATE book_copies
                SET status = %s
                WHERE copy_id = %s \
                """
        self.cursor.execute(query, (status, copy_id))
        self.connection.commit()
        return self.cursor.rowcount > 0

    def delete_copy(self, copy_id):
        try:
            query = "DELETE FROM book_copies WHERE copy_id = %s"
            self.cursor.execute(query, (copy_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print("Delete copy error:", e)
            return False

    #=========== requests ==========================#
    def get_requests_by_type(self, request_type):
            self.cursor.execute("""
                                SELECT r.request_id,
                                       r.member_id,
                                       r.edition_id,
                                       r.request_type,
                                       r.status,
                                       r.initiated_by,
                                       r.request_date,
                                       r.decision_date,
                                       r.librarian_id,
                                       r.note,
                                       u.name  AS member_name,
                                       b.title AS book_title,
                                       e.edition_number
                                FROM requests r
                                         JOIN users u ON r.member_id = u.user_id
                                         JOIN editions e ON r.edition_id = e.edition_id
                                         JOIN books b ON e.book_id = b.book_id
                                WHERE r.request_type = %s
                                ORDER BY r.request_date DESC
                                """, (request_type,))
            return self.cursor.fetchall()

    def update_request(self, request_id, member_id, edition_id):
            query = """
                    UPDATE requests
                    SET member_id=%s, \
                        edition_id=%s, \
                    WHERE request_id = %s \
                    """
            self.cursor.execute(query, (member_id, edition_id, request_id))
            self.connection.commit()
            return self.cursor.rowcount > 0

    def update_request_status(self, request_id, status):
        query = """
                UPDATE requests
                SET status = %s
                WHERE request_id = %s \
                """
        self.cursor.execute(query, (status, request_id))
        self.connection.commit()
        return self.cursor.rowcount > 0

    #============= ISSUES ==========================#
    def get_all_issues(self):
        try:
            self.cursor.execute("""
                                SELECT i.issue_id,
                                    i.issue_date,
                                       i.copy_id,
                                       i.member_id,
                                       i.due_date,
                                       i.return_date,
                                       e.edition_id,
                                       i.status,
                                       u.name  AS member_name,
                                       b.title AS book_title,
                                       e.edition_number
                                FROM issues i
                                         JOIN book_copies bc ON i.copy_id = bc.copy_id
                                         JOIN editions e ON bc.edition_id = e.edition_id
                                         JOIN books b ON e.book_id = b.book_id
                                         JOIN users u ON i.member_id = u.user_id
                                WHERE i.status = 'borrowed'
                                ORDER BY i.issue_date DESC
                                """)
            return self.cursor.fetchall()
        except Exception as e:
            print("Error in get_all_issues:", e)
            return []

    # Check for available copy
    def get_available_copy(self, edition_id):
            self.cursor.execute("""
                                SELECT copy_id
                                FROM book_copies
                                WHERE edition_id = %s
                                  AND status = 'available' LIMIT 1
                                """, (edition_id,))
            return self.cursor.fetchone()  # returns None if no copy available

    # Insert a new issue
    def create_issue(self, copy_id, member_id, due_date,librarian_id=2):
            self.cursor.execute("""
                                INSERT INTO issues (copy_id, member_id, issue_date, due_date, status,librarian_id)
                                VALUES (%s, %s, NOW(), %s, 'borrowed',%s)
                                """, (copy_id, member_id, due_date,librarian_id))
            self.cursor.execute("""
                                UPDATE book_copies
                                SET status='borrowed'
                                WHERE copy_id = %s
                                """, (copy_id,))
            self.connection.commit()

    # Insert a reserved request
    # def create_borrowed_request(self, member_id, edition_id):
    #     self.cursor.execute("""
    #                         INSERT INTO requests (member_id, edition_id, request_type, status, initiated_by,
    #                                               request_date)
    #                         VALUES (%s, %s, 'borrow', 'approved', 'librarian', NOW())
    #                         """, (member_id, edition_id))
    #
    #     # Get the last inserted ID
    #     request_id = self.cursor.lastrowid
    #
    #     self.connection.commit()
    #     return request_id

    # def create_reserved_request(self, member_id, edition_id):
    #         self.cursor.execute("""
    #                             INSERT INTO requests (member_id, edition_id, request_type, status, initiated_by,
    #                                                   request_date)
    #                             VALUES (%s, %s, 'borrow', 'reserved', 'librarian', NOW())
    #                             """, (member_id, edition_id))
    #         self.connection.commit()

    #================== helpers =====================#
    # Get category name by id
    def get_category_name(self, category_id):
        row = self.fetch_one("SELECT name FROM categories WHERE category_id=%s", (category_id,))
        return row["name"] if row else None

    # Check if another book exists for update (exclude current book_id)
    def book_exists_update(self, title, author_id, category_id, book_id):
            query = """
                    SELECT 1 \
                    FROM books
                    WHERE title = %s \
                      AND author_id = %s \
                      AND category_id = %s \
                      AND book_id != %s
                        LIMIT 1 \
                    """
            return bool(self.fetch_one(query, (title, author_id, category_id, book_id)))

    def edition_exists(self, book_id, edition_number):
        query = """
            SELECT edition_id
            FROM editions
            WHERE book_id = %s AND edition_number = %s
            LIMIT 1
        """
        return self.fetch_one(query, (book_id, edition_number))

    def get_members(self):
        self.cursor.execute("""
            SELECT * FROM users WHERE role='member'
        """)
        return self.cursor.fetchall()

    def get_books_with_editions(self):
        try:
            self.cursor.execute("""SELECT 
                                        b.book_id,
                                        b.title,
                                        e.edition_id,
                                        e.edition_number,
                                        COUNT(c.copy_id) AS total_copies
                                    FROM books b
                                    JOIN editions e ON e.book_id = b.book_id
                                    LEFT JOIN book_copies c ON c.edition_id = e.edition_id
                                    GROUP BY e.edition_id, b.book_id, b.title, e.edition_number
                                    ORDER BY b.title, e.edition_number;

                                """)
            rows = self.cursor.fetchall()  # rows are dicts if cursor was created with dictionary=True
            books_with_editions = []
            for row in rows:
                # use column names instead of indices
                book = {"book_id": row['book_id'], "title": row['title']}
                edition = {"edition_id": row['edition_id'], "edition_number": row['edition_number'],"total_copies": row['total_copies']}
                books_with_editions.append((book, edition))
            return books_with_editions
        except Exception as e:
            print("Error in get_books_with_editions:", e)
            return []

    def read_last_book(self, book_id):
        query = "SELECT title FROM books WHERE book_id = %s LIMIT 1"
        row = self.fetch_one(query, (book_id,))
        return row["title"] if row else None

    #check if the member al ready takes that copy
    def is_member_borrowed(self, copy_id, member_id):
            self.cursor.execute("""
                                SELECT member_id
                                FROM issues
                                WHERE member_id = %s AND copy_id = %s
                                  AND status = 'borrowed' LIMIT 1
                                """, (member_id,copy_id))
            return self.cursor.fetchone()  # returns None if no copy available

    def is_member_borrow_limit_reached(self, member_id):
        self.cursor.execute("""
                            SELECT COUNT(*) >= (SELECT CAST(policy_value AS UNSIGNED)
                                                FROM library_policies
                                                WHERE policy_key = 'allowed_borrowed'
                                       LIMIT 1 ) as is_reached
                            FROM issues
                            WHERE member_id = %s
                              AND status = 'borrowed'
                            """, (member_id,))

        result = self.cursor.fetchone()
        # Using .get() prevents a crash if the result is None
        return bool(result.get('is_reached')) if result else False


    def update_status_issue(self, issue_id, status):
        query = """
                UPDATE issues
                SET status = %s,
                    return_date = NOW()
                WHERE issue_id = %s \
                """
        self.cursor.execute(query, (status, issue_id))
        self.connection.commit()
        return self.cursor.rowcount > 0

    def get_issue(self, issue_id):
        """
        Fetch a single issue from the database, including its copy and edition details.
        Returns a dictionary if found, else None.
        """
        query = """
                SELECT i.issue_id, \
                       i.member_id, \
                       i.copy_id, \
                       i.request_id,
                       i.due_date,
                       e.edition_id \
                FROM issues i
                    JOIN book_copies c ON c.copy_id = i.copy_id
                    JOIN editions e ON e.edition_id = c.edition_id
                WHERE i.issue_id = %s LIMIT 1 \
                """
        self.cursor.execute(query, (issue_id,))
        row = self.cursor.fetchone()
        return row

    def update_issue(self, issue_id, member_id, due_date,copy_id):
        query = """
                UPDATE issues
                SET member_id=%s, \
                    copy_id=%s, \
                    due_date=%s
                WHERE issue_id = %s \
                """
        self.cursor.execute(query, (member_id, copy_id, due_date, issue_id))
        self.connection.commit()
        return self.cursor.rowcount > 0

    def update_payment_status(self, issue_id, payment_status):
        query = "UPDATE issues SET payment_status = %s WHERE issue_id = %s"
        self.cursor.execute(query, (payment_status, issue_id))
        self.connection.commit()
        return self.cursor.rowcount > 0

    # def is_reserved(self, request_id, member_id, edition_id):
    #     """
    #     Fetch a single issue from the database, including its copy and edition details.
    #     Returns a dictionary if found, else None.
    #     """
    #     query = """
    #             SELECT *
    #             FROM requests
    #             WHERE request_id = %s AND member_id = %s AND edition_id = %s AND status = 'reserved' \
    #             """
    #     self.cursor.execute(query, (request_id, member_id, edition_id))
    #     row = self.cursor.fetchone()
    #     return row
    #
    #     # ================= DASHBOARD FUNCTIONS ================= #

    def total_books(self):
        row = self.fetch_one("SELECT COUNT(*) AS total FROM books")
        return row['total'] if row else 0

    def total_copies(self):
        row = self.fetch_one("SELECT COUNT(*) AS total FROM book_copies")
        return row['total'] if row else 0

    def available_copies(self):
        row = self.fetch_one("""
                             SELECT COUNT(*) AS total
                             FROM book_copies
                             WHERE status = 'available'
                             """)
        return row['total'] if row else 0

    def issued_books(self):
        row = self.fetch_one("""
                             SELECT COUNT(*) AS total
                             FROM book_copies
                             WHERE status = 'borrowed'
                             """)
        return row['total'] if row else 0

    def overdue_books(self):
        row = self.fetch_one("""
                             SELECT COUNT(*) AS total
                             FROM issues
                             WHERE status = 'borrowed'
                               AND due_date < CURDATE()
                             """)
        return row['total'] if row else 0

    def reserved_requests(self):
        row = self.fetch_one("""
                             SELECT COUNT(*) AS total
                             FROM requests
                             WHERE request_type = 'reserve'
                               AND status = 'pending'
                             """)
        return row['total'] if row else 0

    def in_library_reading(self):
        row = self.fetch_one("""
                             SELECT COUNT(*) AS total
                             FROM book_copies
                             WHERE status = 'in_library'
                             """)
        return row['total'] if row else 0

    def total_members(self):
        row = self.fetch_one("""
                             SELECT COUNT(*) AS total
                             FROM users
                             WHERE role = 'member'
                             """)
        return row['total'] if row else 0

    # change librarian password
    def change_librarian_password(self, password, librarian_id):
            sql = """
                  UPDATE users
                  SET password = %s
                  WHERE user_id = %s; \
                  """
            try:
                self.cursor.execute(sql, (password, librarian_id))
                self.connection.commit()  # Commit the transaction
                print(f"success happen.")
                return True
            except Exception as e:
                print(f"Error: {e}")
                print(f'there is an error happen.')
                return False

    # change librarian details
    def update_librarian_details(self,librarian_data):
            print("in modal ",librarian_data)
            """
            Update librarian details in admin_login table
            """
            sql = """
                  UPDATE users \
                  SET name  = %s, \
                      email = %s
                  WHERE user_id = %s; \
                  """

            try:
                values = (
                    librarian_data.get('name'),
                    librarian_data.get('email'),  # address is optional
                    int(librarian_data.get('librarian_id'))
                )

                self.cursor.execute(sql, values)
                self.connection.commit()

                if self.cursor.rowcount == 0:
                    return False, 'No librarian found with that ID or no changes made'

                return True, 'User details updated successfully'

            except Exception as e:
                self.connection.rollback()
                print(f"Error updating librarian details: {str(e)}")

                # Handle duplicate email/phone errors
                if "Duplicate entry" in str(e) and "email" in str(e):
                    return False, 'Email is already in use by another user'
                if "Duplicate entry" in str(e) and "phone" in str(e):
                    return False, 'Phone number is already in use by another user'

                return False, f'Database error: {str(e)}'

# ===================== CONNECTION FACTORY ===================== #

librarian_db_configuration = DbConfiguration()


def check_librarian_model_connection():
    try:
        db = LibrarianDatabase(
            host=librarian_db_configuration.DB_HOSTNAME,
            port=3307,
            user=librarian_db_configuration.DB_USERNAME,
            password=librarian_db_configuration.DB_PASSWORD,
            database=librarian_db_configuration.DB_NAME
        )
        connection = db.make_connection()
        return True, LibrarianModel(connection)
    except Exception as e:
        print("Database connection failed:", e)
        return False, None
