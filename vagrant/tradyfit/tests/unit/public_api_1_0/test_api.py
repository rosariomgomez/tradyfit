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
    '''testing @public_api.route('/items/category/<category>')
    request items for a non existent category.
    Verify you get a 404
    '''
    response = self.client.get('public-api/v1.0/items/category/notacategory', 
                headers=self.get_api_headers())
    self.assertTrue(response.status_code == 404)


  def test_get_items_valid_category(self):
    '''testing @public_api.route('/items/category/<category>')
    1. Create 2 items. One from soccer and other from cycling category
    2. Request items from soccer category
    3. Verify only the item from soccer was returned'''

    user = self.create_user_location()
    item1 = self.create_item(user.id)
    item2 = self.create_item(user.id, 'bike', 'blue and red', 'cycling')
    response = self.client.get('public-api/v1.0/items/category/cycling', 
                headers=self.get_api_headers())
    self.assertTrue(response.status_code == 200)
    json_response = json.loads(response.data.decode('utf-8'))
    self.assertTrue(len(json_response['items']) == 1)
    self.assertTrue(json_response['items'][0]['name'] == item2.name)


  def test_get_items_invalid_search(self):
    '''testing @public_api.route('/items/search/<search>')
    Verify you get a 400 responses when query is not valid'''
    #1. request with query < MIN_QUERY
    response = self.client.get('public-api/v1.0/items/search/fo', 
                headers=self.get_api_headers())
    self.assertTrue(response.status_code == 400)

    #2. request with query starting with "-"
    response = self.client.get('public-api/v1.0/items/search/-something', 
                headers=self.get_api_headers())
    self.assertTrue(response.status_code == 400)

    #3. request with query containing special chars
    response = self.client.get('public-api/v1.0/items/search/<script>hi', 
                headers=self.get_api_headers())
    self.assertTrue(response.status_code == 400)


  def test_get_items_valid_search(self):
    '''testing @public_api.route('/items/search/<search>')
    1. Create 3 items. Two of them containing the words "blue bike"
    2. Request items with the query="blue bike"
    3. Verify the two items were returned ordered by desc timestamp'''

    user = self.create_user_location()
    item1 = self.create_item(user.id)
    item2 = self.create_item(user.id, 'bike', 'blue and red', 'cycling')
    item3 = self.create_item(user.id, 'tri bike', 'blue print', 'cycling')
    response = self.client.get('public-api/v1.0/items/search/blue bike', 
                headers=self.get_api_headers())
    self.assertTrue(response.status_code == 200)
    json_response = json.loads(response.data.decode('utf-8'))
    self.assertTrue(len(json_response['items']) == 2)
    self.assertTrue(json_response['items'][0]['name'] == item3.name)


