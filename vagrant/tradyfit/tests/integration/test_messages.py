# -*- coding: utf-8 -*-
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