# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'our so secret password'
  SQLALCHEMY_COMMIT_ON_TEARDOWN = True
  TRADYFIT_ADMIN = os.environ.get('TRADYFIT_ADMIN')
  RATELIMIT_STRATEGY = 'fixed-window-elastic-expiry'

  FACEBOOK = {
    'consumer_key': os.environ.get('FB_CKEY'),
    'consumer_secret': os.environ.get('FB_CSECRET'),
    'request_token_params': {'scope': 'email'},
    'base_url': 'https://graph.facebook.com',
    'request_token_url': None,
    'access_token_url': '/oauth/access_token',
    'access_token_method': 'GET',
    'authorize_url': 'https://www.facebook.com/dialog/oauth'
  }

  #AWS S3 credentials
  S3_LOCATION = 'https://s3.amazonaws.com'
  S3_KEY = os.environ.get('S3_KEY')
  S3_SECRET = os.environ.get('S3_SECRET')
  S3_UPLOAD_AVATAR_DIR = '/user_avatars'
  S3_UPLOAD_ITEM_DIR = '/items'

  DEFAULT_ITEM = 'default_item.jpg'
  DEFAULT_AVATAR = 'default_avatar.jpg'

  #MAX IMAGE SIZE ALLOWED 3MB
  MAX_CONTENT_LENGTH = 3 * 1024 * 1024


  @staticmethod
  def init_app(app):
      pass


class DevelopmentConfig(Config):
  DEBUG = True
  SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
      'postgresql:///tradyfit_dev'
  S3_BUCKET = 'tradyfitbucket.dev'


class TestingConfig(Config):
  TESTING = True #@login_required is disabled on tests
  SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
      'postgresql:///tradyfit_test'
  WTF_CSRF_ENABLED = False #disable csrf token protection on forms

  #AWS S3
  S3_BUCKET = 'tradyfitbucket.test'

  #FB Test user credentials
  FB_TEST_ID = '100009532443743'
  FB_TEST_EMAIL = os.environ.get('FB_TEST_EMAIL')
  FB_TEST_PWD = os.environ.get('FB_TEST_PWD'),


class ProductionConfig(Config):
  #S3_BUCKET = 'tradyfitbucket'
  pass

config = {
  'development': DevelopmentConfig,
  'testing': TestingConfig,
  'production': ProductionConfig,

  'default': DevelopmentConfig
}
