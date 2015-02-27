# -*- coding: utf-8 -*-
import unittest
import re
from bs4 import BeautifulSoup
from flask import current_app, url_for
from app import create_app, db
from app.models import Item, Category


class IndexFunctionalTestCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()
    Category.insert_categories()
    self.client = self.app.test_client()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def test_edit_link(self):
    '''verify an item can be edited from the index page
    1. Create an item
    2. Go to index page
    3. Assert the edit link is present
    '''
    c = Category.query.filter_by(name='soccer').one()
    item = Item(name='soccer ball', description='plain ball',
        price=23, category=c)
    db.session.add(item)
    response = self.client.get(url_for('main.index'))
    r = response.get_data(as_text=True)
    self.assertTrue('<a href="/edit/' + str(item.id) + '"' in r)

  def test_delete_item(self):
    '''verify an item can be deleted from the index page
    1. Create an item
    2. Go to index page
    3. Assert the delete link is present
    4. Delete the item
    5. Verfiy the item does not appear at the index page anymore
    '''
    c = Category.query.filter_by(name='soccer').one()
    item = Item(name='soccer ball', description='plain ball',
        price=23, category=c)
    db.session.add(item)
    response = self.client.get(url_for('main.index'))
    r = response.get_data(as_text=True)
    self.assertTrue('<a href="/delete/' + str(item.id) + '"' in r)
    response = self.client.get(url_for('main.delete', id=str(item.id)),
                                follow_redirects=True)
    r = response.get_data(as_text=True)
    self.assertFalse(item.name in r)

