# -*- coding: utf-8 -*-
import unittest
from flask import url_for
from app import create_app, db
from app.models import Category, User, Item, Message


class BasicTestCase(unittest.TestCase):

  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()

  def tearDown(self):
    self.app_context.pop()


class UnitTestCase(BasicTestCase):

  def setUp(self):
    super(UnitTestCase, self).setUp()
    db.create_all()
    Category.insert_categories()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    #remove connection, if not, it stays idle. After running several tests
    #sqlalchemy is using all the connections and an Operational error occur
    db.get_engine(self.app).dispose()
    super(UnitTestCase, self).tearDown()

  def create_user_no_location(self, fb_id='23', email='john@example.com',
                              username='john'):
    u = User(fb_id=fb_id, email=email, name='John Doe', username=username,
            avatar_url='avatar.jpg', city='Mountain View')
    db.session.add(u)
    db.session.commit()
    return u

  def create_user(self, fb_id='4', email='lisa@example.com', username='lisa'):
    u = User(fb_id=fb_id, email=email, name='Lisa Simp', username=username,
            avatar_url='avatar.jpg', city='Madrid', state='NU',
            country='ES', latitude=40.479732, longitude=-3.5898299)
    db.session.add(u)
    db.session.commit()
    return u

  def create_user_location(self, fb_id='3', email='maggy@example.com',
        username='maggy', city='Berlin', state='NU', country='DE',
        latitude=52.5244, longitude=13.4105):
    u = User(fb_id=fb_id, email=email, name='Maggy Simp', username=username,
              avatar_url='avatar.jpg', city=city, state=state,
              country=country, latitude=latitude, longitude=longitude)
    db.session.add(u)
    db.session.commit()
    return u


  def create_item(self, user_id, item_name='ball', item_desc='small and round',
                  category='soccer'):
    c = Category.get_category(category)
    item = Item(name=item_name, description=item_desc, price=23,
                category_id=c.id, image_url='ball.jpg', user_id=user_id)
    db.session.add(item)
    db.session.commit()
    return item

  def create_item_location(self, user, item_name='bike', item_desc='fast',
    category='cycling'):
    c = Category.get_category(category)
    location = user.get_point_coordinates()
    item = Item(name=item_name, description=item_desc, price=23,
                category_id=c.id, image_url='ball.jpg', user_id=user.id,
                location=location, country=user.country, state=user.state,
                city=user.city)
    db.session.add(item)
    db.session.commit()
    return item

  def create_message(self, sender_id, receiver_id, item_id):
    msg = Message(subject='Hi there!', description='some text',
                  sender_id=sender_id, receiver_id=receiver_id, item_id=item_id)
    db.session.add(msg)
    db.session.commit()
    return msg


class ClientTestCase(UnitTestCase):

  def setUp(self):
    super(ClientTestCase, self).setUp()
    self.client = self.app.test_client()
    #do not request urls from S3
    self.app.config["S3_LOCATION"] = ''

  def make_get_request(self, user, url):
    '''make a get request with user in session'''
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = user.id
        sess['_fresh'] = True
      return c.get(url_for(url), follow_redirects=True)

  def make_get_localhost_request(self, url, headers):
    '''make a get request with localhost address to avoid API rate limit'''
    return self.client.get(url, headers=headers,
                            environ_base={'REMOTE_ADDR': '127.0.0.1'})
