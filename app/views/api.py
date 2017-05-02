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
import requests
import requests
import time
import jwt

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from requests.auth import HTTPBasicAuth
from .. import app, db, login_manager
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g
from flask_login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import SQLAlchemy
from ..models import UserT, Wish, Token, BlacklistToken
from werkzeug import secure_filename
from datetime import date, datetime, timedelta
from time import strftime
from random import randint
from werkzeug.security import generate_password_hash, check_password_hash
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


        


JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20


###
# Routing for your application.
###

    
@app.route('/api/users/register', methods = ['GET', 'POST'])
def add_profile():

    if request.method == 'POST':
        
        jsonD=json.loads(request.data)
        user = UserT.query.filter_by(email=jsonD.get('email')).first()
        profile=UserT(firstname=jsonD.get('firstname'),
                      lastname=jsonD.get('lastname'), email=jsonD.get('email'),
                      password=bcrypt.hashpw(jsonD.get('password').encode('utf-8'), bcrypt.gensalt()),
                      datejoined=datetime.now().strftime("%Y-%m-%d"),
                      age=int(jsonD.get('age')), sex=str(jsonD.get('sex'))[:6])
        
        
        if profile:
            
            
            db.session.add(profile)
            db.session.commit()
            
            payload = {
                    'user_id': jsonD.get('id'),
                    'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                    }
            auth_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
            responseObject = {
                
                'status': 'success',
                'message': 'Successfully registered.',
                'auth_token': auth_token.decode('utf-8')
                }
            return make_response(jsonify(responseObject)), 201
            
        elif not profile:
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            return make_response(jsonify(responseObject)), 202
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Some error occurred. Please try again.'
                }
            return make_response(jsonify(responseObject)), 401
           
        
            
                
            # response = jsonify({"error":None,"data":{'firstname':jsonD.get('firstname'),
            #             'lastname':jsonD.get('lastname'),'email':jsonD.get('email'), 
            #             'age':jsonD.get('age'), 'sex':jsonD.get('sex')},"message":"Sucess"})
        
    

        
    
@app.route('/securepage/')
@login_required
def securepage():
    """Render a secure page on our website that only logged in users can access."""
    return render_template('securepage.html')
    
    
@app.route('/api/users/login', methods=["GET", "POST"])
def login():
    
    if request.method == "POST" :
        jsonD= json.loads(request.data)
        user = UserT.query.filter_by(email=jsonD.get('email')).first()
        
        # usrPass = "jsonD.get('id'):jsonD.get('password')"
        
        
        
        if user and user.password == bcrypt.hashpw(jsonD.get('password').encode('utf-8'),
        user.password.decode().encode('utf-8')):
            
            # auth_token =base64.b64encode(usrPass)
            if jwt_token:
                
                payload = {
                    'user_id': jsonD.get('id'),
                    'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                    }
                jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
                    
                    
                token = tokenGenerate()
                tokenobj = Token(token, user.id)
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'auth_token':jwt_token.decode('utf-8'),
                    'data':{'id':user.id,'email':jsonD.get('email'), 
                    'firstname': jsonD.get('firstname'),'token':token}
                }
                
               
                db.session.add(tokenobj)
                db.session.commit()
            
                return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'Try again',
                    "data":{}
                }
            return make_response(jsonify(responseObject)), 500
            
            
    
# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
# tokens = db.session.query(Token).all()
# tokens = map(lambda x:x.token,tokens)
# token = tokenGenerate()
# while token in tokens:
#     token = tokenGenerate()

@login_manager.user_loader
def load_user(auth_token):
    return UserT.query.get(auth_token)


@app.route('/api/users/logout', methods=["POST"])
def logout():
    
    auth_header = request.headers.get('Authorization')
    
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    if auth_token:
        resp = UserT.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            # mark the token as blacklisted
            blacklist_token = BlacklistToken(token=auth_token)
            try:
                # insert the token
                db.session.add(blacklist_token)
                db.session.commit()
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully logged out.'
                }
                return make_response(jsonify(responseObject)), 200
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': e
                }
                return make_response(jsonify(responseObject)), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
    else:
        responseObject = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return make_response(jsonify(responseObject)), 403


            
def tokenGenerate():
    return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range (16))



