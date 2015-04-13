# -*- coding: utf-8 -*-
import os
from . import db, login_manager
from flask import current_app
from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import BaseQuery
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import make_searchable
from datetime import datetime
from app.geolocation import Geolocation

make_searchable()


def get_image(folder, url):
  '''get public url for S3 images'''
  return current_app.config['S3_LOCATION'] + "/" + \
    current_app.config['S3_BUCKET'] + \
    current_app.config[folder] + "/" + url


class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  fb_id = db.Column(db.String(120), unique=True, nullable=False, index=True)
  email = db.Column(db.String(64), unique=True, nullable=False, index=True)
  username = db.Column(db.String(64), unique=True, nullable=False, index=True)
  name = db.Column(db.String(64), unique=False, nullable=False)
  avatar_url = db.Column(db.String(), nullable=False)
  gender = db.Column(db.String(30))
  country = db.Column(db.String(100), default='')
  state =  db.Column(db.String(10), default='')
  city =  db.Column(db.String(60), default='')
  latitude = db.Column(db.Numeric(precision=10, scale=6))
  longitude = db.Column(db.Numeric(precision=10, scale=6))
  member_since = db.Column(db.DateTime(), default=datetime.utcnow)
  last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
  is_admin = db.Column(db.Boolean, default=False)
  items = db.relationship('Item', backref='user', lazy='dynamic',
                          cascade='all, delete-orphan')


  def ping(self):
    '''update last_seen field with current time'''
    self.last_seen = datetime.utcnow()
    db.session.add(self)


  def location(self, ip):
    '''update user location if not yet stored'''
    if not self.city:
      user_geo = Geolocation(ip)
      if user_geo.location:
        r, country = user_geo.get_country()
        if not (r and country): #do not continue if the country is not present
          return
        self.country = country
        r, state = user_geo.get_state()
        if r and state:
          self.state = state
        r, city = user_geo.get_city()
        if r and city:
          self.city = city
        r, latitude = user_geo.get_latitude()
        if r and latitude:
          self.latitude = latitude
        r, longitude = user_geo.get_longitude()
        if r and longitude:
          self.longitude = longitude

        db.session.add(self)


  @staticmethod
  def get_user(email):
    return User.query.filter_by(email = email).first()

  @staticmethod
  def create_username(username):
    '''verify username is not already in the db, if it exists,
    add the next uid number to the name'''
    if User.query.filter_by(username = username).first():
      uid = User.query.count() + 1
      return username + str(uid)
    else:
      return username

  def avatar(self):
    return get_image('S3_UPLOAD_AVATAR_DIR', self.avatar_url)


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


class Category(db.Model):
  __tablename__ = 'categories'
  id    = db.Column(db.Integer, primary_key=True)
  name  = db.Column(db.String, unique=True, index=True)
  items = db.relationship('Item', backref='category')

  @staticmethod
  def insert_categories():
    path = os.path.dirname(os.path.abspath(__file__))
    f = os.path.join(path,"files/categories.txt")
    with open(f, "r") as categories:
      for category in categories: #read each line
        category = category.rstrip('\n')
        c = Category.query.filter_by(name=category).first()
        if c is None: #not in db yet
          category = Category(name=category)
          db.session.add(category)
    db.session.commit()

  @staticmethod
  def get_category_choices():
    '''return a list with tuples (category_code, name) with
    all categories for populate ItemForm category choices'''
    categories = Category.query.all()
    return [(c.id, c.name) for c in categories]

  @staticmethod
  def get_category(name):
    return Category.query.filter_by(name=name).one()


class ItemQuery(BaseQuery, SearchQueryMixin):
  pass


class Item(db.Model):
  query_class = ItemQuery
  __tablename__ = 'items'

  id    = db.Column(db.Integer, primary_key=True)
  name  = db.Column(db.String(80), nullable=False)
  description = db.Column(db.Text)
  price = db.Column(db.Numeric(precision=10, scale=2))
  image_url = db.Column(db.String())
  timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
  modified = db.Column(db.DateTime, index=True)
  category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
  search_vector = db.Column(TSVectorType('name', 'description'))
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

  def image(self):
    return get_image('S3_UPLOAD_ITEM_DIR', self.image_url)

