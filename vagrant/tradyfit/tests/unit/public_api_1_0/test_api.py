# -*- coding: utf-8 -*-
import json
from flask import url_for
from base import ClientTestCase


class APITestCase(ClientTestCase):
  
  def get_api_headers(self):
    return {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }

  def test_404(self):
    response = self.client.get('/bad/url', headers=self.get_api_headers())
    self.assertTrue(response.status_code == 404)
    json_response = json.loads(response.data.decode('utf-8'))
    self.assertTrue(json_response['error'] == 'not found')

  def test_get_items_invalid_category(self):
    '''request items for a non existent category.
    Verify you get a 404
    '''
    response = self.client.get('public-api/v1.0/items/notacategory', 
                headers=self.get_api_headers())
    self.assertTrue(response.status_code == 404)


  def test_get_items_valid_category(self):
    '''testing @public_api.route('/items/<category>')
    1. Create 2 items. One from soccer and other from cycling category
    2. Request items from soccer category
    3. Verify only the item from soccer was returned'''

    user = self.create_user_location()
    item1 = self.create_item(user.id)
    item2 = self.create_item(user.id, 'bike', 'blue and red', 'cycling')
    response = self.client.get('public-api/v1.0/items/cycling', 
                headers=self.get_api_headers())
    self.assertTrue(response.status_code == 200)
    json_response = json.loads(response.data.decode('utf-8'))
    self.assertTrue(len(json_response['items']) == 1)
    self.assertTrue(json_response['items'][0]['name'] == item2.name)


