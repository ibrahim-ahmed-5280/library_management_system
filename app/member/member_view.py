from app import app
from flask import flash, render_template, request, make_response, jsonify, session, redirect, url_for
from app.member.member_model import MemberModel, MemberDatabase, check_member_model_connection
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
import os,re
from werkzeug.utils import secure_filename
from datetime import datetime, date
bcrypt = Bcrypt(app)
# ====================================================#
#================= SESSION STORAGE ===================#

# Helper function for session management
def get_member_session():
    """Retrieve session data."""
    return session.get('member_email')

#=====================================================#
#====== CONTEXT PROCESSOR TO GIVE DATA ALL PAGES =====#

@app.context_processor
def inject_member_data():
    """Automatically inject member data into all templates"""
    context = {
        'member': None
    }
    email = session.get('member_email')
    if email:
        connection_status, member_model = check_member_model_connection()
        if connection_status:
            try:
                _, admin_data = member_model.check_login_member(email)
                if admin_data:
                    context.update({
                        'member': admin_data[0]
                    })
                    return context
            except Exception as e:
                app.logger.error(f"Error loading admin data: {str(e)}")
    return context


#=====================================================#
#=============== PAGES ===============================#

#Login admin page
@app.route('/login')
def login():
    return render_template('member/login.html')

# Dashboard admin page
@app.route('/member/dashboard')
def dashboard_member():
    email = get_member_session()
    if not email:
        return login()

    connect_status, member_model = check_member_model_connection()
    if not connect_status:
        return jsonify({"error": "Database connection failed."})

    # 🔹 Read dashboard statistics


    return render_template(
        'member/dashboard.html',
        member_stats=[]
    )

# Profile admin page
@app.route('/member/profile_member')
def profile_member():
    email = get_member_session()
    if not email:
        return login()
    connect_status, member_model = check_member_model_connection()
    if not connect_status:
        return jsonify({"error": "Database connection failed."})
    return render_template('member/profile_member.html')


@app.route('/member/search_books')
def search_books():

    email = get_member_session()
    if not email:
        return login()

    connect_status, member_model = check_member_model_connection()
    if not connect_status:
        return jsonify({"error": "Database connection failed."})

    keyword = request.args.get('q')
    category_id = request.args.get('category')

    books_data = member_model.search_books(keyword, category_id)

    categories = member_model.view_categories()

    return render_template(
        'member/search_books.html',
        books=books_data,
        categories=categories,
        keyword=keyword,
        selected_category=int(category_id) if category_id else None
    )

@app.route('/member/view_books')
def view_books():
    email = get_member_session()
    if not email:
        return login()
    connect_status, member_model = check_member_model_connection()
    if not connect_status:
        return jsonify({"error": "Database connection failed."})

    books_data = member_model.view_books()
    print("Books data ",books_data)
    return render_template('member/view_books.html',
                           books = books_data)

@app.route('/member/member_requests')
def member_requests():
    email = get_member_session()
    if not email:
        return login()
    connect_status, member_model = check_member_model_connection()
    if not connect_status:
        return jsonify({"error": "Database connection failed."})

    #Read the data
    requests_data = member_model.view_member_requests(session.get("member_id"))
    print("Data gets requests ",requests_data)
    return render_template('member/view_requests.html',
                           member_requests = requests_data)

@app.route('/member/borrowed_books')
def borrowed_books():
    email = get_member_session()
    if not email:
        return login()
    connect_status, member_model = check_member_model_connection()
    if not connect_status:
        return jsonify({"error": "Database connection failed."})

    #Read the data
    borrowed_books_data = member_model.view_currently_borrowed_books(session.get("member_id"))
    return render_template('member/borrowed_books.html',
                           borrowed_books = borrowed_books_data)

@app.route('/member/borrowed_history')
def borrowed_history():
    email = get_member_session()
    if not email:
        return login()
    connect_status, member_model = check_member_model_connection()
    if not connect_status:
        return jsonify({"error": "Database connection failed."})

    #Read the data
    borrowed_history_data = member_model.view_member_borrowing_history(session.get('member_id'))
    return render_template('member/borrowed_history.html',
                           borrowed_history = borrowed_history_data)

@app.route('/member/in_library_reading')
def in_library_reading_view():
    email = get_member_session()
    if not email:
        return login()
    connect_status, member_model = check_member_model_connection()
    if not connect_status:
        return jsonify({"error": "Database connection failed."})

    #Read the data
    reading_sessions_data = member_model.view_member_reading_sessions(session.get("member_id"))
    return render_template('member/in_library_reading.html',
                           reading_sessions = reading_sessions_data)

@app.route('/member/fines')
def fines_or_payment():
    email = get_member_session()
    if not email:
        return login()
    connect_status, member_model = check_member_model_connection()
    if not connect_status:
        return jsonify({"error": "Database connection failed."})

    #Read the data
    fines_data = member_model.view_member_fines(session.get("member_id"))
    return render_template('member/view_fines.html',
                           fines = fines_data)


