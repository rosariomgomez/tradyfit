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


class MessageViewTestCase(ClientTestCase):
  '''Testing: @msg.route('/msg/<int:id>')'''

  def test_message_route_valid_user(self):
    '''verify if you are the sender or receiver you can see the message'''
    u = self.create_user()
    u1 = self.create_user('25', 'maggy@example.com', 'maggy')
    item = self.create_item(u.id)
    msg = self.create_message(u.id, u1.id, item.id)

    #login with user1
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u1.id
        sess['_fresh'] = True

      #1. received message
      response = self.client.get(url_for('msg.message', id=msg.id))
      self.assertEquals(response.status_code, 200)
      self.assertTrue("msg-"+str(msg.id) in response.data)


  def test_message_route_invalid_user(self):
    '''verify that you will be redirected to main if you are not the
    sender/receiver or show a 404 if the message doesn't exist'''
    u = self.create_user()
    u1 = self.create_user('25', 'maggy@example.com', 'maggy')
    u2 = self.create_user('29', 'bart@example.com', 'bart')
    item = self.create_item(u.id)
    msg = self.create_message(u.id, u1.id, item.id)

    #login with user 2
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u2.id
        sess['_fresh'] = True

      #1. non existent message
      response = self.client.get(url_for('msg.message', id=12))
      self.assertEquals(response.status_code, 404)

      #2. not a user's message
      response = self.client.get(url_for('msg.message', id=msg.id))
      self.assertEquals(response.status_code, 302)
      self.assertFalse("msg-"+str(msg.id) in response.data)
