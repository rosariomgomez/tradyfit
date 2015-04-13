# -*- coding: utf-8 -*-
from uuid import uuid4
from mock import patch
from flask import current_app, url_for
from base import ClientTestCase
from app import db
from app.models import Item, Category, User
import app.main.views


class IndexIntegrationTestCase(ClientTestCase):

  def test_search_form_redirect(self):
    '''verify the search form redirects to results when submit'''
    resp = self.client.post(url_for('main.index'),
                            data={
                                'search': 'soccer ball',
                            }, follow_redirects=True)
    self.assertTrue(b'Search results for "soccer ball":' in resp.data)

  @patch('app.main.views.delete_item_image', return_value=True)
  def test_delete_item(self, mock_delete_image):
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
        price=23, category=c, user_id=u.id,
        image_url=self.app.config["DEFAULT_ITEM"])
    item2 = Item(name='soccer t-shirt', description='Real Madrid size M',
        price=28, category=c, user_id=u1.id, image_url='item2.jpg')
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
