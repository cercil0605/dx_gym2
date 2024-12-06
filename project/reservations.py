from flask import Blueprint
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

from . import db
from .models import Reservation

reservations = Blueprint('reservations', __name__)

# get reserved_time
def get_booked_times(reserved_date):
    # find reserved data
    reserve = Reservation.query.filter_by(reserved_date=reserved_date).all()
    # push booked time data in reserved_date to booked_times
    booked_times = []
    for r in reserve:
        booked_times.append(r.reserved_time)

    return booked_times

# add reservation to db
def add_booking(reserved_date, reserved_time):
    # prepare reservation data
    new_reservation = Reservation(
        reserved_date=reserved_date,
        reserved_time=reserved_time)

    try:
        # insert reservation
        db.session.add(new_reservation)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        # failed
        db.session.rollback()
        # error message
        print(f"Error: {e}")
        return False

# get available reservation day(start~end)
def get_reservation_week():
    # get date
    today = datetime.now()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=6)

    return start_date.date(), end_date.date()
