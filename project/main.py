from flask import Flask, render_template, request, redirect, url_for, jsonify, Blueprint, flash
from flask_login import login_required, current_user

from . import reservations
from .reservations import get_booked_times, add_booking, judge_student_id
from . import sendmail

main = Blueprint('main', __name__)
# define available time for reserve
AVAILABLE_TIMES = ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00']

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

@main.route('/reserve',methods=['POST'])
def reserve(): # process reservations
    reserved_date = request.form['date']
    reserved_time = request.form['time']
    student_id = request.form['student_id']

    if not judge_student_id(student_id): # judge student id
        flash("不正な学籍番号です。もう一度やり直してください")
        return redirect(url_for('main.main_page',date=reserved_date)) # redirect same page

    # send reserve mail
    sendmail.send_email(
        to=student_id+sendmail.UNIV_ADDRESS, # student_id@(univ address) ex. 00t0000a@shinshu-u.ac.jp
        subject="体育館予約の確認",
        body="""予約を確定させるために、<a href="127.0.0.1/confirm/{}/{}+{}">こちら</a>をクリックしてください。""".format(sendmail.hash_student_id(student_id=student_id),reserved_date,reserved_time)
    )

    flash("メールを送信しました。予約を確定してください")
    return redirect(url_for('main.main_page', date=reserved_date))  # redirect same page


@main.route('/admin')
@login_required
def admin():
    return render_template('admin.html',name=current_user.name)