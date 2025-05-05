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

class Parent(db.Model):
    __tablename__ = 'parent'
    id = db.Column(db.Integer, primary_key=True)
    parent_name  = db.Column(db.String(150), nullable=False)
    phone        = db.Column(db.String(50))
    email        = db.Column(db.String(150), nullable=False)
    address      = db.Column(db.String(300), nullable=False)
    zipcode      = db.Column(db.String(50))
    relationship = db.Column(db.String(150))
    language     = db.Column(db.String(150), nullable=False)
    ethnicity    = db.Column(db.String(150), nullable=False)
    staff_id     = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_parent_user'), nullable=False)
    staff        = db.relationship('User', backref='parents')
    services_seeking = db.Column(db.Text)
    
    children      = db.relationship(
                       'Child',
                       backref='parent',
                       cascade='all, delete-orphan'
                   )
    
class Child(db.Model):
    __tablename__ = 'child'
    id                = db.Column(db.Integer, primary_key=True)
    parent_id         = db.Column(db.Integer, db.ForeignKey('parent.id', name='fk_child_parent'), nullable=False)

    first_name        = db.Column(db.String(150), nullable=False)
    last_name         = db.Column(db.String(150), nullable=False)
    dob               = db.Column(db.Date)
    gender            = db.Column(db.String(10))
    language          = db.Column(db.String(150), nullable=False)
    ethnicity         = db.Column(db.String(150), nullable=False)
    insurance         = db.Column(db.String(150))
    doctor_visit      = db.Column(db.String(150))
    dentist_visit     = db.Column(db.String(150))
    working_with      = db.Column(db.String(150))
    disability        = db.Column(db.String(150))
    
    


