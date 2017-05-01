from app import app
from . import db
from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from datetime import datetime, date, time, timedelta
import random
import jwt



class UserT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    password = db.Column(db.String(80),nullable=False)
    age = db.Column(db.Integer)    
    sex = db.Column(db.String(6))
    datejoined = db.Column(db.DateTime, nullable=False)
    wishes = db.relationship('Wish', backref='user')
    tokens = db.relationship('Token', backref='user',lazy='dynamic')
    
    def __init__(self, email=None, firstname=None, lastname=None,
                 password=None, age=None, sex=None, datejoined=None):

            
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
        return dict(userid=self.userid,
                    email=self.email,datejoined=self.datejoined)
                    
    def encode_auth_token(self, user_id):
        
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(days=0, seconds=5),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e
            
    @staticmethod
    def decode_auth_token(auth_token):
        
        
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'
    
            
class Wish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userT.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    websiteaddr = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    added_on = db.Column(db.DateTime,nullable=False)
    thumbnail = db.Column(db.String(255))
    
    
    def __init__(self, user_id, title=None, description=None, websiteaddr=None, 
                 added_on=None):
        
        self.user_id = user_id
        self.title = title
        self.description = description
        self.websiteaddr = websiteaddr
        self.added_on = added_on

    def get_id(self):
        return  unicode(self.wishid)
        
        
        

class Token(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('userT.id'))
    
    def __init__(self, token, user_id=None, user=None):
        
        if user_id:
            self.user_id = user_id
        elif user and user.id:
            self._user_id = user.id
        self.token = token




class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)
    
    
    @staticmethod    
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False

db.create_all()
    
