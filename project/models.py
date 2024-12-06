from flask_login import UserMixin
from . import db

# create user table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

# create reservation table
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reserved_date = db.Column(db.String, nullable=False)
    reserved_time = db.Column(db.String, nullable=False)


