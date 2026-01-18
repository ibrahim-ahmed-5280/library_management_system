from app import app
from flask import render_template, request, make_response, jsonify, session, redirect, url_for
from app.librarian.librarian_model import LibrarianModel, LibrarianDatabase, check_librarian_model_connection
from flask_bcrypt import Bcrypt, check_password_hash
import os, re
from datetime import datetime, date
from datetime import datetime
bcrypt = Bcrypt(app)
from werkzeug.utils import secure_filename

# Helper function for session management
def get_librarian_session():
    """Retrieve session data."""
    return session.get('librarian_email')

#=====================================================#
#====== CONTEXT PROCESSOR TO GIVE DATA ALL PAGES =====#

@app.context_processor
def inject_librarian_data():
    """Automatically inject librarian data into all templates"""
    context = {
        'librarian': None
    }
    email = session.get('librarian_email')
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

#=====================================================#
#=================== PAGES ===========================#

#Librarian Login page
@app.route('/librarian/login_page')
def login_page_librarian():
    return render_template('librarian/login_librarian.html')

#librarian dashboard page
@app.route('/librarian/dashboard_page')
def dashboard_page_librarian():
    email = get_librarian_session()
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
        'librarian/dashboard.html',
        lib_stats=stats
    )


# Profile admin page
@app.route('/librarian/profile_librarian')
def profile_librarian():
    email = get_librarian_session()
    if not email:
        return login_page_librarian()
    return render_template('librarian/profile_librarian.html')

@app.route('/librarian/add_book_page')
def add_book_page():
    email = get_librarian_session()
    if not email:
        return login_page_librarian()
    connection_status,librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    categories = librarian_model.read_categories()
    if not categories:
        return render_template('librarian/add_books.html',
                               categories={},
                               books = {},
                               editions = {})
    books = librarian_model.read_books()
    if not books:
        return render_template("librarian/add_books.html",
                               categories=categories,
                               books={},
                               editions={})
    editions = librarian_model.read_editions()
    if not editions:
        return render_template("librarian/add_books.html",
                               categories=categories,
                               books=books,
                               editions={})
    paired_data = list(zip(books, editions))
    return render_template('librarian/add_books.html',
                           categories=categories,
                           books=books,
                           editions=editions,
                           books_with_editions=paired_data)

@app.route('/librarian/add_edition_page')
def add_edition_page():
    email = get_librarian_session()
    if not email:
        return login_page_librarian()
    connection_status,librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    books = librarian_model.read_books()
    if not books:
        return render_template("librarian/add_editions.html",
                               books={})
    return render_template('librarian/add_editions.html',
                           books=books,
                           current_year=datetime.now().year)

@app.route('/librarian/add_copy_page')
def add_copy_page():
    email = get_librarian_session()
    if not email:
        return login_page_librarian()
    connection_status,librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    books = librarian_model.read_books()
    if not books:
        return render_template("librarian/add_book_copies.html",
                               books={},
                               editions={})
    editions = librarian_model.read_editions()
    if not editions:
        return render_template("librarian/add_book_copies.html",
                               books=books,
                               editions={})
    return render_template('librarian/add_book_copies.html',
                           books=books,
                           editions=editions)

@app.route('/librarian/manage_books')
def manage_books():
    email = get_librarian_session()
    if not email:
        return login_page_librarian()
    connection_status,librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    categories = librarian_model.read_categories()
    books_data = librarian_model.read_books_manage()
    if books_data:
        return render_template('/librarian/manage_books.html',
                               books=books_data,
                               categories = categories)
    return render_template('/librarian/manage_books.html')

@app.route('/librarian/manage_editions')
def manage_editions():
    email = get_librarian_session()
    if not email:
        return login_page_librarian()
    connection_status,librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    data_edition_table = librarian_model.read_editions_manage()
    if data_edition_table:
        return render_template('/librarian/manage_editions.html',
                               editions =data_edition_table)
    return render_template('/librarian/manage_editions.html')

