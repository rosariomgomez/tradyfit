# -*- coding: utf-8 -*-
import unittest
import re
from uuid import uuid4
from bs4 import BeautifulSoup
from flask import current_app, url_for
from app import create_app, db
from app.models import Item, Category, User


class IndexFunctionalTestCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()
    Category.insert_categories()
    self.client = self.app.test_client()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def test_edit_link(self):
    '''verify an item can be edited from the index page by the owner
    1. Create two items by two different users
    2. Go to index page
    3. Assert the edit link is present for the user's item
    '''
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john', avatar_url=uuid4().hex + '.jpg')
    u1 = User(fb_id='25', email='maggy@example.com', name='Maggy Simpson',
              username='maggy', avatar_url=uuid4().hex + '.jpg')
    db.session.add_all([u,u1])
    db.session.commit()
    c = Category.query.filter_by(name='soccer').one()
    item = Item(name='soccer ball', description='plain ball',
        price=23, category=c, user_id=u.id)
    item2 = Item(name='soccer t-shirt', description='Real Madrid size M',
        price=28, category=c, user_id=u1.id)
    db.session.add_all([item,item2])
    db.session.commit()
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      response = self.client.get(url_for('main.index'))
      r = response.get_data(as_text=True)
      self.assertTrue('<a href="/edit/' + str(item.id) + '"' in r)
      self.assertFalse('<a href="/edit/' + str(item2.id) + '"' in r)

  def test_delete_item(self):
    '''verify an item can be deleted from the index page
    1. Create an item
    2. Go to index page
    3. Assert the delete link is present
    4. Delete the item
    5. Verfiy the item does not appear at the index page anymore
    '''
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john', avatar_url=uuid4().hex + '.jpg')
    u1 = User(fb_id='25', email='maggy@example.com', name='Maggy Simpson',
              username='maggy', avatar_url=uuid4().hex + '.jpg')
    db.session.add_all([u,u1])
    db.session.commit()
    c = Category.query.filter_by(name='soccer').one()
    item = Item(name='soccer ball', description='plain ball',
        price=23, category=c, user_id=u.id)
    item2 = Item(name='soccer t-shirt', description='Real Madrid size M',
        price=28, category=c, user_id=u1.id)
    db.session.add_all([item,item2])
    db.session.commit()
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      response = self.client.get(url_for('main.index'))
      r = response.get_data(as_text=True)
      self.assertTrue('<a href="/delete/' + str(item.id) + '"' in r)
      self.assertFalse('<a href="/delete/' + str(item2.id) + '"' in r)
      response = self.client.get(url_for('main.delete', id=str(item.id)),
                                follow_redirects=True)
      r = response.get_data(as_text=True)
      self.assertFalse(item.name in r)

