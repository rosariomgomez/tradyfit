# -*- coding: utf-8 -*-
from flask import current_app, url_for
from base import ClientTestCase
from app import db
import app.main.views


class ProfileIntegrationTestCase(ClientTestCase):

  def post_req_profile(self, user):
    '''post request with form information'''
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = user.id
        sess['_fresh'] = True
      return self.client.post(url_for('main.profile'),
                              data={
                                  'username': user.username,
                                  'name': user.name,
                                  'country': 'ES',
                                  'state': 'NU',
                                  'city': 'Madrid'
                              }, follow_redirects=True)

  def test_update_profile(self):
    '''verify user information can be modified
    1. Go to the profile page
    2. Field in the form with a happy case
    3. Verify the new info is displayed
    '''
    u = self.create_user()
    resp = self.post_req_profile(u)
    self.assertTrue('Your profile has been updated' in resp.data)
    self.assertTrue('Madrid' in resp.data)


class DeleteUserIntegrationTestCase(ClientTestCase):

  def test_delete_account(self):
    '''verify a user can be deleted'''
    user = self.create_user()
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = user.id
        sess['_fresh'] = True
      resp = self.client.post(url_for('main.delete_account'),
                              follow_redirects=True)
    self.assertTrue('We are sorry to see you go...' in resp.data)
    self.assertTrue('Welcome to TradyFit' in resp.data)