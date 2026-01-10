from app import app
from flask import render_template, request, make_response, jsonify, session, redirect, url_for
from app.user.user_model import UserModel, UserDatabase, check_user_model_connection
from flask_bcrypt import Bcrypt, check_password_hash
import os
from werkzeug.utils import secure_filename

#Login user page
@app.route('/user/login_page')
def login_page_user():
    return render_template('user/login.html')