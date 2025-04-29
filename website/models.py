from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    role = db.Column(db.String(50), nullable=False, default='employee')  
    approved = db.Column(db.Boolean, nullable=False, default=False) 
    notes = db.relationship('Note')

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_name   = db.Column(db.String(150), nullable=False)
    parent_name  = db.Column(db.String(150), nullable=False)
    age          = db.Column(db.Integer, nullable=False)
    email        = db.Column(db.String(150), nullable=False)
    phone        = db.Column(db.String(50))
    county       = db.Column(db.String(100))
    working_with = db.Column(db.String(150))


