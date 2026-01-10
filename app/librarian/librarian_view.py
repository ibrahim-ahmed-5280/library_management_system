from app import app
from flask import render_template, request, make_response, jsonify, session, redirect, url_for
from app.librarian.librarian_model import LibrarianModel, LibrarianDatabase, check_librarian_model_connection
from flask_bcrypt import Bcrypt, check_password_hash
import os, re
from datetime import datetime, date
from datetime import datetime
from werkzeug.utils import secure_filename

# Helper function for session management
def get_session_data():
    """Retrieve session data."""
    return session.get('email')

#=====================================================#
#====== CONTEXT PROCESSOR TO GIVE DATA ALL PAGES =====#

@app.context_processor
def inject_librarian_data():
    """Automatically inject librarian data into all templates"""
    context = {
        'librarian': None
    }
    email = session.get('email')
    if email:
        connection_status, librarian_model = check_librarian_model_connection()
        if connection_status:
            try:
                librarian_data = librarian_model.check_login_librarian(email)
                if librarian_data:
                    print("Data get",librarian_data)
                    context.update({
                        'librarian': librarian_data
                    })
                    return context
            except Exception as e:
                app.logger.error(f"Error loading librarian data: {str(e)}")
    return context


#Librarian Login page
@app.route('/librarian/login_page')
def login_page_librarian():
    return render_template('admin/login_librarian.html')

#librarian dashboard page
@app.route('/librarian/dashboard_page')
def dashboard_page_librarian():
    email = get_session_data()
    if not email:
        return login_page_librarian()
    connect_status, librarian_model = check_librarian_model_connection()
    if not connect_status:
        return jsonify({"Database connection failed."})
    stats = {
        "total_books": librarian_model.total_books(),
        "total_copies": librarian_model.total_copies(),
        "available_copies": librarian_model.available_copies(),
        "issued_books": librarian_model.issued_books(),
        "overdue_books": librarian_model.overdue_books(),
        "reserved_requests": librarian_model.reserved_requests(),
        "in_library_reading": librarian_model.in_library_reading(),
        "total_members": librarian_model.total_members()
    }
    print("stats",stats)
    return render_template(
        'admin/dashboard.html',
        lib_stats=stats
    )

@app.route('/librarian/add_book_page')
def add_book_page():
    email = get_session_data()
    if not email:
        return login_page_librarian()
    connection_status,librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    categories = librarian_model.read_categories()
    if not categories:
        return render_template('admin/add_books.html',
                               categories={},
                               books = {},
                               editions = {})
    books = librarian_model.read_books()
    if not books:
        return render_template("admin/add_books.html",
                               categories=categories,
                               books={},
                               editions={})
    editions = librarian_model.read_editions()
    if not editions:
        return render_template("admin/add_books.html",
                               categories=categories,
                               books=books,
                               editions={})
    paired_data = list(zip(books, editions))
    return render_template('admin/add_books.html',
                           categories=categories,
                           books=books,
                           editions=editions,
                           books_with_editions=paired_data)

@app.route('/librarian/add_edition_page')
def add_edition_page():
    email = get_session_data()
    if not email:
        return login_page_librarian()
    connection_status,librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    books = librarian_model.read_books()
    if not books:
        return render_template("admin/add_editions.html",
                               books={},
                               editions={})
    return render_template('admin/add_editions.html',
                           books=books)

@app.route('/librarian/add_copy_page')
def add_copy_page():
    email = get_session_data()
    if not email:
        return login_page_librarian()
    connection_status,librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    books = librarian_model.read_books()
    if not books:
        return render_template("admin/add_book_copies.html",
                               books={},
                               editions={})
    editions = librarian_model.read_editions()
    if not editions:
        return render_template("admin/add_book_copies.html",
                               books=books,
                               editions={})
    return render_template('admin/add_book_copies.html',
                           books=books,
                           editions=editions)

