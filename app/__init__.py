from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'login'  

def create_application(config):
  app = Flask(__name__)
  app.config.from_object(config)

  from app.blueprints import blueprint
  app.register_blueprint(blueprint)

  db.init_app(app)
  login.init_app(app)

  return app

from app import routes, models
