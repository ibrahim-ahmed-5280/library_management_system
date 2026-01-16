from app import app
from flask import render_template, request, make_response, jsonify, session, redirect, url_for
from app.admin.admin_model import AdminModel, AdminDatabase, check_admin_model_connection
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
import os,re
from werkzeug.utils import secure_filename
from datetime import datetime, date
bcrypt = Bcrypt(app)
# ====================================================#
#================= SESSION STORAGE ===================#

# Helper function for session management
def get_admin_session():
    """Retrieve session data."""
    return session.get('admin_email')

#=====================================================#
#====== CONTEXT PROCESSOR TO GIVE DATA ALL PAGES =====#

@app.context_processor
def inject_admin_data():
    """Automatically inject admin data into all templates"""
    context = {
        'admin': None
    }
    email = session.get('admin_email')
    if email:
        connection_status, admin_model = check_admin_model_connection()
        if connection_status:
            try:
                _, admin_data = admin_model.check_login_admin(email)
                if admin_data:
                    context.update({
                        'admin': admin_data[0]
                    })
                    return context
            except Exception as e:
                app.logger.error(f"Error loading admin data: {str(e)}")
    return context


#=====================================================#
#=============== PAGES ===============================#

#Login admin page
@app.route('/admin/login_page')
def login_page():
    return render_template('admin/login.html')

# Dashboard admin page
@app.route('/admin/dashboard_page')
def dashboard_page_admin():
    email = get_admin_session()
    if not email:
        return login_page()

    connect_status, admin_model = check_admin_model_connection()
    if not connect_status:
        return jsonify({"error": "Database connection failed."})

    # 🔹 Read dashboard statistics
    stats = {
        "total_books": admin_model.total_books(),
        "total_members": admin_model.total_members(),
        "borrowed_books": admin_model.borrowed_books(),
        "overdue_books": admin_model.overdue_books(),
        "total_staff": admin_model.total_staff(),
        "categories": admin_model.total_categories(),
        "reservations": admin_model.total_reservations(),
        "new_books": admin_model.new_books_this_month()
    }

    return render_template(
        'admin/dashboard.html',
        admin_stats=stats
    )

# Profile admin page
@app.route('/admin/profile_admin')
def profile_admin():
    email = get_admin_session()
    if not email:
        return login_page()
    return render_template('admin/admin_profile.html')


# Admin reports page
@app.route("/admin/reports")
def admin_reports():
    email = get_admin_session()
    if not email:
        return login_page()

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})

    reports = admin_model.get_system_reports()

    return render_template(
        "admin/admin_reports.html",
        reports=reports
    )

# Helper for report page
@app.route("/admin/reports/export/<format>")
def export_report(format):
    return f"Exporting {format}"

#Add admins page
@app.route('/admin/add_admin_page')
def add_admin_page():
    email = get_admin_session()
    print(email)
    if not email:
        return login_page()
    return render_template('admin/add_admin.html')

#Add librarians page
@app.route('/admin/add_librarian_page')
def add_librarian_page():
    email = get_admin_session()
    if not email:
        return login_page()
    return render_template('admin/add_librarian.html')

#Add members page
@app.route('/admin/add_member_page')
def add_member_page():
    email = get_admin_session()
    if not email:
        return login_page()
    return render_template('admin/add_member.html')

#Manage Admins page
@app.route('/admin/manage_admins')
def manage_admins_page():
    email = get_admin_session()
    if not email:
        return login_page()
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    flag, admin_data = admin_model.get_all_admins()
    if flag:
        return render_template('admin/manage_admins.html',
                               admin_data=admin_data)
    return render_template('admin/manage_admins.html',
                           admin_data = [])

#Manage librarians page
@app.route('/admin/manage_librarians')
def manage_librarians_page():
    email = get_admin_session()
    if not email:
        return login_page()
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    flag, librarian_data = admin_model.get_all_librarians()
    if flag:
        return render_template('admin/manage_librarians.html',
                               librarian_data=librarian_data)
    return render_template('admin/manage_librarians.html',
                           librarian_data = [])

