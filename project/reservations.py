from flask import Blueprint
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
import re

from . import db
from .models import Reservation,Request

reservations = Blueprint('reservations', __name__)
STUDENT_ID_PATTERN = re.compile(r'^\d{2}[a-zA-Z]\d{4}[a-zA-Z]$') # student id pattern

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

    existed_reservation = Reservation.query.filter_by(
        reserved_date=reserved_date,
        reserved_time=reserved_time
    ).first()
    # check reservation(already exists)
    if existed_reservation:
        return  False

    # prepare reservation data
    new_reservation = Reservation(
        reserved_date=reserved_date,
        reserved_time=reserved_time
    )

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

# delete booking
def delete_booking(reserved_date, reserved_time):
    try:
        # 予約を検索して削除
        reservation = Reservation.query.filter_by(reserved_date=reserved_date, reserved_time=reserved_time).first()
        if reservation:
            db.session.delete(reservation)
            db.session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error: {e}")
        return False

# add db for request reservation
def request_booking(reserved_date, reserved_time,student_id):
    # same request ?
    existed_request = Request.query.filter_by(
        reserved_date=reserved_date,
        reserved_time=reserved_time,
        student_id=student_id
    )
    # decline
    if existed_request:
        return False

    new_request = Request(
        reserved_date=reserved_date,
        reserved_time=reserved_time,
        student_id=student_id
    )
    try:
        # insert request
        db.session.add(new_request)
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

# judge studentID
def judge_student_id(student_id):
    return bool(STUDENT_ID_PATTERN.match(student_id))