@app.route('/librarian/manage_books')
def manage_books():
    email = get_session_data()
    if not email:
        return login_page_librarian()
    connection_status,librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    categories = librarian_model.read_categories()
    books_data = librarian_model.read_books_manage()
    if books_data:
        return render_template('/admin/manage_books.html',
                               books=books_data,
                               categories = categories)
    return render_template('/admin/manage_books.html')

@app.route('/librarian/manage_editions')
def manage_editions():
    email = get_session_data()
    if not email:
        return login_page_librarian()
    connection_status,librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    data_edition_table = librarian_model.read_editions_manage()
    if data_edition_table:
        return render_template('/admin/manage_editions.html',
                               editions =data_edition_table)
    return render_template('/admin/manage_editions.html')

@app.route('/librarian/manage_copies')
def manage_copies():
    email = get_session_data()
    if not email:
        return login_page_librarian()
    connection_status,librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    data_copies_table = librarian_model.read_copies_manage()
    print(data_copies_table)
    if data_copies_table:
        return render_template('/admin/manage_book_copies.html',
                               copies =data_copies_table)
    return render_template('/admin/manage_book_copies.html')
#=====================================================#
#============ CHECK FUNCTIONS ========================#


#============ CHECKING LOGIN =========================#
#======== LOGIN OPERATIONS ===========================#
@app.route('/librarian/login_librarian', methods=['POST'])
def login_librarian():
    data = request.get_json()

    print(f"The data recevied {data}")
    # Extract fields
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    # All validations passed
    connection_status, librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    result = librarian_model.check_login_librarian(email)
    if result:
        print(result)
        if check_password_hash(result.get('password'), password):
            print(result)
            session['librarian_id'] = result.get('user_id')
            session['email'] = result.get('email')
            session['password'] = result.get('password')
            return jsonify({
                "success": True,
                "message": "Librarian gets successfully."
            })
        else:
            return jsonify({
                "success": False,
                "error": "invalid_pass",
                "message": "Password is incorrect."
            })

    return jsonify({
        "success": False,
        "error": "invalid_email",
        "message": "Data not in the database."
    })


#=====================================================#
#============ SAVE DATA ==============================#
@app.route('/books/add', methods=['POST'])
def add_book():
    data = request.get_json()

    title = data.get('title', '').strip()
    author_name = data.get('author_name', '').strip()
    category_id = data.get('category_id')
    description = data.get('description', '').strip()

    # ---------------- VALIDATION ----------------

    if not title:
        return jsonify(success=False, error="title", message="Book title is required.")

    if len(title) < 3 or len(title) > 150:
        return jsonify(success=False, error="title", message="Book title must be 3–150 characters.")

    if not author_name:
        return jsonify(success=False, error="author", message="Author name is required.")

    if len(author_name) < 3 or len(author_name) > 100:
        return jsonify(success=False, error="author",
                       message="Author name must be 3–100 characters.")

    if not re.match(r'^[A-Za-z.\s]+$', author_name):
        return jsonify(success=False, error="author",
                       message="Author name can contain letters, spaces, and dots only.")

    if not category_id or not str(category_id).isdigit():
        return jsonify(success=False, error="category",
                       message="Valid category is required.")

    # ---------------- DB CONNECTION ----------------

    connection_status, book_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify(success=False, message="Database connection failed.")

    # ---------------- AUTHOR HANDLING ----------------
    # Avoid duplicate authors
    author_id = book_model.get_author_id_by_name(author_name)

    if not author_id:
        author_id = book_model.insert_author(author_name)
        print(f"Author {author_id} added.")

    # ---------------- BOOK DUPLICATE CHECK ----------------
    if book_model.book_exists(title, author_id, category_id):
        return jsonify(success=False,
                       message="This book already exists in the selected category.")

    # ---------------- INSERT BOOK ----------------
    book_id = book_model.insert_book(
        title=title,
        author_id=author_id,
        category_id=category_id,
        description=description
    )

    return jsonify({
        "success": True,
        "message": "Book added successfully.",
        "book_id": book_id,
        "title": title
    })

