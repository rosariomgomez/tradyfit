# -*- coding: utf-8 -*-
from StringIO import StringIO
from mock import patch
from flask import current_app, url_for
from base import ClientTestCase
from app import db
from app.models import Item, Category
import app.main.views


class CreateItemIntegrationTestCase(ClientTestCase):

  def post_req_item_create(self, user, image=None):
    if image:
      image = (StringIO('contents'), image)

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = user.id
        sess['_fresh'] = True
      c = Category.get_category('soccer')
      return self.client.post(url_for('main.create'),
                              data={
                                  'name': 'soccer ball',
                                  'description': 'plain ball',
                                  'price': 234,
                                  'category': c.id,
                                  'image': image
                              }, follow_redirects=True)

  @patch('app.main.views.save_item_image', return_value='image.jpg')
  def test_create_item(self, mock):
    '''verify an item can be correctly created
    1. Go to the create an item's page
    2. Field in the form with a happy case
    3. Verify you are redirected to home page and the item is present
    '''
    u = self.create_user()
    resp = self.post_req_item_create(u, 'image.jpg')
    self.assertTrue('Your item has been created' in resp.data)
    self.assertTrue('234$' in resp.data)


  @patch('app.main.views.save_item_image', return_value=None)
  def test_create_item_image_problem(self, mock):
    '''verify an item will not be created if fails uploading the image
    1. Go to the create an item's page
    2. Field in the form with a happy case
    3. Simulate error uploading image to S3 (mock return None)
    4. Verify you are redirected to home page item was not created
    '''
    u = self.create_user()
    resp = self.post_req_item_create(u, 'image.jpg')
    self.assertTrue('Sorry, there was a problem creating your item.' in
                    resp.data)
    self.assertFalse('234$' in resp.data)


  def test_create_item_without_image(self):
    '''verify an item can be correctly created without an image
    1. Go to the create an item's page
    2. Field in the form without selecting an image
    3. Verify you are redirected to home page item and item was created
    with the default image
    '''
    u = self.create_user()
    resp = self.post_req_item_create(u)
    self.assertTrue(b'Your item has been created' in resp.data)
    self.assertTrue(current_app.config["DEFAULT_ITEM"] in resp.data)
