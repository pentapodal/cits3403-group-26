from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

def create_application(config):
  app = Flask(__name__)
  app.config.from_object(config)
  db = SQLAlchemy(app)
  migrate = Migrate(app, db)
  login = LoginManager(app)
  login.login_view = 'login'
  return app

from app import routes, models
