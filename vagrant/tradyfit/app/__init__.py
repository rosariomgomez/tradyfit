from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask_jsglue import JSGlue
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.moment import Moment
from flask_limiter import Limiter
from flask.ext.mobility import Mobility
from config import config
import geonamescache
from geopy.geocoders import GoogleV3


bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
gc = geonamescache.GeonamesCache()
geolocator = GoogleV3()
jsglue = JSGlue()
limiter = Limiter()

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
  jsglue.init_app(app)
  limiter.init_app(app)
  Mobility(app)

  from .admin import admin as admin_blueprint
  app.register_blueprint(admin_blueprint, url_prefix='/admin')

  from .main import main as main_blueprint
  app.register_blueprint(main_blueprint)

  from .auth import auth as auth_blueprint
  app.register_blueprint(auth_blueprint)

  from .msg import msg as msg_blueprint
  app.register_blueprint(msg_blueprint)

  from .public_api_1_0 import public_api as public_api_1_0_blueprint
  app.register_blueprint(public_api_1_0_blueprint,
                        url_prefix='/public-api/v1.0')

  return app
