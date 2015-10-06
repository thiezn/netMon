from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from hashlib import md5
from werkzeug.contrib.fixers import ProxyFix


# import the views and models to start the main
# application logic(vim will report an issue as it's not used)
# from app import views, models


app = Flask(__name__)
app.debug = True
app.wsgi_app = ProxyFix(app.wsgi_app)

# load the config file
app.config.from_object('config')

# init the database (uses settings from config file)
db = SQLAlchemy(app)



from .models import User


def dbinit():
    """ Populates the database with dummy data """
    db.drop_all()
    db.create_all()
    db.session.add(User(name='thiezn',
                        password=hash_string('Kweetniet0'),
                        email='thies@home.com',
                        role='ROLE_ADMIN',
                        active=True))
    db.session.add(User(name='thies',
                        password=hash_string('Kweetniet0'),
                        email='thijs@home.com',
                        role='ROLE_USER',
                        active=True))
    db.session.add(User(name='John',
                        password=hash_string('Kweetniet0'),
                        email='john@doe.com',
                        role='ROLE_USER',
                        active=True))
    db.session.commit()


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


def hash_string(string):
    """ Converts a password to hash """
    salted_hash = (string + app.config['SECRET_KEY']).encode('utf-8')
    return md5(salted_hash).hexdigest()


from app import views, models