#Manage members page
@app.route('/admin/manage_members')
def manage_members_page():
    email = get_admin_session()
    if not email:
        return login_page()
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    flag , member_data = admin_model.get_all_members()
    if flag:
        return render_template('admin/manage_members.html',
                               member_data=member_data)
    return render_template('admin/manage_members.html',
                           member_data=[])

#manage settings or policies of the library
@app.route('/admin/add_policy_page')
def add_policy_page():
    email = get_admin_session()
    if not email:
        return login_page()
    return render_template('admin/add_policy.html',
                           policy_data=[])


#manage settings or policies of the library
@app.route('/admin/manage_policy_page')
def manage_policy_page():
    email = get_admin_session()
    if not email:
        return login_page()

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    flag, policy_data = admin_model.get_all_policies()
    if flag:
        return render_template('admin/manage_policy.html',
                               policy_data=policy_data)
    return render_template('admin/manage_policy.html',
                           policy_data=[])

# ============THE LOGICS AND DATABASE INTERACTIONS ====================#
#=====================================================#
#======== LOGIN OPERATIONS ===========================#
@app.route('/admin/login_admin', methods=['POST'])
def login_admin():
    data = request.get_json()

    print(f"The data recevied {data}")
    # Extract fields
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    # All validations passed
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    flag, result = admin_model.check_login_admin(email)
    if flag:
        if check_password_hash(result[0].get('password'), password):
            print(result)
            session['user_id'] = result[0].get('user_id')
            session['admin_email'] = result[0].get('email')
            session['admin_password'] = result[0].get('password')
            return jsonify({
                "success": True,
                "message": "Admin added successfully."
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
#======== INSERT OPERATIONS ===========================#

#Add admin user
@app.route("/admin/add_admin", methods=["POST"])
def add_admin():
    data = request.get_json()

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    confirm = data.get("confirm","").strip()
    # ---- VALIDATION ----
    name_parts = name.split()
    if len(name_parts) < 3 or len(name_parts) > 4:
        return jsonify(success=False, message="Admin name must have 3–4 parts.")

    if not re.match(r"^[A-Za-z ]{5,60}$", name):
        return jsonify(success=False, message="Invalid name format.")

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify(success=False, message="Invalid email address.")

    if len(password) < 6:
        return jsonify(success=False, message="Password too short.")
    if confirm != password:
        return jsonify(success = False, message = "Confirm password must be same as password")
    hashed_password = generate_password_hash(password)

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify(success = False,message="Database connection failed.")

    #check if the email already used
    success,data = admin_model.check_email_exist(email)
    if success:
        return jsonify(success=False, message="Email already exists.")

    #insert the new admin
    flag,message_get = admin_model.add_admin(name,email,hashed_password)
    print(message_get)
    if flag:
        return jsonify(success=True, message= message_get)

    return jsonify(success=False, message="Admin not registered.")

#Add librarian user
@app.route("/admin/add_librarian", methods=["POST"])
def add_librarian():
    data = request.get_json()

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    confirm = data.get("confirm","").strip()
    # ---- VALIDATION ----
    name_parts = name.split()
    if len(name_parts) < 3 or len(name_parts) > 4:
        return jsonify(success=False, message="Admin name must have 3–4 parts.")

    if not re.match(r"^[A-Za-z ]{5,60}$", name):
        return jsonify(success=False, message="Invalid name format.")

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify(success=False, message="Invalid email address.")

    if len(password) < 6:
        return jsonify(success=False, message="Password too short.")
    if confirm != password:
        return jsonify(success = False, message = "Confirm password must be same as password")
    hashed_password = generate_password_hash(password)

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify(success = False,message="Database connection failed.")

    #check if the email already used
    success,data = admin_model.check_email_exist(email)
    if success:
        return jsonify(success=False, message="Email already exists.")

    #insert the new admin
    flag,message_get = admin_model.add_librarian(name,email,hashed_password)
    print(message_get)
    if flag:
        return jsonify(success=True, message= message_get)

    return jsonify(success=False, message="Librarian not registered.")

#Add member user
@app.route("/admin/add_member", methods=["POST"])
def add_member():
    data = request.get_json()

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    confirm = data.get("confirm","").strip()
    membership_type = data.get("membership_type", "").strip()
    membership_start = data.get("membership_start", "").strip()
    membership_end = data.get("membership_end", "").strip()

    # ---- VALIDATION ----
    name_parts = name.split()
    if len(name_parts) < 3 or len(name_parts) > 4:
        return jsonify(success=False, message="Admin name must have 3–4 parts.")

    if not re.match(r"^[A-Za-z ]{5,60}$", name):
        return jsonify(success=False, message="Invalid name format.")

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify(success=False, message="Invalid email address.")

    if len(password) < 6:
        return jsonify(success=False, message="Password too short.")
    if confirm != password:
        return jsonify(success = False, message = "Confirm password must be same as password")

    # ---------------- MEMBERSHIP TYPE ----------------
    if membership_type not in ("student", "external"):
        return jsonify(
            success=False,
            message="Invalid membership type."
        )

    # ---------------- START DATE ----------------
    try:
        start_date = datetime.strptime(membership_start, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return jsonify(
            success=False,
            message="Invalid membership start date."
        )

    # ---------------- END DATE ----------------
    try:
        end_date = datetime.strptime(membership_end, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return jsonify(
            success=False,
            message="Invalid membership end date."
        )

    # ---------------- DATE ORDER ----------------
    if end_date <= start_date:
        return jsonify(
            success=False,
            message="Membership end date must be after start date."
        )

    # ---------------- START DATE NOT IN PAST ----------------
    if start_date < date.today():
        return jsonify(
            success=False,
            message="Membership start date cannot be in the past."
        )

    # ---------------- MINIMUM 1 YEAR DURATION ----------------
    MIN_DAYS = 365
    if (end_date - start_date).days < MIN_DAYS:
        return jsonify(
            success=False,
            message="Membership must be at least 1 year."
        )
    hashed_password = generate_password_hash(password)

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify(success = False,message="Database connection failed.")

    #check if the email already used
    success,data = admin_model.check_email_exist(email)
    if success:
        return jsonify(success=False, message="Email already exists.")

    #insert the new admin
    flag,message_get = admin_model.add_member(name,email,hashed_password,membership_type,start_date,end_date)
    if flag:
        print(message_get)
        return jsonify(success=True, message= message_get)

    return jsonify(success=False, message="Member not registered.")

#Add policy
@app.route("/admin/add_policy", methods=["POST"])
def add_policy():
    data = request.get_json()

    policy_name  = data.get("policy_name", "").strip()
    policy_key   = data.get("policy_key", "").strip()
    policy_value = data.get("policy_value", "").strip()
    description  = data.get("description", "").strip()

    # ---------- VALIDATION ----------

    # Policy name
    if len(policy_name) < 3 or len(policy_name) > 100:
        return jsonify(
            success=False,
            message="Policy name must be between 3 and 100 characters."
        )

    # Policy key (snake_case)
    if not re.match(r"^[a-z_]{3,50}$", policy_key):
        return jsonify(
            success=False,
            message="Policy key must contain only lowercase letters and underscores."
        )

    # Policy value
    if not policy_value:
        return jsonify(
            success=False,
            message="Policy value is required."
        )

    # Description
    if len(description) < 5:
        return jsonify(
            success=False,
            message="Description must be at least 5 characters."
        )

    # ---------- DB CONNECTION ----------
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify(
            success=False,
            message="Database connection failed."
        )

    # ---------- CHECK UNIQUE POLICY KEY ----------
    exists, _ = admin_model.check_policy_key_exist(policy_key)
    if exists:
        return jsonify(
            success=False,
            message="Policy key already exists."
        )

    # ---------- INSERT POLICY ----------
    flag, msg = admin_model.add_policy(
        policy_name,
        policy_key,
        policy_value,
        description,
        session.get('user_id')
    )

    if flag:
        return jsonify(success=True, message=msg)

    return jsonify(
        success=False,
        message="Policy not registered."
    )


#=====================================================#
#======== UPDATE OPERATIONS ===========================#


#Update admin and librarian user
@app.route("/admin/update_user", methods=["POST"])
def update_user():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    status = data.get("status","").strip()
    user_id = int(data.get("user_id","").strip())
    # ---- VALIDATION ----
    name_parts = name.split()
    if len(name_parts) < 3 or len(name_parts) > 4:
        return jsonify(success=False, message="Admin or librarian name must have 3–4 parts.")

    if not re.match(r"^[A-Za-z ]{5,60}$", name):
        return jsonify(success=False, message="Invalid name format.")

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify(success=False, message="Invalid email address.")

    if status not in ['active', 'inactive']:
        return jsonify(sucess=False,message ="Status must be active or inactive")

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify(success = False,message="Database connection failed.")

    #check if the email already used
    success,data = admin_model.check_email_exist(email,data.get('user_id'))
    if success:
        return jsonify(success=False, message="Email already exists.")
    #update the librarian details
    flag,message_get = admin_model.update_user(name,email,status,user_id)
    print(message_get)
    if flag:
        return jsonify(success=True, message= message_get)

    return jsonify(success=False, message="User not updated.")

#Update member user
@app.route("/admin/update_member", methods=["POST"])
def update_member():
    data = request.get_json()

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    membership_type = data.get("membership_type", "").strip()
    membership_start = data.get("membership_start", "").strip()
    membership_end = data.get("membership_end", "").strip()
    status = data.get("status","").strip()
    user_id = int(data.get('user_id',"").strip())
    # ---- VALIDATION ----
    name_parts = name.split()
    if len(name_parts) < 3 or len(name_parts) > 4:
        return jsonify(success=False, message="Admin name must have 3–4 parts.")

    if not re.match(r"^[A-Za-z ]{5,60}$", name):
        return jsonify(success=False, message="Invalid name format.")

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify(success=False, message="Invalid email address.")

    if status not in ['active', 'inactive']:
        return jsonify(success=False,message ="Status must be active or inactive")

    # ---------------- MEMBERSHIP TYPE ----------------
    if membership_type not in ["student", "external"]:
        return jsonify(
            success=False,
            message="Invalid membership type."
        )

    # ---------------- START DATE ----------------
    try:
        start_date = datetime.strptime(membership_start, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return jsonify(
            success=False,
            message="Invalid membership start date."
        )

    # ---------------- END DATE ----------------
    try:
        end_date = datetime.strptime(membership_end, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return jsonify(
            success=False,
            message="Invalid membership end date."
        )

    # ---------------- DATE ORDER ----------------
    if end_date <= start_date:
        return jsonify(
            success=False,
            message="Membership end date must be after start date."
        )

    # ---------------- START DATE NOT IN PAST ----------------
    if start_date < date.today():
        return jsonify(
            success=False,
            message="Membership start date cannot be in the past."
        )

    # ---------------- MINIMUM 1 YEAR DURATION ----------------
    MIN_DAYS = 365
    if (end_date - start_date).days < MIN_DAYS:
        return jsonify(
            success=False,
            message="Membership must be at least 1 year."
        )

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify(success = False,message="Database connection failed.")

    #check if the email already used
    success,data = admin_model.check_email_exist(email,user_id)
    if success:
        return jsonify(success=False, message="Email already exists.")

    #insert the new admin
    flag,message_get = admin_model.update_member(name,email,membership_type,start_date,end_date,status,user_id)
    if flag:
        print(message_get)
        return jsonify(success=True, message= message_get)

    return jsonify(success=False, message="Member not updated.")

#Update password admin and librarian user
@app.route("/admin/update_user_password", methods=["POST"])
def update_user_password():
    data = request.get_json()
    password = data.get("password", "").strip()
    confirm = data.get("confirm", "").strip()
    user_id = int(data.get("user_id","").strip())

    if len(password) <6:
        return jsonify(sucess=False,message ="Password must be 6 chars or above")
    if confirm != password:
        return jsonify(success=False,message ="Confirm password must match password")

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify(success = False,message="Database connection failed.")

    hashed_password = generate_password_hash(password)
    #update the librarian details
    flag,message_get = admin_model.update_user_password(hashed_password,user_id)
    print(message_get)
    if flag:
        return jsonify(success=True, message= message_get)

    return jsonify(success=False, message="User password not updated.")

#Add policy
@app.route("/admin/update_policy", methods=["POST"])
def update_policy():
    data = request.get_json()

    policy_name  = data.get("policy_name", "").strip()
    policy_key   = data.get("policy_key", "").strip()
    policy_value = data.get("policy_value", "").strip()
    description  = data.get("description", "").strip()
    policy_id = int(data.get('policy_id',"").strip())
    # ---------- VALIDATION ----------

    # Policy name
    if len(policy_name) < 3 or len(policy_name) > 100:
        return jsonify(
            success=False,
            message="Policy name must be between 3 and 100 characters."
        )

    # Policy key (snake_case)
    if not re.match(r"^[a-z_]{3,50}$", policy_key):
        return jsonify(
            success=False,
            message="Policy key must contain only lowercase letters and underscores."
        )

    # Policy value
    if not policy_value:
        return jsonify(
            success=False,
            message="Policy value is required."
        )

    # Description
    if len(description) < 5:
        return jsonify(
            success=False,
            message="Description must be at least 5 characters."
        )

    # ---------- DB CONNECTION ----------
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify(
            success=False,
            message="Database connection failed."
        )

    # ---------- CHECK UNIQUE POLICY KEY ----------
    exists, _ = admin_model.check_policy_key_exist(policy_key,policy_id)
    if exists:
        return jsonify(
            success=False,
            message="Policy key already exists."
        )

    # ---------- INSERT POLICY ----------
    flag, msg = admin_model.update_policy(
        policy_id,
        policy_name,
        policy_key,
        policy_value,
        description,
        session.get('user_id')
    )

    if flag:
        return jsonify(success=True, message=msg)

    return jsonify(
        success=False,
        message="Policy not registered."
    )


# change admin password
@app.route('/change_password_admin', methods=['POST'])
def change_password_admin():

    data = request.get_json()
    print(data)
    if not all(key in data for key in ['old_password', 'new_password', 'confirm_password']):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if len(data['new_password']) < 6 or len(data['new_password']) > 20:
        return jsonify({'success': False, 'message': 'Password must be at least 6 to 20 characters long'}), 400

    if data['new_password'] != data['confirm_password']:
        return jsonify({'success': False, 'message': 'New password and confirmation do not match'}), 400
    if not bcrypt.check_password_hash(session['admin_password'], data['old_password']):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed', 'field': 'general'}), 500

    hashed_password = bcrypt.generate_password_hash(data.get('new_password')).decode('utf-8')
    success = admin_model.change_admin_password(hashed_password, data.get('admin_id'))
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



# change admin details
@app.route('/change_admin_details', methods=['POST'])
def change_admin_details():
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

        connection_status, admin_model = check_admin_model_connection()
        if connection_status:
            success = admin_model.update_admin_details(data)
            if success:
                return jsonify({'status': True, 'message': 'admin details updated successfully'})
            return jsonify({'status': False, 'message': 'Failed to update user details'})
        return jsonify({"Database connection problem."})
    except Exception as e:
        print(f'Error updating user details: {str(e)}')
        return jsonify({'status': False, 'message': 'Server error occurred while updating user details'}), 500

#=====================================================#
#======== LOGOUT OPERATION ===========================#

#Logout admin user
@app.route('/admin/logout')
def logout_admin():
    session.clear()
    return login_page()