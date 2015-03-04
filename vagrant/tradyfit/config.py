# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'our so secret password'
  SQLALCHEMY_COMMIT_ON_TEARDOWN = True
  TRADYFIT_ADMIN = os.environ.get('TRADYFIT_ADMIN')

  FACEBOOK = {
    'consumer_key': os.environ.get('FB_CKEY'),
    'consumer_secret': os.environ.get('FB_CSECRET'),
    'request_token_params': {'scope': 'email'},
    'base_url': 'https://graph.facebook.com',
    'request_token_url': None,
    'access_token_url': '/oauth/access_token',
    'authorize_url': 'https://www.facebook.com/dialog/oauth'
  }

  @staticmethod
  def init_app(app):
      pass


class DevelopmentConfig(Config):
  DEBUG = True
  SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
      'postgresql:///tradyfit_dev'


class TestingConfig(Config):
  TESTING = True #@login_required is disabled on tests
  SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
      'postgresql:///tradyfit_test'
  WTF_CSRF_ENABLED = False #disable csrf token protection on forms


class ProductionConfig(Config):
  pass

config = {
  'development': DevelopmentConfig,
  'testing': TestingConfig,
  'production': ProductionConfig,

  'default': DevelopmentConfig
}
