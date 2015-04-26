# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from flask import url_for
from base import ClientTestCase
from app.models import Category
import app.main.views


class CategoriesIntegrationTestCase(ClientTestCase):

  def test_categories_nologin(self):
    '''verify that items are shown ordered by time creation if
    user is not logged in
    1. Create 2 items
    2. Go to categories page
    3. Check the items appears on the results in the correct order
       (ordered by timestamp)
    '''
    u = self.create_user()
    item = self.create_item(u.id, 'tri suit', 'black and blue')
    item1 = self.create_item(u.id, 'bicycle', 'tri scatante bike')

    response = self.client.get(url_for('main.categories'))
    resp = response.get_data(as_text=True)
    soup = BeautifulSoup(resp)
    items = soup.find_all("div", id=re.compile("^item-"))
    self.assertTrue(len(items) == 2)
    self.assertTrue("item-"+str(item1.id) in str(items[0]))


  def test_categories_user_login_with_coordinates(self):
    '''verify that items are shown ordered by user nearby
    if the request is made with an authenticated user with location
    1. Create 2 items one form a Madrid user, other from Berlin
    2. Go to categories page with a user from Barcelona
    3. Check the 2 items appears on the results in the correct order
       (ordered by nearby: Madrid, Berlin)
    '''
    user_madrid = self.create_user()
    item_madrid = self.create_item_location(user_madrid, 'madrid bike',
                                  'break records with this bicycle')
    user_berlin = self.create_user_location()
    item_berlin = self.create_item_location(user_berlin, 'berlin bike',
                                   'specially designed to win')
    user_barcelona = self.create_user_location('2', 'bart@example.com',
                      'bart', 'Barcelona', 'NU', 'ES', 41.387128, 2.16856499)

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = user_barcelona.id
        sess['_fresh'] = True

      response = self.client.get(url_for('main.categories'))
      resp = response.get_data(as_text=True)
      soup = BeautifulSoup(resp)
      items = soup.find_all("div", id=re.compile("^item-"))
      self.assertTrue(len(items) == 2)
      self.assertTrue("item-"+str(item_madrid.id) in str(items[0]))
      self.assertTrue("item-"+str(item_berlin.id) in str(items[1]))



class CategoryIntegrationTestCase(ClientTestCase):

  def test_category_nologin(self):
    '''verify that items from the requested category are shown ordered
    by time creation if user is not logged in
    1. Create 3 items, 2 of the same category (soccer)
    2. Go to the soccer's category page
    3. Check the items appears on the results in the correct order
       (ordered by timestamp)
    '''
    u = self.create_user()
    category = Category.get_category('soccer')
    item = self.create_item(u.id)
    item1 = self.create_item(u.id, 'bicycle', 'tri scatante bike', 'cycling')
    item2 = self.create_item(u.id, 't-shirt', 'big', 'soccer')

    response = self.client.get(url_for('main.category', id=category.id))
    resp = response.get_data(as_text=True)
    soup = BeautifulSoup(resp)
    items = soup.find_all("div", id=re.compile("^item-"))
    self.assertTrue(len(items) == 2)
    self.assertTrue("item-"+str(item2.id) in str(items[0]))


  def test_category_user_login_with_coordinates(self):
    '''verify that items from the requested category are shown ordered
    by user nearby if the request is made with an authenticated user
    with location
    1. Create 3 items. Two from soccer category, one form a Madrid user,
    other from Berlin
    2. Go to soccer's category page with a user from Barcelona
    3. Check the 2 items appears on the results in the correct order
       (ordered by nearby: Madrid, Berlin)
    '''
    user_madrid = self.create_user()
    item_madrid = self.create_item_location(
                                    user_madrid, 't-shirt', 'big', 'soccer')
    item_madrid1 = self.create_item_location(
                                    user_madrid, 'bike', 'fast', 'cycling')
    user_berlin = self.create_user_location()
    item_berlin = self.create_item_location(user_berlin)
    user_barcelona = self.create_user_location('2', 'bart@example.com',
                      'bart', 'Barcelona', 'NU', 'ES', 41.387128, 2.16856499)
    category = Category.get_category('cycling')

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = user_barcelona.id
        sess['_fresh'] = True

      response = self.client.get(url_for('main.category', id=category.id))
      soup = BeautifulSoup(response.get_data(as_text=True))
      items = soup.find_all("div", id=re.compile("^item-"))
      self.assertTrue(user_barcelona.city in response.data) #user's city name
      self.assertTrue(len(items) == 2)
      self.assertTrue("item-"+str(item_madrid1.id) in str(items[0]))
      self.assertTrue("item-"+str(item_berlin.id) in str(items[1]))