@app.route('/librarian/manage_copies')
def manage_copies():
    email = get_librarian_session()
    if not email:
        return login_page_librarian()
    connection_status,librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    data_copies_table = librarian_model.read_copies_manage()
    print(data_copies_table)
    if data_copies_table:
        return render_template('/librarian/manage_book_copies.html',
                               copies =data_copies_table)
    return render_template('/librarian/manage_book_copies.html')

# ---------------- Get Requests by Type ----------------
def get_requests_by_type(request_type):
    connection_status, request_model = check_librarian_model_connection()
    if not connection_status:
        return []

    return request_model.get_requests_by_type(request_type)


@app.route('/requests/borrow')
def borrow_requests_page():
    email = get_librarian_session()
    if not email:
        return login_page_librarian()
    borrow_requests = get_requests_by_type('borrow')
    return render_template('librarian/borrow_requests.html', requests=borrow_requests, request_type='borrow')

@app.route('/requests/reserve')
def reverse_requests_page():
    email = get_librarian_session()
    if not email:
        return login_page_librarian()
    return_requests = get_requests_by_type('reserve')
    print(f"return_requests: {return_requests}")
    return render_template('librarian/reverse_requests.html',
                           requests=return_requests, request_type='reverse')

@app.route('/issue_books')
def manage_issues():
    email = get_librarian_session()
    if not email:
        return login_page_librarian()
    connection_status, librarian_modal = check_librarian_model_connection()
    if not connection_status:
        return jsonify("Database connection failed")

    members = librarian_modal.get_members()
    books_with_editions = librarian_modal.get_books_with_editions()
    issues = librarian_modal.get_all_issues()
    print(f"The data gets {books_with_editions}")
    return render_template('librarian/issue_management.html',
                           issues=issues,
                           members=members,
                           books_with_editions=books_with_editions)

@app.route('/return_issue_page')
def return_issue_page():
    email = get_librarian_session()
    if not email:
        return login_page_librarian()
    connection_status, librarian_modal = check_librarian_model_connection()
    if not connection_status:
        return jsonify(success=False, message="Database connection failed"), 500

    all_borrows = librarian_modal.get_all_issues()
    if all_borrows:
        return render_template('librarian/return_books.html',
                               issues=all_borrows,
                               today=date.today()
                               )
    return render_template('librarian/return_books.html',
                           issues=[])

@app.route('/librarian/fines_page')
def fines_overdue_page():
    email = get_librarian_session()
    if not email:
        return login_page_librarian()

    connection_status, librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify(success=False, message="Database connection failed"), 500

    fines = librarian_model.get_all_overdue_fines()

    return render_template(
        'librarian/fines_and_overdue.html',
        fines=fines,
        today=date.today()
    )

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
            session['librarian_email'] = result.get('email')
            session['librarian_password'] = result.get('password')
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


#=======================================================#
#============ INSERT DATA ==============================#
@app.route('/books/add', methods=['POST'])
def add_book():
    try:
        data = request.get_json()
        print(f"Data received {data}")

        title = data.get('title', '').strip()
        author_name = data.get('author_name', '').strip()
        category_id = data.get('category_id')
        description = data.get('description', '').strip()

        # Validation code ...

        connection_status, book_model = check_librarian_model_connection()
        if not connection_status:
            return jsonify(success=False, message="Database connection failed.")

        # Author handling and book insertion
        author_id = book_model.get_author_id_by_name(author_name)
        if not author_id:
            author_id = book_model.insert_author(author_name)

        if book_model.book_exists(title, author_id, category_id):
            return jsonify(success=False, message="This book already exists.")

        book_id = book_model.insert_book(title, author_id, category_id, description)

        return jsonify({
            "success": True,
            "message": "Book added successfully.",
        })

    except Exception as e:
        print("Error in add_book:", e)  # <-- Log the exact error
        return jsonify(success=False, message="Internal server error"), 500

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
    return jsonify({
        "success": True,
        "message": "Edition added successfully."
    })

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

