from . import db
from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
import random




class UserT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80), unique=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    password = db.Column(db.String(80),nullable=False)
    age = db.Column(db.Integer)    
    sex = db.Column(db.String(6))
    datejoined = db.Column(db.DateTime, nullable=False)
    wishes = db.relationship('Wish',backref='UserT')
    tokens = db.relationship('Token',backref='UserT',lazy='dynamic')
    
    def __init__(self, username, email=None, firstname=None, lastname=None,
                 password=None, age=None, sex=None, datejoined=None):

            self.username=username
            self.email=email
            self.firstname=firstname.title()
            self.lastname=lastname.title()
            self.password = password
            self.age=age
            self.sex = sex.upper()
            self.datejoined=datejoined
            
        
        
    def set_password(self, password):
        self.password = generate_password_hash(password)

   
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_userid(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support
    
    def to_json(self):
        return dict(userid=self.userid,username=self.username,
                    email=self.email,datejoined=self.datejoined)

            
class Wish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wishid = db.Column(db.Integer, db.ForeignKey(UserT.id), nullable=False)
    title = db.Column(db.String, nullable=False)
    websiteaddr = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    added_on = db.Column(db.DateTime,nullable=False)
    thumbnail = db.Column(db.String(255))
    
    
    def __init__(self, wishid, title=None, description=None, websiteaddr=None, 
                 added_on=None):
        
        self.wishid = wishid
        self.title = title
        self.description = description
        self.websiteaddr = websiteaddr
        self.added_on = added_on

    def get_id(self):
        return  unicode(self.wishid)
        
        
        

class Token(db.Model):
    
    id = db.Column(db.Integer, db.ForeignKey(UserT.id))
    tokens = db.Column(db.String(255), primary_key=True)
    
    def __init__(self, token):
        
        self.tokens = tokens




db.create_all()
    
