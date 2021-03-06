# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'our so secret password'
  RATELIMIT_STRATEGY = 'fixed-window-elastic-expiry'

  OPBEAT = {
    'ORGANIZATION_ID': os.environ.get('OPBEAT_ORG_ID'),
    'APP_ID': os.environ.get('OPBEAT_APP_ID'),
    'SECRET_TOKEN': os.environ.get('OPBEAT_SECRET')
  }

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

  #Disable OPBEAT logger
  OPBEAT = {'APP_ID': None}


class TestingConfig(Config):
  TESTING = True #@login_required is disabled on tests
  SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
      'postgresql:///tradyfit_test'
  WTF_CSRF_ENABLED = False #disable csrf token protection on forms

  #Disable OPBEAT logger
  OPBEAT = {'APP_ID': None}

  #AWS S3
  S3_BUCKET = 'tradyfitbucket.test'

  #FB Test users credentials
  FB_TEST_ID = os.environ.get('FB_TEST_ID')
  FB_TEST_EMAIL = os.environ.get('FB_TEST_EMAIL')
  FB_TEST_PWD = os.environ.get('FB_TEST_PWD')

  FB_TEST_ID1 = os.environ.get('FB_TEST_ID1')
  FB_TEST_EMAIL1 = os.environ.get('FB_TEST_EMAIL1')
  FB_TEST_PWD1 = os.environ.get('FB_TEST_PWD1')


class HerokuConfig(Config):
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
  S3_BUCKET = 'tradyfitbucket'
  S3_KEY = os.environ.get('S3_KEY_PROD')
  S3_SECRET = os.environ.get('S3_SECRET_PROD')



config = {
  'development': DevelopmentConfig,
  'testing': TestingConfig,
  'heroku': HerokuConfig,

  'default': DevelopmentConfig
}
