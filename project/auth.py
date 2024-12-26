from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from . import db
from .models import User

# use blueprint
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # 新しくアカウント作った後にログインし直させるため
    if current_user.is_authenticated:
        logout_user()

    if request.method == 'POST':
        # check user info
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False  # keep login or not

        # find info of user
        user = User.query.filter_by(email=email).first()

        if not user : # no user found
            flash("Please check your login details and try again.(User not found)")
            return redirect(url_for('auth.login'))  # redirect
        elif not check_password_hash(user.password, password): # Email address or Password not match
            flash("Please check your login details and try again.((Password or Email not match))")
            return redirect(url_for('auth.login'))

        # passed
        login_user(user, remember=remember)
        return redirect(url_for('main.admin_confirm'))

    return render_template('login.html')


@auth.route('/signup',methods=['GET','POST'])
@login_required
def signup():
    if request.method == 'POST':
        # get val from DB and typed
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        # find existed user
        user = User.query.filter_by(email=email).first()

        if user:  # already existed so try again
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))

        # prepare for new user by hashing pass sha256
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'))

        # add user
        db.session.add(new_user)
        db.session.commit()

        # Done, go to login page
        flash("Created new user")

    return render_template('signup.html')

@auth.route('/logout')
@login_required  # login user only
def logout():
    logout_user()
    return redirect(url_for("main.main_page"))

