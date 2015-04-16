# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from flask import url_for
from base import ClientTestCase
import app.msg.views


class MessageIntegrationTestCase(ClientTestCase):

  def test_create_message(self):
    '''verify a message is sent when the form is correctly field.
    User is redirected to item page'''

    u = self.create_user()
    u1 = self.create_user('25', 'maggy@example.com', 'maggy')
    item = self.create_item(u.id)

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u1.id
        sess['_fresh'] = True

      response = self.client.post(url_for('msg.create', id=item.id),
                                  data={
                                    'subject': 'Hi there!',
                                    'description': 'Some description here',
                                  }, follow_redirects=True)
      self.assertTrue('Your message has been sent.' in response.data)
      self.assertTrue(item.name.capitalize() in response.data)

  def test_notifications(self):
    '''verify you can see an unread message in the notifications when a
    message is sent to you'''
    u = self.create_user()
    u1 = self.create_user('25', 'maggy@example.com', 'maggy')
    item = self.create_item(u.id)
    msg = self.create_message(u1.id, u.id, item.id)

    response = self.make_get_request(u, 'msg.notifications')
    #assert message is present and it appears under unread messages category
    self.assertTrue(msg.subject in response.data)
    soup = BeautifulSoup(response.get_data(as_text=True))
    ul_unread_messages = soup.find("ul", id="msgs-unread")
    unread_messages = ul_unread_messages.find_all("li", id=re.compile("^msg-"))
    self.assertTrue("msg-"+str(msg.id) in str(unread_messages[0]))

  def test_reply_message(self):
    '''verify you can reply a message'''
    u = self.create_user()
    u1 = self.create_user('25', 'maggy@example.com', 'maggy')
    item = self.create_item(u.id)
    msg = self.create_message(u1.id, u.id, item.id)

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True

      response = self.client.post(url_for('msg.message', id=msg.id),
                                  data={
                                    'subject': 'Answer to message',
                                    'description': 'Some description here',
                                  }, follow_redirects=True)
      self.assertTrue('Your message has been sent.' in response.data)

