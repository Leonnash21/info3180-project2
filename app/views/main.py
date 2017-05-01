
###
# The functions below should be applicable to all Flask apps.
###


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
from flask import abort, render_template, request, redirect, url_for, flash, jsonify, session, g
from flask_login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import SQLAlchemy
from ..forms import LoginForm, SignupForm, WishForm, ShareForm
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

__all__ = ['home', 'about', 'form_view', 'send_text_file', 'add_header',
            'page_not_found']

forms = {
    # tuples of (FormObject, template_file) for forms sent to angular as templates
    'login': (LoginForm, 'login.html'), 'register': (SignupForm, 'add_profile.html'),
    'wishitem': (WishForm, 'addwish.html'),
    'share': (ShareForm, 'share.html')
}

templates = {
    'profile': 'view_profile.html', 
}

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

@app.route('/about/')
@login_required
def about():
    """Render the website's about page."""
    return render_template('about.html')


@app.route('/forms/<formname>.html', methods=['GET'])
def form_view(formname):
    try:
        formObject, template = forms[formname]
    except KeyError:
        abort(404)
    return render_template(template, form=formObject(formdata=None))


@app.route('/tmpl/<templatename>.html', methods=['GET'])
def tmpl_view(templatename):
    try:
        tmpl = templates[templatename]
    except KeyError:
        abort(404)
    return render_template(tmpl)


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


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