@app.route('/books/update', methods=['POST'])
def update_book():
    data = request.get_json()

    book_id = data.get('book_id')
    title = data.get('title', '').strip()
    author_name = data.get('author_name')
    category_id = data.get('category_id')

    print(f"Data received: {data}")
    # ---------------- VALIDATION ----------------
    if not book_id or not str(book_id).isdigit():
        return jsonify(success=False, message="Invalid book ID.")

    if not title:
        return jsonify(success=False, error="title", message="Book title is required.")

    if len(title) < 3 or len(title) > 150:
        return jsonify(success=False, error="title", message="Book title must be 3–150 characters.")

    if len(author_name) < 3 or len(author_name) > 100:
        return jsonify(success=False, error="author",
                       message="Author name must be 3–100 characters.")

    if not re.match(r'^[A-Za-z.\s]+$', author_name):
        return jsonify(success=False, error="author",
                       message="Author name can contain letters, spaces, and dots only.")

    if not category_id or not str(category_id).isdigit():
        return jsonify(success=False, error="category", message="Please select a valid category.")

    # ---------------- DB CONNECTION ----------------
    connection_status, book_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify(success=False, message="Database connection failed.")

    # ---------------- DUPLICATE CHECK ----------------
    # Avoid duplicate authors
    author_id = book_model.get_author_id_by_name(author_name)

    if not author_id:
        author_id = book_model.insert_author(author_name)
        print(f"Author {author_id} added.")

    # Check if another book with same title/author/category exists
    if book_model.book_exists_update(title, author_id, category_id, book_id):
        return jsonify(success=False,
                       message="Another book with the same title, author, and category already exists.")

    # ---------------- UPDATE BOOK ----------------
    updated = book_model.update_book(
        book_id=book_id,
        title=title,
        author_id=author_id,
        category_id=category_id
    )

    if not updated:
        return jsonify(success=False, message="You have not make any changes.")

    # Return updated names for JS table refresh
    author_name = data.get('author_name')
    category_name = book_model.get_category_name(category_id)

    print("Halkan la yimid")
    return jsonify({
        "success": True,
        "message": "Book updated successfully.",
        "book_id": book_id,
        "title": title,
        "author_name": author_name,
        "category_name": category_name
    })

@app.route('/editions/add', methods=['POST'])
def add_edition():
    data = request.get_json()

    book_id = str(data.get('book_id', '')).strip()
    edition_number = str(data.get('edition_number', '')).strip()
    publisher = str(data.get('publisher', '')).strip()
    publication_year = str(data.get('publication_year', '')).strip()

    # ---------------- VALIDATION ----------------

    if not book_id or not book_id.isdigit():
        return jsonify(
            success=False,
            error="book",
            message="Valid book is required."
        )

    if not edition_number:
        return jsonify(
            success=False,
            error="edition_number",
            message="Edition number is required."
        )

    if len(edition_number) < 2 or len(edition_number) > 30:
        return jsonify(
            success=False,
            error="edition_number",
            message="Edition number must be 2–30 characters."
        )

    if not re.match(r'^[A-Za-z0-9 .\-]+$', edition_number):
        return jsonify(
            success=False,
            error="edition_number",
            message="Edition number contains invalid characters."
        )

    if publisher:
        if len(publisher) < 2 or len(publisher) > 100:
            return jsonify(
                success=False,
                error="publisher",
                message="Publisher must be 2–100 characters."
            )

        if not re.match(r"^[A-Za-z0-9 .'\-&]+$", publisher):
            return jsonify(
                success=False,
                error="publisher",
                message="Publisher contains invalid characters."
            )

    if publication_year:
        try:
            year = int(publication_year)
            current_year = datetime.now().year
            if year < 1450 or year > current_year:
                return jsonify(
                    success=False,
                    error="publication_year",
                    message=f"Year must be between 1450 and {current_year}."
                )
        except ValueError:
            return jsonify(
                success=False,
                error="publication_year",
                message="Invalid publication year."
            )

    # ---------------- DB CONNECTION ----------------

    connection_status, librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify(
            success=False,
            message="Database connection failed."
        )

    # ---------------- DUPLICATE CHECK ----------------

    exists = librarian_model.edition_exists(book_id, edition_number)

    if exists:
        return jsonify(
            success=False,
            message="This edition already exists for the selected book."
        )

    # ---------------- INSERT EDITION ----------------

    edition_id = librarian_model.insert_edition(
        book_id=book_id,
        edition_number=edition_number,
        publisher=publisher or None,
        publication_year=publication_year or None
    )
    last_book = librarian_model.read_last_book(book_id)
    return jsonify({
        "success": True,
        "message": "Edition added successfully.",
        "edition_id": edition_id,
        "edition_number": edition_number,
        "title": last_book,
    })

