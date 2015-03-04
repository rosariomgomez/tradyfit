# -*- coding: utf-8 -*-
import unittest
import time
from app import create_app, db
from app.models import Category, Item, User, load_user


class ModelTestCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()


class CategoryModelTestCase(ModelTestCase):
  def test_insert_categories(self):
    categories = Category.query.all()
    self.assertEqual(categories, [])
    Category.insert_categories()
    c = Category.query.filter_by(name='soccer').one()
    self.assertEqual(c.name, 'soccer')

  def test_insert_categories_no_dup(self):
    '''make sure that if a category is already in db, it is not
    added again'''
    c = Category(name='soccer')
    db.session.add(c)
    db.session.commit()
    Category.insert_categories()
    self.assertEqual(Category.query.filter_by(name='soccer').count(), 1)


class UserModelTestCase(ModelTestCase):
  def test_username(self):
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john')
    db.session.add(u)
    db.session.commit()
    #the username already exists, append the next uid to the name
    self.assertTrue(User.create_username('john') == 'john2')
    #username doesn't exist, so it can be assigned
    self.assertTrue(User.create_username('jacky') == 'jacky')

  def test_ping(self):
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john')
    db.session.add(u)
    db.session.commit()
    time.sleep(2)
    last_seen_before = u.last_seen
    u.ping()
    self.assertTrue(u.last_seen > last_seen_before)

  def test_get_user(self):
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john')
    db.session.add(u)
    db.session.commit()
    self.assertEqual(User.get_user('john@example.com'), u)
    self.assertEqual(User.get_user('nobody@example.com'), None)

  def test_load_user(self):
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john')
    db.session.add(u)
    db.session.commit()
    self.assertEqual(load_user(u.id), u)
