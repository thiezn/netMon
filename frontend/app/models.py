import datetime
from app import db

USER_ROLES = ('ROLE_ADMIN', 'ROLE_USER', 'ROLE_BUSINESS', 'ROLE_BAND')


class User(db.Model):
    """Class contains database model for all users of the site"""

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(120))
    datecreated = db.Column(db.DateTime)
    role = db.Column(db.Enum('ROLE_ADMIN',
                             'ROLE_USER'), default='ROLE_USER')
    active = db.Column(db.Boolean)

    def __repr__(self):
        """Prints out a nice human readable of the class"""
        return '<User %r>' % (self.name)

    def __init__(self, name=None,
                 password=None, email=None,
                 role=None, active=None):

        self.name = name
        self.email = email
        self.password = password
        self.datecreated = datetime.datetime.utcnow()
        self.role = role
        self.active = active

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
