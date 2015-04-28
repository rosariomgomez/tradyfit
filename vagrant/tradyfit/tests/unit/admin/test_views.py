# -*- coding: utf-8 -*-
from flask import url_for
from base import ClientTestCase
import app.admin.views


class IndexViewTestCase(ClientTestCase):
  '''Testing: @admin.route('/')'''

  def test_index_no_admin_user(self):
    '''verify you are redirected to home if user is not and admin user'''
    #not logged in
    response = self.client.get(url_for('admin.index'), follow_redirects=True)
    r = response.get_data(as_text=True)
    self.assertTrue('id="search-form"' in r)

    #logged in not admin
    user = self.create_user()
    response = self.make_get_request(user, 'admin.index')
    r = response.get_data(as_text=True)
    self.assertTrue('id="search-form"' in r)


  def test_index_admin_user(self):
    '''verify you can see the admin panel if you are an admin user
    and users are displayed'''
    user = self.create_user()
    user.is_admin = True
    response = self.make_get_request(user, 'admin.index')
    r = response.get_data(as_text=True)
    self.assertTrue('Admin Panel' in r)
    self.assertTrue('id="users"' in r)


class ItemsViewTestCase(ClientTestCase):
  '''Testing: @admin.route('/items')'''

  def test_items_no_admin_user(self):
    '''verify you are redirected to home if user is not and admin user'''
    #not logged in
    response = self.client.get(url_for('admin.items'), follow_redirects=True)
    r = response.get_data(as_text=True)
    self.assertTrue('id="search-form"' in r)

    #logged in not admin
    user = self.create_user()
    response = self.make_get_request(user, 'admin.items')
    r = response.get_data(as_text=True)
    self.assertTrue('id="search-form"' in r)


  def test_items_admin_user(self):
    '''verify you can see the admin panel if you are an admin user
    and items are displayed'''
    user = self.create_user()
    user.is_admin = True
    response = self.make_get_request(user, 'admin.items')
    r = response.get_data(as_text=True)
    self.assertTrue('Admin Panel - Items' in r)
    self.assertTrue('id="items"' in r)



