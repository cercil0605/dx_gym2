import datetime

from flask import Flask, render_template, request, redirect, url_for, jsonify, Blueprint, flash
from flask_login import login_required, current_user

from . import reservations
from .models import StudentInfo, Reservation, Request
from .reservations import get_booked_times, add_booking, judge_student_id, delete_booking, add_request_booking,delete_request_booking,check_reservation_time,get_booked_times_details
from . import sendmail

main = Blueprint('main', __name__)
# define available time for reserve   8:00 - 18:30
AVAILABLE_TIMES = [
    datetime.time(hour, minute).strftime('%H:%M')
    for hour in range(8, 19)  # Change to 19 to include 18:00
    for minute in (0, 30)
]
# send address (for test use 127.---)
# SEND_ADDRESS = "127.0.0.1"
SEND_ADDRESS = "reserve.cercil.net"
@main.route('/')
def main_page(): # show main page(for reserve)
    start_date, end_date = reservations.get_reservation_week() # get available day
    reserved_date = request.args.get('date',start_date.isoformat()) # start day and shaping
    booked_times = get_booked_times(reserved_date)
    # return for html
    return render_template(
        'index.html',
        available_times=AVAILABLE_TIMES,
        booked_times=booked_times,
        reserved_date=reserved_date,
        start_of_week=start_date,
        end_of_week=end_date
    )

@main.route('/api/get_reservations',methods=['GET'])
def get_reserved_times(): # get reservations info
    reserved_date = request.args.get('date')
    booked_times = get_booked_times(reserved_date) # find reserved time in 'date'(ex 2024-12-01)
    return jsonify(booked_times) # return json pattern

# for admin, show reserved_time and reserver
@main.route('/api/get_reservations_detail',methods=['POST'])
def get_reservations_detail():
    date = request.args.get('date')
    reserved_data = get_booked_times_details(date)
    print(reserved_data)
    return jsonify(reserved_data)



@main.route('/reserve',methods=['POST'])
def reserve(): # process reservations
    reserved_date = request.form['date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    student_id = request.form['student_id']
    # judge start_time and end_time are correct or not
    if not check_reservation_time(start_time, end_time, reserved_date):
        return redirect(url_for('main.main_page'))

    # send reserve mail
    sendmail.send_email(
        to=student_id+sendmail.UNIV_ADDRESS, # student_id@(univ address) ex. 00t0000a@shinshu-u.ac.jp
        subject="体育館予約申請の確認",
        body="""{} {} - {} の予約申請を完了させるために、<a href="{}/confirm/{}/{}+{}-{}">こちら</a>をクリックしてください。"""
        .format(
            reserved_date,
                start_time,
                end_time,
                SEND_ADDRESS,
                sendmail.hash_student_id(student_id=student_id),
                reserved_date,
                start_time,
                end_time
                )
    )
    return redirect(url_for('main.main_page'))



# confirm reservation
@main.route('/confirm/<string:hash_id>/<string:reserved_date>+<string:start_time>-<string:end_time>')
def confirm(hash_id,reserved_date,start_time,end_time):
    reserve_student = StudentInfo.query.filter_by(hashed_id=hash_id).first()

    if reserve_student:
        if add_request_booking(reserved_date=reserved_date,start_time=start_time,end_time=end_time,student_id=reserve_student.student_id):# first access, add date,time,student_id
            return "予約申請が完了しました。この画面は閉じて構いません。"
        else: # second access or if the time was already reserved
            return "予約申請が完了済みです。"

    else: # block unauthorized access
        return "存在しない予約申請です。"

# for admin check request
@main.route('/request')
@login_required
def admin_confirm():
    requests = Request.query.all()
    return render_template('requests.html',requests=requests)

# add booking(for student)　　　****必要改善****
@main.route('/approve', methods=['POST'])
def student_approve_reservation():
    # get request data
    request_id = request.form['request_id']
    requests = Request.query.filter_by(id=request_id).first()
    # add booking
    if add_booking(reserved_date=requests.reserved_date, start_time=requests.start_time,end_time=requests.end_time,reserver_id=requests.student_id):
        # delete data from requestDB to disappear the request
        delete_request_booking(request_id=request_id,condition=True)
        return redirect(url_for('main.admin_confirm'))
    else:
        flash("予約確定失敗")
        return redirect(url_for('main.admin_confirm'))

#reject booking(for student)
@main.route('/reject', methods=['POST'])
def student_reject_reservation():
    # get request data
    request_id = request.form['request_id']
    # delete
    if delete_request_booking(request_id=request_id,condition=False):
        return redirect(url_for('main.admin_confirm'))
    else:
        flash("予約削除に失敗しました")
        return redirect(url_for('main.admin_confirm'))


# for admin
@main.route('/admin')
@login_required
def admin():
    return render_template('admin.html',user_name=current_user.name,available_times=AVAILABLE_TIMES)

# add booking (for admin)
@main.route('/admin/reserve', methods=['POST'])
def admin_reserve():
    # the span of reservation of admin is 30 min
    try :
        data = request.get_json()
        reserved_date = data.get('date')
        start_time = data.get('start_time')
        end_time = (datetime.datetime.strptime(data.get('start_time'), "%H:%M") + datetime.timedelta(minutes=30)).strftime("%H:%M")

        if add_booking(reserved_date=reserved_date, start_time=start_time,end_time=end_time,reserver_id="admin"):
            return jsonify({'success': True, 'message': '予約が確定しました'}), 200
        else:
            return jsonify({'success': False, 'message': '予約に失敗しました'}), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': '内部エラーが発生しました'}), 500

# delete booking(for admin)
@main.route('/admin/delete', methods=['POST'])
def admin_delete_reservation():
    data = request.get_json()
    reserved_date = data.get('date')
    reserved_start_time = data.get('start_time')

    if delete_booking(reserved_date,reserved_start_time):  # Use delete_booking function
        return jsonify({'success': True, 'message': '予約が削除されました'}), 200



