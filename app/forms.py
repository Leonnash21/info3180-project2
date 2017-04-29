from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email
from wtforms.fields import TextField, FileField, SelectField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired, DataRequired
from wtforms.fields.html5 import EmailField 
from wtforms import validators
from wtforms.widgets import TextArea
from flask_wtf.file import FileField, FileAllowed, FileRequired


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember me ')


class SignupForm(Form):
    
    firstname = TextField('Firstname', validators=[Required()])
    lastname = TextField('Lastname', validators=[Required()])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[Required(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    age = IntegerField('Age', validators=[Required()])
    sex = SelectField('Sex', choices=[('Male', 'Male'), ('Female','Female')], validators=[Required()])
    image = FileField('Profile Photo', validators=[FileRequired(), FileAllowed(['jpg,png'], 'Images Only!')])
    biography = TextField('Biography', validators=[Required()])
    

class WishForm(Form):
    title = TextField('Title',  validators=[Required()])
    description = TextField('Description',  validators=[Required()])
    websiteaddr = TextField('Reference',  validators=[Required()])
    # image


class ShareForm(Form):
    emails = TextField('Share with:', validators=[Required()])
    message = TextField('Optional Message', widget=TextArea())
    