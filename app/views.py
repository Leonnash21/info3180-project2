"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, jsonify, session, g
from flask_login import login_user, logout_user, current_user, login_required
from forms import LoginForm, ProfileForm
from models import UserProfile
import os
import math
from app import db
from werkzeug import secure_filename
from datetime import date, datetime
from time import strftime
import random
from werkzeug.security import generate_password_hash, check_password_hash



###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

@app.route('/about/')
@login_required
def about():
    """Render the website's about page."""
    return render_template('about.html')
    
@app.route('/profile/', methods = ['GET', 'POST'])
def add_profile():
    form = ProfileForm()
    # iURL = url_for('app', filename='static/images/')
    
    if request.method == 'POST' and form.validate_on_submit:
        
        
        username =(request.form['firstname']) + str(random.randint(10,1000))
        id = random.randint(1000000, 1099999)
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        age = request.form['age']
        biography = request.form['biography']
        sex =  request.form['sex']
       
        file = request.files['image']
        image = secure_filename(file.filename)
        file.save(os.path.join("app/static/images", image))
        password = generate_password_hash(request.form['password'])
        datejoined= datetime.now().strftime("%a, %d %b %Y")

        profile = UserProfile (id, username, firstname, lastname, password, age, biography, sex, image, datejoined)
        db.session.add(profile)
        db.session.commit()
        
        flash ('User ' + username + ' sucessfully added!', 'success')
        flash ('Please proceed to "Login"', 'success')
        return redirect (url_for('add_profile'))
        
   
    
    flash_errors(form)        
    return render_template('add_profile.html', form=form)
    
    
@app.route('/profiles/',methods=["POST","GET"])
def list_profiles():
    
    users = db.session.query(UserProfile).all()
    if request.headers['Content-Type']=='application/json' or request.method == "POST":
        ulist=[]
        for user in users:
            ulist.append({'id':user.id, 'username':user.username})
            users = {'users': ulist}
        return jsonify(users)
                
    return render_template('list_profiles.html', users=users)

@app.route('/profile/<int:id>',methods=["POST","GET"])
# @login_required
def view_profile(id):
    users = UserProfile.query.filter_by(id=id).first()
    iURL = url_for('static', filename='images/' +users.image) 

    if request.headers['Content-Type']=='application/json' or request.method == "POST":
        return jsonify(id=users.id, username=users.username, image=users.image, gender=users.sex, age=users.age, datejoined=users.datejoined)
        
    else:
        
        userp = {'id':users.id, 'username':users.username, 'image':iURL, 'age':users.age, 'firstname':users.firstname, 'lastname':users.lastname, 'gender':users.sex, 'biography':users.biography, 'date joined':users.datejoined}
        return render_template('view_profile.html', userp=userp)
        
        
    
@app.route('/securepage/')
@login_required
def securepage():
    """Render a secure page on our website that only logged in users can access."""
    return render_template('securepage.html')
    
    
@app.route('/login/', methods=["GET", "POST"])
def login():
    
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('home'))
        
        
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        
        
        username = form.username.data
        password = form.password.data
        remember_me = form.password.data
        
        user = UserProfile.query.filter_by(username=username).first()
        
        
        if user is not None:
            if check_password_hash(user.password, password):
                
                login_user(user, remember = remember_me)
                
            # remember to flash a message to the user
            flash ('Logged in successfully.', 'success')
            return redirect(url_for("securepage")) 
        else:
            flash ('Username or Password incorrect','danger')
    flash_errors(form)
    return render_template("login.html", form=form)

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session

@login_manager.user_loader
def load_user(id):
    return UserProfile.query.get(int(id))


@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('home'))




def flash_errors(form):
    for field, errors in form.errors.items():
        
        for error in errors:
            flash(u"Error in the %s field - %s" % (getattr(form, field).label.text,error), 'danger')
            
            
###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")
