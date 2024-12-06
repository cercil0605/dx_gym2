from . import db

# create reservation table
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reserved_date = db.Column(db.String, nullable=False)
    reserved_time = db.Column(db.String, nullable=False)

