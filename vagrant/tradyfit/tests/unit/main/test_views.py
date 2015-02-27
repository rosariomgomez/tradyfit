# -*- coding: utf-8 -*-
import unittest
import re
from bs4 import BeautifulSoup
from flask import current_app, url_for
from app import create_app, db
from app.models import Item, Category


class ViewTestCase(unittest.TestCase):
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


class IndexViewTestCase(ViewTestCase):
  '''Testing: @main.route('/')'''

  def test_index_route(self):
    response = self.client.get('/')
    self.assertEquals(response.status_code, 200)

  def test_index(self):
    '''verify you are in the index page'''
    response = self.client.get(url_for('main.index'))
    r = response.get_data(as_text=True)
    self.assertTrue('Welcome to TradyFit' in r)

  def test_item_displayed(self):
    '''verify you can see an item listed in the index page
    1. Create item
    2. Go to index page
    3. Assert the item is there
    '''
    c = Category.query.filter_by(name='soccer').one()
    item = Item(name='soccer ball', description='plain ball',
        price=23, category=c)
    db.session.add(item)
    response = self.client.get(url_for('main.index'))
    r = response.get_data(as_text=True)
    self.assertTrue("item-"+str(item.id) in r)

  def test_items_displayed_correct_order(self):
    '''verify you can see the items listed ordered by timestamp at the 
    index page
    1. Create two items
    2. Go to index page
    3. Assert the second item created appears on top
    '''
    c = Category.query.filter_by(name='soccer').one()
    item = Item(name='soccer ball', description='plain ball',
        price=23, category=c)
    db.session.add(item)
    item2 = Item(name='soccer t-shirt', description='Real Madrid size M',
        price=28, category=c)
    db.session.add(item2)
    response = self.client.get(url_for('main.index'))
    soup = BeautifulSoup(response.get_data(as_text=True))
    items = soup.find_all("li", id=re.compile("^item-"))
    self.assertTrue("item-"+str(item2.id) in str(items[0]))


class CreateItemViewTestCase(ViewTestCase):
  '''Testing: @main.route('/create/', methods=['GET', 'POST'])'''
  
  def test_create_item_route(self):
    '''verify you can access the create an item page
    1. Go to the create an item's page
    2. Assert you get the correct page
    '''
    response = self.client.get(url_for('main.create'))
    self.assertEquals(response.status_code, 200)
    r = response.get_data(as_text=True)
    self.assertTrue('id="item-creation"' in r)

  def test_create_item_form(self):
    '''verify all fields for creating an item are present
    1. Go to the create an item's page
    2. Check all fields in the form are present
    '''
    response = self.client.get(url_for('main.create'))
    r = response.get_data(as_text=True)
    fields = ['name', 'description', 'price', 'category']
    for field in fields:
        self.assertTrue('id="' + field + '"' in r)

  def test_create_item(self):
    '''verify an item can be correctly created
    1. Go to the create an item's page
    2. Field in the form with a happy case
    3. Verify you are redirected to home page and the item is present
    '''
    c = Category.query.filter_by(name='soccer').one()
    resp = self.client.post(url_for('main.create'), 
                            data={
                                'name': 'soccer ball',
                                'description': 'plain ball',
                                'price': 234,
                                'category': c.id
                            }, follow_redirects=True)
    self.assertTrue(b'Your item has been created' in resp.data)
    self.assertTrue(b'234$' in resp.data)


class ItemViewTestCase(ViewTestCase):
  '''Testing: @main.route('/item/<int:id>')'''

  def test_item_route(self):
    '''verify you get a 404 for a non existent item
    and that you can access the item page for an existent item
    1. Go to a non existent item's page
    2. Assert you get a 404 response
    3. Create an item
    4. Go to the item's page
    5. Assert you get the correct page 
    '''
    response = self.client.get(url_for('main.item', id=12))
    self.assertEquals(response.status_code, 404)
    c = Category.query.filter_by(name='soccer').one()
    item = Item(name='soccer ball', description='plain ball',
        price=23, category=c)
    db.session.add(item)
    db.session.commit()
    response = self.client.get(url_for('main.item', id=item.id))
    r = response.get_data(as_text=True)
    self.assertTrue('id="item-'+str(item.id) + '"' in r)


class EditItemViewTestCase(ViewTestCase):
  '''Testing: @main.route('/edit/<int:id>', methods=['GET', 'POST'])'''

  def test_edit_item_route(self):
    '''verify you get a 404 for a non existent item
    and that you can access the edit page for a created item
    1. Go to a non existent item edit's page
    2. Assert you get a 404 response
    3. Create an item
    4. Go to the edit item's page
    5. Assert you get the correct edit page 
    '''
    response = self.client.get(url_for('main.edit', id=12))
    self.assertEquals(response.status_code, 404)
    c = Category.query.filter_by(name='soccer').one()
    item = Item(name='soccer ball', description='plain ball',
        price=23, category=c)
    db.session.add(item)
    db.session.commit()
    response = self.client.get(url_for('main.edit', id=item.id))
    r = response.get_data(as_text=True)
    self.assertTrue('id="edit-item-'+str(item.id) + '"' in r)

  def test_edit_form(self):
    '''verify that an item can be edit and it's updated correctly'''
    c = Category.query.filter_by(name='soccer').one()
    item = Item(name='soccer ball', description='plain ball',
                price=23, category=c)
    db.session.add(item)
    db.session.commit()
    resp = self.client.post(url_for('main.edit', id=item.id), 
                            data={
                                'name': item.name,
                                'description': item.description,
                                'price': 234,
                                'category': c.id
                            }, follow_redirects=True)
    self.assertTrue(b'Your item has been updated' in resp.data)
    self.assertTrue(b'234$' in resp.data)

class DeleteItemViewTestCase(ViewTestCase):
    '''Testing: @main.route('/delete/<int:id>')'''

    def test_delete_item_route(self):
      '''verify you get a 404 for a non existent item
      and that you can delete a created item
      1. Request to delete a non existent item
      2. Assert you get a 404 response
      3. Create an item 
      4. Check it appears at index page
      4. Go to the delete route
      5. Assert your item has been deleted
      '''
      response = self.client.get(url_for('main.delete', id=12))
      self.assertEquals(response.status_code, 404)
      c = Category.query.filter_by(name='soccer').one()
      item = Item(name='soccer ball', description='plain ball',
                  price=23, category=c)
      db.session.add(item)
      db.session.commit()
      response = self.client.get(url_for('main.index'))
      r = response.get_data(as_text=True)
      self.assertTrue("item-"+str(item.id) in r)
      response = self.client.get(url_for('main.delete', id=item.id),
                                  follow_redirects=True)
      self.assertTrue(b'Your item has been deleted.' in response.data)
