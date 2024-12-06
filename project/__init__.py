from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def setup_blueprint(app):
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .reservations import reservations as res_blueprint
    app.register_blueprint(res_blueprint)

def create_app():
    # setup flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # setup db
    db.init_app(app)
    # setup blueprint
    setup_blueprint(app)

    return app
