"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

import os
import math
import flask
import base64
import random
import smtplib
import json
import bcrypt
import urlparse


from app import app, db, login_manager
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g
from flask_login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import SQLAlchemy
from forms import LoginForm, SignupForm, WishForm
from models import UserT, Wish, Token
import requests
import time
from app import db
from werkzeug import secure_filename
from datetime import date, datetime
from time import strftime
from random import randint
from werkzeug.security import generate_password_hash, check_password_hash
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
    
@app.route('/api/users/register', methods = ['GET', 'POST'])
def add_profile():
    form = SignupForm()
    
    if request.method == 'POST' and form.validate_on_submit:
        
        jsonD=json.loads(request.data)
        
        profile=UserT(jsonD.get('username'), firstname=jsonD.get('firstname'),
                      lastname=jsonD.get('lastname'), email=jsonD.get('email'),
                      password=bcrypt.hashpw(jsonD.get('password').encode('utf-8'), bcrypt.gensalt()),
                      datejoined=datetime.now().strftime("%Y-%m-%d"),
                      age=int(jsonD.get('age')), sex=str(jsonD.get('sex'))[:6])
        
        
        if profile:
            db.session.add(profile)
            db.session.commit()
            response = jsonify({"error":None,"data":{'firstname':jsonD.get('firstname'),'lastname':jsonD.get('lastname'),'username':jsonD.get('username'),'email':jsonD.get('email'), 'age':jsonD.get('age'), 'sex':jsonD.get('sex')},"message":"Sucess"})
        
        else:
            response = jsonify({"error":"1","data":{},'message':'not signed up'})
        return response

        
    
@app.route('/securepage/')
@login_required
def securepage():
    """Render a secure page on our website that only logged in users can access."""
    return render_template('securepage.html')
    
    
@app.route('/api/users/login', methods=["GET", "POST"])
def login():
    
    if request.method == "POST":
        jsonD= json.loads(request.data)
        user = UserT.query.filter_by(email=jsonD.get('email')).first()
        if user and user.password == bcrypt.hashpw(jsonD.get('password').encode('utf-8'),
        user.password.decode().encode('utf-8')):
            
            token = tokenGenerate()
            # token = Token(user.id)
            db.session.add(token)
            db.session.commit()
            
            response = jsonify({"error":None,"data":{'id':user.id,'username':jsonD.get('username'),'token':token.token},"message":"logged"})
            
        else:
            response = jsonify({"error":"1","data":{},"message":'not logged in'})
    return response
        
        
# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session

@login_manager.user_loader
def load_user(id):
    return UserT.query.get(int(id))


@app.route('/api/users/logout', methods=["POST"])
def logout():
    jsonD= json.loads(request.data)
    token =Token.query.filter_by(token=jsonD('token')).first()
    if token:
        db.session.delete(token)
        db.session.commit()
        response = jsonify({'status':'logged out'})
    else:
        response = jsonify({'status':'not logged out'})
    return response
    
# tokens = db.session.query(Token).all()
#         tokens = map(lambda x:x.token,tokens)
#         token = tokenGenerate()
#         while token in tokens:
#             token = tokenGenerate()
            
def tokenGenerate():
    return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range (16))



def flash_errors(form):
    for field, errors in form.errors.items():
        
        for error in errors:
            flash(u"Error in the %s field - %s" % (getattr(form, field).label.text,error), 'danger')



@app.route('/api/users',methods=["POST","GET"])
@login_required
def list_profiles():
    
    users = db.session.query(UserT).all()
    ulist=[]
    for user in users:
        ulist.append({'id':user.id, 'firstname':user.firstname, 
        'lastname':user.lastname, 'username':user.username, 
        'email':user.email, 'age':user.age, 'sex':user.sex})
        
    if (len(ulist)>0):
        response = jsonify({"error":None,"data":{"users":ulist},"message":"Success"})
    else:
        response = jsonify({"error":"1","data":{},"message":"did not retrieve all users"})
    return response            
    
    
    
@app.route('/api/users/{userid}/', methods = ["GET","POST"])
@login_required
def profile_view(userid):
    users = UserT.query.filter_by(userid=userid).first()
    
    if users:
        
        response = jsonify({"error":None,"data":{'id':users.id,
                   'firstname':users.firstname,'lastname':users.lastname,
                   'username':users.username,'email':users.email,'age':users.age,
                   'sex': users.sex, 'datejoined':timeI(users.datejoined)},
                   "message":"Success"})

    else:
        
        response = jsonify({"error":"1","data":{},'message':'did not retrieve user'})
    
    return response
            