@app.route('/editions/update', methods=['POST'])
def update_edition():
    data = request.get_json()

    edition_id = data.get('edition_id')
    edition_number = (data.get('edition_number') or '').strip()
    publisher = (data.get('publisher') or '').strip()
    publication_year = data.get('publication_year')

    # ---------------- VALIDATION ----------------
    if not edition_id or not str(edition_id).isdigit():
        return jsonify(success=False, message="Invalid edition ID.")

    # Edition Number
    if not edition_number:
        return jsonify(success=False, error="edition_number",
                       message="Edition number is required.")

    if len(edition_number) < 2 or len(edition_number) > 30:
        return jsonify(success=False, error="edition_number",
                       message="Edition number must be 2–30 characters.")

    if not re.match(r'^[A-Za-z0-9 .\-]+$', edition_number):
        return jsonify(success=False, error="edition_number",
                       message="Edition number contains invalid characters.")

    # Publisher (optional)
    if publisher:
        if len(publisher) < 2 or len(publisher) > 100:
            return jsonify(success=False, error="publisher",
                           message="Publisher must be 2–100 characters.")
        if not re.match(r"^[A-Za-z0-9 .'\-&]+$", publisher):
            return jsonify(success=False, error="publisher",
                           message="Publisher contains invalid characters.")

    # Publication Year (optional)
    if publication_year:
        try:
            publication_year = int(publication_year)
            current_year = datetime.now().year
            if publication_year < 1450 or publication_year > current_year:
                return jsonify(success=False, error="publication_year",
                               message=f"Year must be between 1450 and {current_year}.")
        except ValueError:
            return jsonify(success=False, error="publication_year",
                           message="Invalid publication year.")

    # ---------------- DB CONNECTION ----------------
    connection_status, edition_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify(success=False, message="Database connection failed.")

    # ---------------- DUPLICATE CHECK ----------------
    if edition_model.edition_exists_update(
        edition_number=edition_number,
        edition_id=edition_id
    ):
        return jsonify(success=False,
                       message="Another edition with the same number already exists.")

    # ---------------- UPDATE EDITION ----------------
    updated = edition_model.update_edition(
        edition_id=edition_id,
        edition_number=edition_number,
        publisher=publisher,
        publication_year=publication_year
    )

    if not updated:
        return jsonify(success=False,
                       message="There is no any change happen yet.")

    # ---------------- SUCCESS RESPONSE ----------------
    return jsonify(
        success=True,
        message="Edition updated successfully.",
        edition_id=edition_id,
        edition_number=edition_number,
        publisher=publisher,
        publication_year=publication_year
    )
