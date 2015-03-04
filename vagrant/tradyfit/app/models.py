# -*- coding: utf-8 -*-
from . import db, login_manager
from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import BaseQuery
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import make_searchable
from datetime import datetime
import os

make_searchable()


class User(UserMixin, db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  fb_id = db.Column(db.String(120), unique=True, nullable=False, index=True)
  email = db.Column(db.String(64), unique=True, nullable=False, index=True)
  username = db.Column(db.String(64), unique=True, nullable=False, index=True)
  name = db.Column(db.String(64), unique=False, nullable=False)
  avatar_url = db.Column(db.String(), unique=True)
  gender = db.Column(db.String(30))
  country = db.Column(db.String(100), default='')
  state =  db.Column(db.String(10), default='')
  city =  db.Column(db.String(60), default='')
  member_since = db.Column(db.DateTime(), default=datetime.utcnow)
  last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
  is_admin = db.Column(db.Boolean, default=False)
  items = db.relationship('Item', backref='user', lazy='dynamic',
                          cascade='all, delete-orphan')

  def ping(self):
    '''update last_seen field with current time'''
    self.last_seen = datetime.utcnow()
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


class ItemQuery(BaseQuery, SearchQueryMixin):
  pass


class Item(db.Model):
  query_class = ItemQuery
  __tablename__ = 'items'

  id    = db.Column(db.Integer, primary_key=True)
  name  = db.Column(db.String(80), nullable=False)
  description = db.Column(db.Text)
  price = db.Column(db.Numeric(precision=10, scale=2))
  timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
  modified = db.Column(db.DateTime, index=True)
  category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
  search_vector = db.Column(TSVectorType('name', 'description'))
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