# ============THE LOGICS AND DATABASE INTERACTIONS ====================#
#=====================================================#
#======== LOGIN OPERATIONS ===========================#
@app.route('/login_member', methods=['POST'])
def login_member():
    data = request.get_json()

    print(f"The data recevied {data}")
    # Extract fields
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    # All validations passed
    connection_status, member_model = check_member_model_connection()
    if not connection_status:
        return jsonify({"success": False, "message": "Database connection failed."})
    flag, result = member_model.check_login_member(email)
    print(flag,result)
    if flag:
        if check_password_hash(result[0].get('password'), password):
            print(result)
            session['member_id'] = result[0].get('user_id')
            session['member_email'] = result[0].get('email')
            session['member_password'] = result[0].get('password')
            return jsonify({
                "success": True,
                "message": "Member gets successfully."
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

#================== INSERT OPERATIONS ===============#
@app.route('/member/request-borrow/<int:edition_id>', methods=['POST', 'GET'])
def member_request_borrow(edition_id):
    email = get_member_session()
    if not email:
        return redirect(url_for('login')) # Use redirect for login too

    connect_status, member_model = check_member_model_connection()
    if not connect_status:
        flash("Database connection failed.", "danger")
        return redirect(url_for('search_books')) # Replace with your search route name
    flag, data = member_model.is_member_request(session.get('member_id'), edition_id)
    if flag:
        flash("This book is already borrowed or requested.", "danger")
        return redirect(url_for('search_books'))

    result = member_model.create_borrow_request(session.get('member_id'), edition_id)

    if result is True:
        flash("Request submitted successfully!", "success")
        return redirect(url_for('member_requests'))
    else:
        flash("Request failed. Please try again.", "danger")
        return redirect(url_for('search_books'))

@app.route('/member/request-reserve/<int:edition_id>', methods=['POST', 'GET'])
def member_request_reserve(edition_id):
    email = get_member_session()
    if not email:
        return redirect(url_for('login'))

    connect_status, member_model = check_member_model_connection()
    if not connect_status:
        flash("Database connection failed.", "danger")
        return redirect(url_for('search_books'))

    # Check if the user already has a pending request for this edition
    flag, data = member_model.is_member_request(session.get('member_id'), edition_id)
    if flag:
        flash("You have already reserved this book.", "danger")
        return redirect(url_for('search_books'))

    result = member_model.create_reserve_request(session.get('member_id'), edition_id)

    if result is True:
        flash("Book reserved successfully!", "success")
        return redirect(url_for('member_requests'))
    else:
        flash("Reservation failed. Please try again.", "danger")
        return redirect(url_for('search_books'))

#=====================================================#
#======== UPDATE OPERATIONS ==========================#
@app.route('/member/cancel_request/<int:request_id>', methods=['POST'])
def cancel_request(request_id):
    email = get_member_session()
    if not email:
        return login()
    connect_status, member_model = check_member_model_connection()
    if not connect_status:
        return jsonify({"error": "Database connection failed."})
    try:
        # Perform the cancel
        if member_model.cancel_request(request_id):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False})
    except Exception as e:
        print(e)
        return jsonify({"success": False})

#========== UPDATE HELPERS ===========================#
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

#============== UPDATE ACTIONS ========================#
# change admin password
@app.route('/change_password_member', methods=['POST'])
def change_password_member():

    data = request.get_json()
    print(data)
    if not all(key in data for key in ['old_password', 'new_password', 'confirm_password']):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if len(data['new_password']) < 6 or len(data['new_password']) > 20:
        return jsonify({'success': False, 'message': 'Password must be at least 6 to 20 characters long'}), 400

    if data['new_password'] != data['confirm_password']:
        return jsonify({'success': False, 'message': 'New password and confirmation do not match'}), 400
    if not bcrypt.check_password_hash(session['member_password'], data['old_password']):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400

    connection_status, member_model = check_member_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed', 'field': 'general'}), 500

    hashed_password = bcrypt.generate_password_hash(data.get('new_password')).decode('utf-8')
    success = member_model.change_member_password(hashed_password, data.get('member_id'))
    if success:
        session['password'] = hashed_password
        return jsonify({'success': True, 'message': 'Password changed successfully'}), 200
    return jsonify({'success': False, 'message': 'Failed to change password', 'field': 'general'}), 400

# change admin details
@app.route('/change_member_details', methods=['POST'])
def change_member_details():
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

        connection_status, member_model = check_member_model_connection()
        if connection_status:
            success = member_model.update_member_details(data)
            if success:
                return jsonify({'status': True, 'message': 'admin details updated successfully'})
            return jsonify({'status': False, 'message': 'Failed to update user details'})
        return jsonify({"Database connection problem."})
    except Exception as e:
        print(f'Error updating user details: {str(e)}')
        return jsonify({'status': False, 'message': 'Server error occurred while updating user details'}), 500

#=======================================================#
#======== LOGOUT OPERATION =============================#
#Logout member user
@app.route('/logout')
def logout():
    session.clear()
    return login()