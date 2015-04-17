# -*- coding: utf-8 -*-
from flask import url_for
from app import db
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
    #assert message is present
    self.assertTrue(msg.subject in response.data)


  def test_reply_message_success(self):
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


  def test_reply_message_same_user(self):
    '''verify you cannot reply a message to yourself'''
    receiver = self.create_user()
    sender = self.create_user('25', 'maggy@example.com', 'maggy')
    item = self.create_item(receiver.id)
    msg = self.create_message(sender.id, receiver.id, item.id)

    #sender try to reply the message to herself
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = sender.id
        sess['_fresh'] = True

      response = self.client.post(url_for('msg.message', id=msg.id),
                                  data={
                                    'subject': 'Answer to message',
                                    'description': 'Some description here',
                                  }, follow_redirects=True)
      self.assertFalse('Your message has been sent.' in response.data)


  def test_reply_message_delete_item(self):
    '''verify a message is not created if item is deleted'''
    receiver = self.create_user()
    sender = self.create_user('25', 'maggy@example.com', 'maggy')
    item = self.create_item(receiver.id)
    msg = self.create_message(sender.id, receiver.id, item.id)
    db.session.delete(item)
    db.session.commit()

    #receiver try to reply the message
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = receiver.id
        sess['_fresh'] = True

      response = self.client.post(url_for('msg.message', id=msg.id),
                                  data={
                                    'subject': 'Answer to message',
                                    'description': 'Some description here',
                                  }, follow_redirects=True)
      self.assertFalse('Your message has been sent.' in response.data)


  def test_reply_message_delete_sender(self):
    '''verify a message is not created if sender is deleted'''
    receiver = self.create_user()
    sender = self.create_user('25', 'maggy@example.com', 'maggy')
    item = self.create_item(receiver.id)
    msg = self.create_message(sender.id, receiver.id, item.id)
    db.session.delete(sender)
    db.session.commit()

    #receiver try to reply the message
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = receiver.id
        sess['_fresh'] = True

      response = self.client.post(url_for('msg.message', id=msg.id),
                                  data={
                                    'subject': 'Answer to message',
                                    'description': 'Some description here',
                                  }, follow_redirects=True)
      self.assertFalse('Your message has been sent.' in response.data)

