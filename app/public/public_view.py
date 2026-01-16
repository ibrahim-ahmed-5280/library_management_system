from app import app
from flask import render_template, request, make_response, jsonify, session, redirect, url_for

from app.librarian import librarian_model
from app.public.public_model import PublicModel, PublicDatabase, check_public_model_connection
from flask_bcrypt import Bcrypt, check_password_hash
import os
from werkzeug.utils import secure_filename


@app.route('/')
def index():
    connection_status ,publib_model = check_public_model_connection()
    if not connection_status:
        return render_template('public/index.html')

    stats = {
        "total_books": publib_model.total_books(),
        "total_copies": publib_model.total_copies(),
        "total_categories": publib_model.total_categories(),
        "total_members": publib_model.total_members()
    }
    return render_template('public/index.html',
                           stats_public = stats)