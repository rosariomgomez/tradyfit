# -*- coding: utf-8 -*-
from uuid import uuid4
from StringIO import StringIO
from mock import patch
from flask import current_app, url_for
from base import ClientTestCase
from app import db
from app.models import Item, Category, User
import app.main.views


class CreateItemIntegrationTestCase(ClientTestCase):

  @patch('app.main.views.save_item_image', return_value='image.jpg')
  def test_create_item(self, mock):
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


  @patch('app.main.views.save_item_image', return_value=None)
  def test_create_item_image_problem(self, mock):
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
