from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from project.sendmail import generate_credentials

db = SQLAlchemy()
# setup flask-login
def setup_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User  # use models module
    # get user information by using primary key
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

def setup_blueprint(app):
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .reservations import reservations as res_blueprint
    app.register_blueprint(res_blueprint)
    from .auth import auth as auth_blueprint  # import auth.py
    app.register_blueprint(auth_blueprint)  # register
    from .sendmail import  sendmail as send_blueprint
    app.register_blueprint(send_blueprint)

def create_app():
    # setup flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # setup db
    db.init_app(app)
    # set up for login manager
    setup_login_manager(app)
    # setup blueprint
    setup_blueprint(app)
    # setup gmail api
    generate_credentials()
    return app
