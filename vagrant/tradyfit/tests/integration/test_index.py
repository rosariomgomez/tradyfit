# -*- coding: utf-8 -*-
from mock import patch
from flask import url_for
from base import ClientTestCase
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
    u = self.create_user()
    u1 = self.create_user('25', 'maggy@example.com', 'maggy')
    item = self.create_item(u.id)
    item2 = self.create_item(u1.id, 't-shirt', 'blue small size')

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
      self.assertFalse(item.description in r)
