# -*- coding: utf-8 -*-
import unittest
from app import create_app, db
from app.models import Category, User, Item


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
    super(UnitTestCase, self).tearDown()

  def create_user(self, fb_id='23', email='john@example.com', username='john'):
    u = User(fb_id=fb_id, email=email, name='John Doe', username=username,
            avatar_url='avatar.jpg', city='Mountain View')
    db.session.add(u)
    db.session.commit()
    return u

  def create_item(self, user_id, item_name='ball', item_desc='small and round'):
    c = Category.get_category('soccer')
    item = Item(name=item_name, description=item_desc, price=23,
                category_id=c.id, image_url='ball.jpg', user_id=user_id)
    db.session.add(item)
    db.session.commit()
    return item


class ClientTestCase(UnitTestCase):

  def setUp(self):
    super(ClientTestCase, self).setUp()
    Category.insert_categories()
    self.client = self.app.test_client()
    #do not request urls from S3
    self.app.config["S3_LOCATION"] = ''

