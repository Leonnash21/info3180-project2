from . import db
from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash



class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    password = db.Column(db.String(255))
    age = db.Column(db.Integer)
    biography = db.Column(db.String(80))
    sex = db.Column(db.String(6))
    image=db.Column(db.LargeBinary)
    datejoined = db.Column(db.DateTime)
    
    
    
    def __init__(self, id, username, firstname, lastname, password, age, biography, sex, image, datejoined):
        
            self.id=id
            self.username=username
            self.firstname=firstname.title()
            self.lastname=lastname.title()
            self.password = password
            self.age=age
            self.biography=biography
            self.sex = sex.upper()
            self.image=image
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

    def get_id(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support
    
    def __repr__(self):
        return '<User %r>' % (self.username)
