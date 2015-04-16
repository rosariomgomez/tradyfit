# -*- coding: utf-8 -*-
from flask import url_for
from base import ClientTestCase
import app.msg.views


class CreateViewTestCase(ClientTestCase):
  '''Testing: @msg.route('msg/create/<int:id>', methods=['GET', 'POST'])'''

  def test_create_message_route(self):
    '''verify you can go to create message page if an existent item is passed
    or you get a 404 for a non existent item
    1. Try to create a message for a non existent item
    2. Assert you get a 404 response
    3. Try to create a message of an existent item
    4. Assert you get the correct create page
    '''
    u = self.create_user()
    u1 = self.create_user('25', 'maggy@example.com', 'maggy')
    item = self.create_item(u.id)

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u1.id
        sess['_fresh'] = True

      #1. non existent item
      response = self.client.get(url_for('msg.create', id=12))
      self.assertEquals(response.status_code, 404)

      #2. create message page
      response = self.client.get(url_for('msg.create', id=item.id))
      self.assertEquals(response.status_code, 200)


class NotificationsViewTestCase(ClientTestCase):
  '''Testing: @msg.route('/notifications')'''

  def test_notifiactions_route(self):
    '''verify you can go to notifications page'''
    user = self.create_user()
    response = self.make_get_request(user, 'msg.notifications')
    self.assertEquals(response.status_code, 200)
    self.assertTrue('msgs-unread' in response.data)