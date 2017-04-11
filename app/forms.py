from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired
from wtforms.fields import TextField, FileField, SelectField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired, DataRequired
 

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember me ')


class ProfileForm(Form):
    
    
    firstname = TextField('Firstname', validators=[Required()])
    lastname = TextField('Lastname', validators=[Required()])
    password = PasswordField('Password', validators=[Required(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    age = IntegerField('Age', validators=[Required()])
    sex = SelectField('Sex', choices=[('Male', 'Male'), ('Female','Female')], validators=[Required()])
    image = FileField('Profile Photo', validators=[FileRequired(), FileAllowed(['jpg,png'], 'Images Only!')])
    biography = TextField('Biography', validators=[Required()])