def flash_errors(form):
    for field, errors in form.errors.items():
        
        for error in errors:
            flash(u"Error in the %s field - %s" % (getattr(form, field).label.text,error), 'danger')



# @app.route('/api/users',methods=["POST","GET"])
# @login_required
# def list_profiles():
    
#     users = db.session.query(UserT).all()
#     ulist=[]
#     for user in users:
#         ulist.append({'id':user.id, 'firstname':user.firstname, 
#         'lastname':user.lastname,
#         'email':user.email, 'age':user.age, 'sex':user.sex})
        
#     if (len(ulist)>0):
#         response = jsonify({"error":None,"data":{"users":ulist},"message":"Success"})
#     else:
#         response = jsonify({"error":"1","data":{},"message":"did not retrieve all users"})
#     return response            
    
    
@app.route('/api/users', methods=["GET"])
@login_required
def get():
    # get the auth token
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    if auth_token:
        resp = UserT.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            user = UserT.query.filter_by(id=resp).first()
            responseObject = {
                'status': 'success',
                'data': {
                    'user_id': user.id,
                    'email': user.email,
                    'admin': user.admin,
                    'registered_on': user.datejoined
                }
            }
            return make_response(jsonify(responseObject)), 200
        responseObject = {
            'status': 'fail',
            'message': resp
        }
        return make_response(jsonify(responseObject)), 401
    else:
        responseObject = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return make_response(jsonify(responseObject)), 401
        
        
@app.route('/api/users/<userid>', methods = ["GET","POST"])
# @login_required  # commented temporarily so I can work on the front end
def profile_view(userid):
    users = UserT.query.filter_by(id=userid).first()
    
    if users:
        
        response = jsonify({"error":None,"data":{'id':users.id,
                   'firstname':users.firstname,'lastname':users.lastname,
                   'email':users.email,'age':users.age,
                   'sex': users.sex, 'datejoined':timeI(users.datejoined)},
                   "message":"Success"})

    else:
        
        response = jsonify({"error":"1","data":{},'message':'did not retrieve user'})
    
    return response
            

@app.route('/api/users/<userid>/wishlist', methods = ["GET", "POST", "DELETE"])
@login_required
def wishlist(userid):
    if request.method == "POST":
        users =UserT.query.filter_by(id=wishid).first()
        jsonD= json.loads(request.data)
        wish = Wish(users.id,websiteaddr=jsonD.get('websiteaddr'),thumbnails=jsonD.get('thumbnail'),
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
        jsonD= json.loads(request.data)
        wishid=jsonD.get(wishid)
        users =UserT.query.filter_by(id=wishid).first()
        wish = Wish(users.id,websiteaddr=jsonD.get('websiteaddr'),thumbnail=jsonD.get('thumbnail'),
               title=jsonD.get('title'),description=jsonD.get('description'),
               added_on=datetime.now().strftime("%Y-%m-%d"))
        for w in wish:
            
            db.session.delete(w)
            db.session.commit()
            response = jsonify({"error":None,"data":{'userid':userid,
                       'url':jsonD.get('websiteaddr'),'thumbnail':wish.thumbnail,
                       'title':jsonD.get('title'),
                       'description':jsonD.get('description')},"message":"Success"})
          
        else:
            response = jsonify({"error":"1", "data":{},'message':'wish not made'})
        
        
    else:
        
        
        users = UserT.query.filter_by(id=userid).first()
        wishes = Wish.query.filter_by(user_id=users.id).all()
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


@app.route('/api/users/<userid>/wishlist/<itemid>', methods = ["GET", "POST", "DELETE"])
@login_required
def wishlist_item(userid, itemid):
    if request.method == 'POST':
        # do the post stuff
        user= db.session.query(UserT).filter_by(userid=userid).first()
        wish= db.session.query(Wish).filter_by(itemid=itemid)
        db.session.delete(wish)
        db.session.commit()
        response = jsonify({"error": None, "message":"Success"})
    elif request.method == 'DELETE':
        # do the delete dance
        wish=wish.object.get(id=request.data.itemid)
        response = jsonify({"error": N})# 'DELETED'  # change this line
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
    

def timeI(entry):
    day = time.strftime("%a")
    date = time.strftime("%d")
    if (date <10):
        date = date.lstrip('0')
    month = time.strftime("%b")
    year = time.strftime("%Y")
    return day + ", " + date + " " + month + " " + year





