from flask import Blueprint,flash
from datetime import datetime, timedelta

from flask_sqlalchemy.model import Model
from sqlalchemy.exc import SQLAlchemyError
from typing import Type
import re

from . import db
from .models import Reservation,Request
from .sendmail import send_email

reservations = Blueprint('reservations', __name__)
STUDENT_ID_PATTERN = re.compile(r'^\d{2}[a-zA-Z]\d{4}[a-zA-Z]$') # student id pattern
# mail address setup
SEND_FROM ='support@cercil.net'
UNIV_ADDRESS = '@shinshu-u.ac.jp'

# get reserved_time
def get_booked_times(reserved_date):
    # find reserved data
    reserve = Reservation.query.filter_by(reserved_date=reserved_date).all()
    # push booked time in booked_times
    booked_times = []
    for r in reserve:
        booked_times.extend(generate_time_intervals(r.start_time, r.end_time))

    return booked_times

# get reserved_time for admin
def get_booked_times_details(reserved_date):
    reserve = Reservation.query.filter_by(reserved_date=reserved_date).all()
    booked_times = []
    for r in reserve: # insert like [ [10:00,10:30,11:00,11:30], 21t***** ]
        booked_times.append(generate_time_intervals(r.start_time, r.end_time))
        booked_times.append(r.reserver_id)

    return booked_times

# add reservation to db
def add_booking(reserved_date,start_time,end_time,reserver_id):

    # block double booking
    if check_duplicate(Reservation,reserved_date=reserved_date,start_time=start_time,end_time=end_time,reserver_id=reserver_id):
        return False
    if check_duplicate_detail(reserved_date=reserved_date,start_time=start_time,end_time=end_time):
        return False
    # prepare reservation data  *****Reservation table needs date,time,reserver_id(ex student_id or admin)*****
    new_reservation = Reservation(
        reserved_date=reserved_date,
        start_time=start_time,
        end_time=end_time,
        reserver_id=reserver_id
    )
    try:
        # insert reservation
        db.session.add(new_reservation)
        db.session.commit()
        if reserver_id != "admin":
            # send reserve mail
            send_email(
                to=reserver_id + UNIV_ADDRESS,  # student_id@(univ address) ex. 00t0000a@shinshu-u.ac.jp
                subject="体育館予約確定のお知らせ",
                body="""{} {} - {}の予約が確定しました。""".format(reserved_date, start_time, end_time)
            )
        return True
    except SQLAlchemyError as e:
        # failed
        db.session.rollback()
        # error message
        print(f"Error: {e}")
        return False

# delete booking
def delete_booking(reserved_date, start_time):
    try:
        # 予約を検索して削除
        reservation = Reservation.query.filter_by(reserved_date=reserved_date, start_time=start_time).first()
        if reservation:
            db.session.delete(reservation)
            db.session.commit()
            if reservation.reserver_id != "admin":
                send_email(
                    to=reservation.reserver_id + UNIV_ADDRESS,  # student_id@(univ address) ex. 00t0000a@shinshu-u.ac.jp
                    subject="体育館予約申請の削除について",
                    body="""{} {} - {}の予約が管理者によって削除されました。""".format(reservation.reserved_date,
                                                                                      reservation.start_time,
                                                                                      reservation.end_time)
                )
            return True
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error: {e}")
        return False

# add db for request reservation
def add_request_booking(reserved_date,start_time,end_time,student_id):
    # same request ?
    if check_duplicate(Request,reserved_date=reserved_date,start_time=start_time,end_time=end_time,student_id=student_id):
        return False

    new_request = Request(
        reserved_date=reserved_date,
        start_time=start_time,
        end_time=end_time,
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

# delete data from Request DB
def delete_request_booking(request_id,condition):
    try:
        # find request by using id(UNIQUE)
        requests = Request.query.filter_by(id=request_id).first()
        if requests:
            db.session.delete(requests)
            db.session.commit()
            # for reject
            if condition is False:
                # send reject mail
                send_email(
                    to=requests.student_id+ UNIV_ADDRESS,  # student_id@(univ address) ex. 00t0000a@shinshu-u.ac.jp
                    subject="体育館予約申請の削除について",
                    body="""{} {} - {}の予約申請が管理者によって削除されました。""".format(requests.reserved_date, requests.start_time, requests.end_time)
                )

        return True
    except SQLAlchemyError as e:
        db.session.rollback()
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

# check duplicate in database(same data)
def check_duplicate(table_class: Type[Model], **filters) -> bool:
    duplicate = table_class.query.filter_by(**filters).first()
    return duplicate is not None # if it exists return True

def check_duplicate_detail(reserved_date,start_time,end_time):
    new_reservation = generate_time_intervals(start_time,end_time)
    existed_reservation = get_booked_times(reserved_date)

    print("new_reservation", new_reservation)
    print("existed_reservation", existed_reservation)

    for elements in new_reservation:
        if elements in existed_reservation:
            return True

    return False
# generate time ex) start=10:00,end=12:00 -> return [10:00,10:30,11:00,11:30]
def generate_time_intervals(start: str, end: str):
    start_time = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")

    time_list = []
    current_time = start_time

    while current_time < end_time:  # exclude end_time
        time_list.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=30)  # add 30min

    return time_list
# check duplication of reservation time
def check_reservation_time(start_time: str, end_time: str,date):
    start_time = datetime.strptime(start_time, "%H:%M")
    end_time = datetime.strptime(end_time, "%H:%M")
    if start_time > end_time:
        flash("開始時間が終了時間より遅いです。もう一度やり直してください")
        return False

    if start_time == end_time:
        flash ("開始時間と終了時間が一致しています。もう一度やり直してください")
        return False

    flash("メールを送信しました。予約申請を確定してください")
    return True