@app.route('/issue_books/insert', methods=['POST'])
def insert_issue():
    data = request.get_json()
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

    # 1. Check if member is already holding/requesting this edition
    has_it, reason = librarian_modal.is_member_holding_edition(member_id, edition_id)

    if has_it:
        if reason == "borrowed":
            msg = "Member already has a copy of this book in their possession."
        elif reason == "reserved":
            msg = "Member already has an active (pending/approved) request for this book."
        else:
            msg = "Database error verifying member status."

        return jsonify(success=False, message=msg)

    # 2. Try to get an available copy
    copy = librarian_modal.get_available_copy(edition_id)

    if copy:
            # --- ISSUE LOGIC ---
            reached_borrow, msg = librarian_modal.has_reached_limits(member_id, 'borrow')
            if reached_borrow:
                return jsonify(success=False, message=msg)

            request_id = librarian_modal.create_borrowed_request(member_id, edition_id,session.get('librarian_id'))
            librarian_modal.create_issue(copy['copy_id'], member_id, due_date, request_id, session['librarian_id'])
            return jsonify(success=True, message="No reservation needed. Book issued immediately.")

    else:
            # --- RESERVE LOGIC (No copy available) ---
            reached_reserve, msg = librarian_modal.has_reached_limits(member_id, 'reserve')
            if reached_reserve:
                return jsonify(success=False, message="No copies available AND " + msg)

            success = librarian_modal.create_reservation(member_id, edition_id,session.get('librarian_id'))
            if success:
                return jsonify(success=True, message="No copies available. Book has been Reserved for the member.")
            else:
                return jsonify(success=False, message="Failed to create reservation.")

