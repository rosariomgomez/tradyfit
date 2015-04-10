# -*- coding: utf-8 -*-
import unittest
import re
from uuid import uuid4
from StringIO import StringIO
from mock import Mock, patch
from flask import current_app, url_for
from app import create_app, db
from app.models import Item, Category, User
import app.main.views


class CreateItemIntegrationTestCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()
    #do not request urls from S3
    self.app.config["S3_LOCATION"] = ''

    db.create_all()
    Category.insert_categories()
    self.client = self.app.test_client()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()


  @patch('app.main.views.save_item_image')
  def test_create_item(self, mock_save_item_image):
    '''verify an item can be correctly created
    1. Go to the create an item's page
    2. Field in the form with a happy case
    3. Verify you are redirected to home page and the item is present
    '''
    #create a user
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john', avatar_url=uuid4().hex + '.jpg')
    db.session.add(u)
    db.session.commit()

    mock_save_item_image.return_value = 'image.jpg'

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      c = Category.query.filter_by(name='soccer').one()
      resp = self.client.post(url_for('main.create'),
                              data={
                                  'name': 'soccer ball',
                                  'description': 'plain ball',
                                  'price': 234,
                                  'category': c.id,
                                  'image': (StringIO('contents'), 'image.jpg')
                              }, follow_redirects=True)
      self.assertTrue(b'Your item has been created' in resp.data)
      self.assertTrue(b'234$' in resp.data)


  @patch('app.main.views.save_item_image')
  def test_create_item_image_problem(self, mock_save_item_image):
    '''verify an item will not be created if fails uploading the image
    1. Go to the create an item's page
    2. Field in the form with a happy case
    3. Simulate error uploading image to S3 (mock return None)
    4. Verify you are redirected to home page item was not created
    '''
    #create a user
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john', avatar_url=uuid4().hex + '.jpg')
    db.session.add(u)
    db.session.commit()

    #simulate error on S3 uploading
    mock_save_item_image.return_value = None

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      c = Category.query.filter_by(name='soccer').one()
      resp = self.client.post(url_for('main.create'),
                              data={
                                  'name': 'soccer ball',
                                  'description': 'plain ball',
                                  'price': 234,
                                  'category': c.id,
                                  'image': (StringIO('contents'), 'image.jpg')
                              }, follow_redirects=True)
      self.assertTrue(b'Sorry, there was a problem creating your item.' in
                      resp.data)
      self.assertFalse(b'234$' in resp.data)


  def test_create_item_without_image(self):
    '''verify an item can be correctly created without an image
    1. Go to the create an item's page
    2. Field in the form without selecting an image
    3. Verify you are redirected to home page item and item was created
    with the default image
    '''
    #create a user
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john', avatar_url=uuid4().hex + '.jpg')
    db.session.add(u)
    db.session.commit()

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      c = Category.query.filter_by(name='soccer').one()
      resp = self.client.post(url_for('main.create'),
                              data={
                                  'name': 'soccer ball',
                                  'description': 'plain ball',
                                  'price': 234,
                                  'category': c.id
                              }, follow_redirects=True)
      self.assertTrue(b'Your item has been created' in resp.data)
      self.assertTrue(current_app.config["DEFAULT_ITEM"] in resp.data)
