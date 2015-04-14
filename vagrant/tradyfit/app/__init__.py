from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.moment import Moment
from config import config
import geonamescache
from geopy.geocoders import GoogleV3


bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
gc = geonamescache.GeonamesCache()
geolocator = GoogleV3()

login_manager = LoginManager()
login_manager.login_view = 'main.index'

def create_app(config_name):
  app = Flask(__name__)
  app.config.from_object(config[config_name])
  config[config_name].init_app(app)

  bootstrap.init_app(app)
  moment.init_app(app)
  db.init_app(app)
  login_manager.init_app(app)

  from .main import main as main_blueprint
  app.register_blueprint(main_blueprint)

  from .auth import auth as auth_blueprint
  app.register_blueprint(auth_blueprint)

  return app