#========================================================#
#============== UPDATE DATA =============================#
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


    return jsonify({
        "success": True,
        "message": "Book updated successfully.",
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


@app.route('/issue_books/update', methods=['POST'])
def update_issue():
    data = request.get_json()
    issue_id = data.get('issue_id')
    member_id = data.get('member_id')
    edition_id = data.get('edition_id')
    due_date_str = data.get('due_date')

    # 1. Basic & Date Validation (Keep your existing code here)
    if not all([issue_id, member_id, edition_id, due_date_str]):
        return jsonify(success=False, message="All fields are required"), 400

    try:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        if due_date <= date.today():
            return jsonify(success=False, message="Due date must be greater than today"), 400
    except ValueError:
        return jsonify(success=False, message="Invalid date format"), 400

    connection_status, librarian_modal = check_librarian_model_connection()
    if not connection_status:
        return jsonify(success=False, message="Database connection failed"), 500

    # 2. Get Current Data
    current_issue = librarian_modal.get_issue(issue_id)
    if not current_issue:
        return jsonify(success=False, message="Issue record not found"), 404

    # 3. LOGIC: If Edition or Member has changed, perform possession check
    # We ignore the check if it's the SAME person and SAME book (just updating due date)
    if str(edition_id) != str(current_issue['edition_id']) or str(member_id) != str(current_issue['member_id']):
        has_it, reason = librarian_modal.is_member_holding_edition(member_id, edition_id)
        if has_it:
            return jsonify(success=False, message=f"Member cannot switch to this book: already {reason}.")

    # 4. HANDLE EDITION CHANGE
    if str(edition_id) != str(current_issue['edition_id']):
        # Check if new edition is available
        new_copy = librarian_modal.get_available_copy(edition_id)

        if new_copy:
            # Check borrow limits for the member (since it's essentially a new borrow)
            reached, msg = librarian_modal.has_reached_limits(member_id, 'borrow')
            # Important: subtract 1 from reached check because they are giving one back?
            # Or just proceed if it's a direct swap.

            # TRANSACTION: Swap the books
            # a) Set old copy to available
            librarian_modal.update_status(current_issue['copy_id'], 'available')
            # b) Set new copy to borrowed
            librarian_modal.update_status(new_copy['copy_id'], 'borrowed')
            # c) Update the issue record
            librarian_modal.update_issue(issue_id, member_id, due_date, new_copy['copy_id'])

            return jsonify(success=True, message="Book swapped and issue updated successfully.")

        else:
            # NO COPY AVAILABLE: Do you want to convert the current issue to a reservation?
            # Recommendation: Don't update the issue, tell the librarian to return the old one first.
            return jsonify(success=False, message="New edition not available. Cannot update.")

    else:
        # 5. SIMPLE UPDATE (Just Member or Due Date)
        librarian_modal.update_issue(issue_id, member_id, due_date, current_issue['copy_id'])
        return jsonify(success=True, message="Issue updated successfully.")

@app.route('/return_issue/update', methods=['POST'])
def update_return_issue():
    data = request.get_json()
    print(f"data: {data}")
    issue_id = data.get('issue_id')
    status = data.get('status')
    request_id = data.get('request_id')
    copy_id = data.get('copy_id')
    due_date_str = data.get('due_date')  # Format: 'YYYY-MM-DD'
    member_id = data.get('member_id')

    if status not in ['returned', 'borrowed']:
        return jsonify({"success": False, "message": "Invalid status"}), 400

    connection_status, librarian_modal = check_librarian_model_connection()
    if not connection_status:
        return jsonify(success=False, message="Database connection failed"), 500

    # 1. Update the issue status
    flag = librarian_modal.update_status_issue(issue_id, status)

    if flag:
        # 2. Handle Fine Calculation if returning a book
        if status == 'returned':
            today = datetime.now().date()
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

            if today > due_date:
                # Calculate days overdue
                overdue_days = (today - due_date).days

                # Get fine rate from policy
                fine_rate = float(librarian_modal.get_policy_value('fine_overdue'))
                total_fine = overdue_days * fine_rate

                # Insert fine into database
                if total_fine > 0:
                    librarian_modal.add_fine(issue_id, member_id, total_fine)

            # 3. Update Book and Request status
            librarian_modal.update_status_issue(issue_id, status)
            librarian_modal.update_status(copy_id, "available")
            librarian_modal.update_request_status(request_id, 'completed')

        return jsonify(success=True, message="Issue updated and processed successfully.")

    return jsonify({"success": False, "message": "Issue not updated successfully."})

@app.route('/librarian/approve_borrow_requests', methods=['POST'])
def approve_borrow_requests():
    email = get_librarian_session()
    if not email:
        return redirect(url_for('login')) # Use redirect for login too

    data = request.get_json()
    print(f"Data in request: {data}")
    request_id = int(data.get('request_id'))
    status = data.get('status')
    member_id = int(data.get('member_id'))
    due_date_str = data.get('due_date')
    edition_id = int(data.get('edition_id'))

    try:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        if due_date <= date.today():
            return jsonify(success=False, message="Due date must be greater than today"), 400
    except ValueError:
        return jsonify(success=False, message="Invalid date format"), 400

    connect_status, librarian_model = check_librarian_model_connection()
    if not connect_status:
        return jsonify(success=False, message="Database connection failed"), 500
    # reached_borrow, msg = librarian_model.has_reached_limits(member_id, 'borrow')
    # if reached_borrow:
    #     return jsonify(success=False, message="Reached limits"), 400
    flag = librarian_model.update_request_status(request_id, status)
    if flag:
        copy = librarian_model.get_available_copy(edition_id)
        librarian_model.create_issue(copy['copy_id'], member_id, due_date, request_id, session['librarian_id'])
        return jsonify(success=True, message="Issue updated with new status successfully.")
    else:
        return jsonify(success=False, message="Request status not updated."), 400


@app.route('/librarian/approve_reserve_requests', methods=['POST'])
def approve_reserve_requests():
    email = get_librarian_session()
    if not email:
        return redirect(url_for('login'))  # Use redirect for login too

    data = request.get_json()
    request_id = int(data.get('request_id'))
    status = data.get('status')
    due_date_str = data.get('due_date')
    member_id = int(data.get('member_id'))
    edition_id = int(data.get('edition_id'))

    try:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        if due_date <= date.today():
            return jsonify(success=False, message="Due date must be greater than today"), 400
    except ValueError:
        return jsonify(success=False, message="Invalid date format"), 400

    connect_status, librarian_model = check_librarian_model_connection()
    if not connect_status:
        return jsonify(success=False, message="Database connection failed"), 500
    reached_borrow, msg = librarian_model.has_reached_limits(member_id, 'borrow')
    if reached_borrow:
        return jsonify(success=False, message="Borrow limit reached successfully."), 400

    flag = librarian_model.update_request_status(request_id, status)
    if flag:
        copy = librarian_model.get_available_copy(edition_id)
        librarian_model.create_issue(copy['copy_id'], member_id, due_date, request_id, session['librarian_id'])
        return jsonify(success=True, message="Request approved successfully."), 200
    else:
        return jsonify(success=False, message="Request failed. Please try again."), 500

@app.route('/librarian/pay_fine', methods=['POST'])
def pay_fine():
    email = get_librarian_session()
    if not email:
        return jsonify(success=False, message="Unauthorized"), 401

    connection_status, librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify(success=False, message="Database connection failed"), 500

    data = request.get_json()
    issue_id = data.get('issue_id')

    success = librarian_model.update_payment_status(issue_id,'paid')

    if success:
        return jsonify(success=True)
    return jsonify(success=False, message="Payment update failed")

@app.route('/change_password_librarian', methods=['POST'])
def change_password_librarian():

    data = request.get_json()
    print(data)
    if not all(key in data for key in ['old_password', 'new_password', 'confirm_password']):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if len(data['new_password']) < 6 or len(data['new_password']) > 20:
        return jsonify({'success': False, 'message': 'Password must be at least 6 to 20 characters long'}), 400

    if data['new_password'] != data['confirm_password']:
        return jsonify({'success': False, 'message': 'New password and confirmation do not match'}), 400
    if not bcrypt.check_password_hash(session['librarian_password'], data['old_password']):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400

    connection_status, librarian_model = check_librarian_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed', 'field': 'general'}), 500

    hashed_password = bcrypt.generate_password_hash(data.get('new_password')).decode('utf-8')
    success = librarian_model.change_librarian_password(hashed_password, data.get('librarian_id'))
    if success:
        session['password'] = hashed_password
        return jsonify({'success': True, 'message': 'Password changed successfully'}), 200
    return jsonify({'success': False, 'message': 'Failed to change password', 'field': 'general'}), 400

#funtions use for validate
# function for validating full name
def validate_full_name(name):
    name = name.strip()
    if not all(word.isalpha() for word in name.split()):
        return False, 'Name must contain only alphabets (no numbers or special characters)'
    if len(name) < 9:
        return False, 'Name must be at least 9 characters long'
    if len(name) > 60:
        return False, 'Name cannot exceed 60 characters'
    words = name.split()
    word_count = len(words)
    if word_count < 3 or word_count > 4:
        return False, 'Name must contain 3 or 4 words separated by spaces'
    for word in words:
        if len(word) < 3 or len(word) > 15:
            return False, f'Each name must be between 3 and 15 characters: "{word}" is invalid'
    return True, None

# function for validating email
def validate_email(email):
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))


