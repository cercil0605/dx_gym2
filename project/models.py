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

# create student table
class StudentInfo(db.Model):
    student_id = db.Column(db.String(8), primary_key=True)
    hashed_id = db.Column(db.String(32),nullable=False)

# create request table
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reserved_date = db.Column(db.String, nullable=False)
    reserved_time = db.Column(db.String, nullable=False)
    student_id = db.Column(db.String(8), primary_key=True)



