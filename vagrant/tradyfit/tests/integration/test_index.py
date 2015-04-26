# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
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


  def test_search_no_query(self):
    '''verify you are redirected to home if no query on session cookie'''
    resp = self.client.get(url_for('main.search_results'),
                          follow_redirects=True)
    self.assertTrue('id="search-form"' in resp.data)


  def test_search_results_nologin(self):
    '''verify that search results are shown ordered by time creation if
    user is not logged in
    1. Create 3 items
    2. Make a search with a word in common from 2 of the 3 items
       (independent of uper/lower case)
    3. Check both items appears on the results in the correct order
       (ordered by timestamp)
    '''
    u = self.create_user()
    item = self.create_item(u.id, 'tri suit', 'black and blue')
    item1 = self.create_item(u.id, 'bicycle', 'tri scatante bike')
    item2 = self.create_item(u.id,'t-shirt','manchester club t-shirt')

    response = self.client.post(url_for('main.index'),
                              data={
                                  'search': 'tri'
                              }, follow_redirects=True)
    resp = response.get_data(as_text=True)
    self.assertTrue('Search results for "tri":' in resp)
    soup = BeautifulSoup(resp)
    items = soup.find_all("div", id=re.compile("^item-"))
    self.assertTrue(len(items) == 2)
    self.assertTrue("item-"+str(item1.id) in str(items[0]))


  def test_search_results_user_login_with_coordinates(self):
    '''verify that search results are shown ordered by user nearby
    if the request is made with an authenticated user with location
    1. Create 2 items with the word "bicycle" in common:
       one form a Madrid user, other from Berlin
    2. Make a search with the word "bicycle" with a user from Barcelona
    3. Check the 2 items appears on the results in the correct order
       (ordered by nearby: Madrid, Berlin)
    '''
    user_madrid = self.create_user()
    item_madrid = self.create_item_location(user_madrid, 'fast and furious',
                                  'break records with this bicycle')
    user_berlin = self.create_user_location()
    item_berlin = self.create_item_location(user_berlin, 'triathlon bicycle',
                                   'specially designed to win')
    user_barcelona = self.create_user_location('2', 'bart@example.com',
                      'bart', 'Barcelona', 'NU', 'ES', 41.387128, 2.16856499)

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = user_barcelona.id
        sess['_fresh'] = True

      response = self.client.post(url_for('main.index'),
                              data={
                                  'search': 'bicycle'
                              }, follow_redirects=True)
      soup = BeautifulSoup(response.get_data(as_text=True))
      items = soup.find_all("div", id=re.compile("^item-"))
      self.assertTrue(user_barcelona.city in response.data) #user's city name
      self.assertTrue(len(items) == 2)
      self.assertTrue("item-"+str(item_madrid.id) in str(items[0]))
      self.assertTrue("item-"+str(item_berlin.id) in str(items[1]))


  def test_search_sqlinjection(self):
    '''make sure the search is not vulnerable to an SQL injection'''

    response = self.client.post(url_for('main.index'),
                            data={
                                'search': "foo UNION SELECT id FROM categories"
                            }, follow_redirects=True)
    soup = BeautifulSoup(response.get_data(as_text=True))
    items = soup.find_all("div", id=re.compile("^item-"))
    self.assertTrue(not items)