@app.route('/change_librarian_details', methods=['POST'])
def change_librarian_details():
    if not request.is_json:
        return jsonify({'status': False, 'message': 'Request must be JSON'}), 400

    try:
        data = request.get_json()
        print(data)
        errors = {}

        if not data.get('name'):
            errors['name'] = 'Name is required'
        else:
            is_valid_name, name_error = validate_full_name(data['name'])
            if not is_valid_name:
                errors['name'] = name_error

        if not data.get('email'):
            errors['email'] = 'Email is required'
        elif not validate_email(data['email']):
            errors['email'] = 'Invalid email format'

        if errors:
            return jsonify({'status': False, 'message': 'Validation failed', 'errors': errors}), 400

        connection_status, librarian_modal = check_librarian_model_connection()
        if connection_status:
            success = librarian_modal.update_librarian_details(data)
            if success:
                return jsonify({'status': True, 'message': 'librarian details updated successfully'})
            return jsonify({'status': False, 'message': 'Failed to update user details'})
        return jsonify({"Database connection problem."})
    except Exception as e:
        print(f'Error updating user details: {str(e)}')
        return jsonify({'status': False, 'message': 'Server error occurred while updating user details'}), 500
#===================================================#
#================ DELETE DATA ======================#
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


#===================================================#
#================= LOGOUT ==========================#
#Logout librarian user
# @app.route('/librarian/logout')
# def logout_librarian():
#     session.clear()
#     return login_page_librarian()