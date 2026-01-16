from flask import Flask, session

app = Flask(__name__)

from app.admin import admin_model
from app.admin import admin_view

from app.librarian import librarian_view
from app.librarian import librarian_model

from app.member import member_view
from app.member import member_model

from app.public import public_view
from app.public import public_model

# set secret key
app.secret_key = '5280'