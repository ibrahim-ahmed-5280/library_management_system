from app import app
from flask import render_template, request, make_response, jsonify, session, redirect, url_for
from app.public.public_model import PublicModel, PublicDatabase, check_public_model_connection
from flask_bcrypt import Bcrypt, check_password_hash
import os
from werkzeug.utils import secure_filename

@app.route('/')
def index():
    return render_template('public/index.html')