@app.route('/api/users/{userid}/wishlist', methods = ["GET", "POST", "DELETE"])
@login_required
def addwish(userid):
    if request.method == "POST":
        users =UserT.query.filter_by(id=wishid).first()
        jsonD= json.loads(request.data)
        wish = Wish(users.id,websiteaddr=jsonD.get('websiteaddr'),thumbnail=jsonD.get('thumbnail'),
               title=jsonD.get('title'),description=jsonD.get('description'),
               added_on=datetime.now().strftime("%Y-%m-%d"))
        if wish:
            
            db.session.add(wish)
            db.session.commit()
            response = jsonify({"error":None,"data":{'userid':userid,
                       'url':jsonD.get('websiteaddr'),'thumbnail':wish.thumbnail,
                       'title':jsonD.get('title'),
                       'description':jsonD.get('description')},"message":"Success"})
          
        else:
            response = jsonify({"error":"1", "data":{},'message':'wish not made'})
    
    elif request.method == "DELETE":
        users =UserT.query.filter_by(id=wishid).first()
        jsonD= json.loads(request.data)
        wish = Wish(users.id,websiteaddr=jsonD.get('websiteaddr'),thumbnail=jsonD.get('thumbnail'),
               title=jsonD.get('title'),description=jsonD.get('description'),
               added_on=datetime.now().strftime("%Y-%m-%d"))
        if wish:
            
            db.session.delete(wish)
            db.session.commit()
            response = jsonify({"error":None,"data":{'userid':userid,
                       'url':jsonD.get('websiteaddr'),'thumbnail':wish.thumbnail,
                       'title':jsonD.get('title'),
                       'description':jsonD.get('description')},"message":"Success"})
          
        else:
            response = jsonify({"error":"1", "data":{},'message':'wish not made'})
        
        
    else:
        
        
        users = UserT.query.filter_by(id=userid).first()
        wishes = Wish.query.filter_by(userid=users.id).all()
        wishl = []
        for wish in wishes:
            wishl.append({'title':wish.name,'websiteaddr':wish.websiteaddr,
            'thumbnail':wish.thumbnail,'description':wish.description,
            'added_on':timeI(wish.added_on)})
            
        if(len(wishl)>0):
            response = jsonify({"error":"null",
                        "data":{"user":users.firstname + " " + users.lastname, 
                        "wishes":wishl},"message":"Success"})
        else:
            response = jsonify({"error":"1","data":{},"message":"Unable to get wishes"})        
    return response


@app.route('/api/users/{userid}/wishlist/{itemid}', methods = ["GET", "POST", "DELETE"])
@login_required
def wishlist_item(userid, itemid):
    if request.method == 'POST':
        # do the get stuff
        users=db.session.query(User).filter_by(userid=userid).first()
        wish=db.session.query(Wish).filter_by(itemid=itemid).first()
        response = 'POSTED'  # change this line
    elif request.method == 'DELETE':
        # do the delete dance
        response = 'DELETED'  # change this line
    else: # it's a get
        # getter
        response = 'GOTTEN'  # change this line
    return response


app.route('/api/thumbnails', methods = ["GET"])
def view_thumbs():
    url = request.args.get('url')
    soup = BeautifulSoup.BeautifulSoup(requests.get(url).text)
    images = BeautifulSoup.BeautifulSoup(requests.get(url).text).findAll("img")
    
    imageList = []
    
    
    og_image = (soup.find('meta', property='og:image') or
                    soup.find('meta', attrs={'name': 'og:image'}))
    if og_image and og_image['content']:
        imageList.append(urlparse.urljoin(url, og_image['content']))
    
    
    thumbnail_spec = soup.find('link', rel='image_src')
    if thumbnail_spec and thumbnail_spec['href']:
        imageList.append(urlparse.urljoin(url, thumbnail_spec['href']))
    
    image = "%s"
    for img in images:
        results= image % urlparse.urljoin(url, img["src"])
        imageList+=[results]
           
    if(len(imageList)>0):
        response = jsonify({'error':None, "data":{"thumbnails":imageList},"message":"Success"})
    else:
        response = jsonify({'error':'1','data':{},'message':'Thumbnail extraction failed'})
    return response
    
    
    
# @app.route('/api/users/{userid}/wishlist/{itemid}', methods=['DELETE'])
# def delete_entry():
#     users = db.session.query(Wish).all()
    
#       db.session.delete(wishid)
#       db.session.commit()
#       flash('delete done.')
#   return redirect(url_for(''))
  
  
  
# ability to share/send wishlist
@app.route('/api/users/{userid}')
def share (userid):
        
    users = UserT.query.filter_by(id=userid).first()
    jsonD = json.loads(request.data)
    fromaddr = str(users.email)
    sender = str(users.firstname)+str(users.lastname)
    emails = jsonD.get['emails']
    message = jsonD.get['message']
    subject = jsonD.get['subject']
    wishes = jsonD.get['wishes']
    wishl = []
    
    for wish in wishes:
        wishl.append(str(wish))
    allWish = ", ".join(str(wish) for wish in wishl)
    msg = MIMEMultipart()
    
    elist = []
    for email in emails:
        elist.append(str(email))
    
    msg['From'] = fromaddr
    msg['To'] = ", ".join(elist)
    msg['Subject'] = subject
    
    header = 'View your friends wishlist. See what the like.'
    footer = 'Follow the link to view app'
    
    msg.attach(MIMEText(header,'plain'))
    msg.attach(MIMEText(message,'plain'))
    msg.attach(MIMEText('Their Wishlist: '+ allWish,'plain'))
    msg.attach(MIMEText(footer,'plain'))
    
    messageToSend = msg.as_string()
    
    username= ''
    password= ''
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(sender,elist,messageToSend)
    server.quit()
    response = jsonify({"error":None,"data":{"emails":elist,"subject":subject,"message":message,"wishes":allWish},"message":"Success"})
    return response




###
# The functions below should be applicable to all Flask apps.
###





        
@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)
    
# @app.before_request
# def before_request():
#     method = request.form.get('_method', '').upper()
#     if method:
#         request.environ['REQUEST_METHOD'] = method
#         ctx = flask._request_ctx_stack.top
#         ctx.url_adapter.default_method = method
#         assert request.method == method



@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 0 minutes.
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

def timeI(entry):
    day = time.strftime("%a")
    date = time.strftime("%d")
    if (date <10):
        date = date.lstrip('0')
    month = time.strftime("%b")
    year = time.strftime("%Y")
    return day + ", " + date + " " + month + " " + year
@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")
