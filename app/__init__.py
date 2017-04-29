from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
# from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = "DzdIjmqHaPQfGSFgEQ9Uxw2a3e5KgviiNrQ639aWHv"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://proj2:password123@localhost/proj2"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # added just to suppress a warning
app.config['DEFAULT_ADMIN'] = 'Admin <admin@example.com>'


# CSRFProtect(app)
db = SQLAlchemy(app)

# Flask-Login login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = None

app.config.from_object(__name__)
from app import views