@app.route('/book_copies/add', methods=['POST'])
def add_book_copies():
    data = request.get_json()
    print(f"Data Received: {data}")

    edition_id = str(data.get('edition_id', '')).strip()
    copies_count = str(data.get('copies_count', '')).strip()

    # ---------------- VALIDATION ----------------

    if not edition_id or not edition_id.isdigit():
        return jsonify(
            success=False,
            error="book",
            message="Valid edition is required."
        )
    print(copies_count, type(copies_count))
    if not copies_count or not str(copies_count).isdigit() or int(copies_count) < 1:
        return jsonify(
            success=False,
            error="copies_count",
            message="Copies count is required and must be a positive integer."
        )

    # ---------------- DB CONNECTION ----------------

    connection_status, librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify(
            success=False,
            message="Database connection failed."
        )

    # ---------------- DUPLICATE CHECK ----------------

    # ---------------- INSERT COPIES    ----------------

    edition_id = librarian_model.insert_copies(
        edition_id=edition_id,
        count=copies_count
    )

    return jsonify({
        "success": True,
        "message": "Copies added successfully.",
    })

@app.route('/copies/update-status', methods=['POST'])
def update_copy_status_route():
    data = request.get_json()
    copy_id = data.get('copy_id')
    status = (data.get('status') or '').strip().lower()

    # ---------------- VALIDATION ----------------
    allowed_statuses = ['available','lost','damaged','maintenance']

    if not copy_id or not str(copy_id).isdigit():
        return jsonify(success=False, message="Invalid copy ID.")

    if status not in allowed_statuses:
        return jsonify(success=False, error="status", message="Invalid status value.")

    # ---------------- DB CONNECTION ----------------
    connection_status, copy_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify(success=False, message="Database connection failed.")

    # ---------------- UPDATE STATUS ----------------
    updated = copy_model.update_status(copy_id=copy_id, status=status)
    if not updated:
        return jsonify(success=False, message="You don't make any change for the status.")

    # ---------------- SUCCESS RESPONSE ----------------
    return jsonify(success=True, message="Copy status updated successfully.", copy_id=copy_id, status=status)

@app.route('/copies/delete', methods=['POST'])
def delete_copy():
    data = request.get_json()
    copy_id = data.get('copy_id')

    if not copy_id or not str(copy_id).isdigit():
        return jsonify(success=False, message="Invalid copy ID.")

    # Connect to your database or model
    connection_status, copy_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify(success=False, message="Database connection failed.")

    # Check if copy exists and is available
    # copy_data = copy_model.get_copy_by_id(copy_id)
    # if not copy_data:
    #     return jsonify(success=False, message="Copy not found.")
    #
    # if copy_data['status'].lower() != 'available':
    #     return jsonify(success=False, message="Only available copies can be deleted.")

    # Perform deletion
    deleted = copy_model.delete_copy(copy_id)
    if deleted:
        return jsonify(success=True, message=f"Copy #{copy_id} deleted successfully.")
    else:
        return jsonify(success=False, message="Failed to delete copy.")


# ---------------- Get Requests by Type ----------------
def get_requests_by_type(request_type):
    connection_status, request_model = check_librarian_model_connection()
    if not connection_status:
        return []

    return request_model.get_requests_by_type(request_type)


@app.route('/requests/borrow')
def borrow_requests_page():
    email = get_session_data()
    if not email:
        return login_page_librarian()
    borrow_requests = get_requests_by_type('borrow')
    return render_template('admin/borrow_requests.html', requests=borrow_requests, request_type='borrow')

@app.route('/requests/return')
def return_requests_page():
    email = get_session_data()
    if not email:
        return login_page_librarian()
    return_requests = get_requests_by_type('return')
    return render_template('admin/return_requests.html', requests=return_requests, request_type='return')


@app.route('/issue_books')
def manage_issues():
    email = get_session_data()
    if not email:
        return login_page_librarian()
    connection_status, librarian_modal = check_librarian_model_connection()
    if not connection_status:
        return jsonify("Database connection failed")

    members = librarian_modal.get_members()
    books_with_editions = librarian_modal.get_books_with_editions()
    issues = librarian_modal.get_all_issues()
    print(f"The data gets {books_with_editions}")
    return render_template('admin/issue_management.html',
                           issues=issues,
                           members=members,
                           books_with_editions=books_with_editions)

