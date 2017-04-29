
import os
import math
import flask
import base64
import random
import smtplib
import json
import bcrypt
import urlparse


from .. import app, db, login_manager
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g
from flask_login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import SQLAlchemy
from ..models import UserT, Wish, Token
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



# ability to share/send wishlist
@app.route('/api/users/{userid}', methods=["POST"])
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