# ------------------ Insert New Issue ------------------
@app.route('/issue_books/insert', methods=['POST'])
def insert_issue():
    data = request.get_json()
    print(f"Data received {data}")
    member_id = data.get('member_id')
    edition_id = data.get('edition_id')
    due_date_str = data.get('due_date')

    # Basic validation
    if not member_id or not edition_id or not due_date_str:
        return jsonify(
            success=False,
            message="All fields are required"
        ), 400

    # Date validation
    try:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(
            success=False,
            message="Invalid due date format"
        ), 400

    if due_date <= date.today():
        return jsonify(
            success=False,
            message="Due date must be greater than today"
        ), 400


    connection_status, librarian_modal = check_librarian_model_connection()
    if not connection_status:
        return jsonify("Database connection failed")

    # Check available copy
    copy = librarian_modal.get_available_copy(edition_id)

    if copy:
        if librarian_modal.is_member_borrowed(edition_id, member_id):
            return jsonify(success=False, message="Member borrowed already this book.")
        request_id = librarian_modal.create_borrowed_request(member_id, edition_id)
        librarian_modal.create_issue(copy['copy_id'], member_id, due_date,request_id)
        return jsonify({"success": True, "message": "Book issued successfully."})
        librarian_modal.update_status(copy['copy_id'], 'borrowed')
    else:
        librarian_modal.create_reserved_request(member_id, edition_id)
        return jsonify({"success": False, "message": "No available copy. Request reserved."})

@app.route('/issue_books/update', methods=['POST'])
def update_issue():
    data = request.get_json()
    print(f"Data received for update: {data}")

    issue_id = data.get('issue_id')
    member_id = data.get('member_id')
    edition_id = data.get('edition_id')
    due_date_str = data.get('due_date')

    # Basic validation
    if not issue_id or not member_id or not edition_id or not due_date_str:
        return jsonify(success=False, message="All fields are required"), 400

    # Date validation
    try:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(success=False, message="Invalid due date format"), 400

    if due_date <= date.today():
        return jsonify(success=False, message="Due date must be greater than today"), 400

    # Check DB connection
    connection_status, librarian_modal = check_librarian_model_connection()
    if not connection_status:
        return jsonify(success=False, message="Database connection failed"), 500

    # Get current issue details
    current_issue = librarian_modal.get_issue(issue_id)
    if not current_issue:
        return jsonify(success=False, message="Issue not found"), 404

    current_edition_id = current_issue['edition_id']
    current_copy_id = current_issue['copy_id']

    # If edition is changed
    if str(edition_id) != str(current_edition_id) and str(member_id) == str(current_issue['member_id']):
        # Check available copy for new edition
        copy = librarian_modal.get_available_copy(edition_id)

        if copy:
            if librarian_modal.is_member_borrowed(edition_id, member_id):
                return jsonify(success=False, message="The new Member borrowed already this book.")
            # Update issue with new copy and member
            librarian_modal.update_issue(issue_id, member_id, due_date, copy['copy_id'])
            # Update the request table if needed
            librarian_modal.update_request(current_issue.get('request_id'), member_id, edition_id)
            # Update old copy status to available
            librarian_modal.update_status(current_copy_id, 'available')
            # Update new copy status to borrowed
            librarian_modal.update_status(copy['copy_id'], 'borrowed')
            return jsonify(success=True, message="Issue updated with new edition successfully.")
        else:
            # No copy available: create reserved request
            librarian_modal.create_reserved_request(member_id, edition_id)
            librarian_modal.update_status_issue(issue_id, "returned")
            return jsonify(success=False, message="No available copy for the selected edition. Request reserved.")
    else:
        if librarian_modal.is_reserved(current_issue.get('request_id'),edition_id, member_id):
            return jsonify(success=False, message="Member borrowed already this book.")

        # Edition not changed, just update member and due date
        librarian_modal.update_issue(issue_id, member_id, edition_id, due_date, current_copy_id)
        return jsonify(success=True, message="Issue updated successfully.")




#Logout admin user
@app.route('/librarian/logout')
def logout_librarian():
    session.clear()
    return login_page_librarian()