# -*- coding: utf-8 -*-
import unittest
import re
from uuid import uuid4
from bs4 import BeautifulSoup
from flask import current_app, url_for
from app import create_app, db
from app.models import Item, Category, User


class ViewTestCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()
    Category.insert_categories()
    self.client = self.app.test_client(use_cookies=True)

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

  def test_navbar_anonymous_user(self):
    '''verify if you are not logged in you cannot see the list an item
    link and you see the log in link'''
    response = self.client.get(url_for('main.index'))
    r = response.get_data(as_text=True)
    self.assertTrue('Log In with Facebook' in r)
    self.assertFalse('List an item' in r)

  def test_navbar_login_user(self):
    '''verify if you are logged in, you can see the link to list an item
    and the right dropdown menu'''
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john', avatar_url=uuid4().hex + '.jpg')
    db.session.add(u)
    db.session.commit()
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      resp = c.get(url_for('main.index'))
      self.assertTrue(b'List an item' in resp.data)
      self.assertTrue(u.username in resp.get_data(as_text=True))

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

  def test_search_form(self):
    '''verify the search form is displayed'''
    response = self.client.get(url_for('main.index'))
    self.assertTrue(b'id="search-form"' in response.data)

  def test_search_form_redirect(self):
    '''verify the search form redirects to results when submit'''
    resp = self.client.post(url_for('main.index'),
                            data={
                                'search': 'soccer ball',
                            }, follow_redirects=True)
    self.assertTrue(b'Search results for "soccer ball":' in resp.data)


class CreateItemViewTestCase(ViewTestCase):
  '''Testing: @main.route('/create/', methods=['GET', 'POST'])'''

  def test_create_item_route_login(self):
    '''verify you can create an item
    1. Go to the create an item's page
    2. Assert you get the correct page
    '''
    #create a user
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john', avatar_url=uuid4().hex + '.jpg')
    db.session.add(u)
    db.session.commit()
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      response = self.client.get(url_for('main.create'))
      self.assertEquals(response.status_code, 200)
      r = response.get_data(as_text=True)
      self.assertTrue('id="item-creation"' in r)

  def test_create_item_form(self):
    '''verify all fields for creating an item are present
    1. Go to the create an item's page
    2. Check all fields in the form are present
    '''
    #create a user
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john', avatar_url=uuid4().hex + '.jpg')
    db.session.add(u)
    db.session.commit()
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
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
    #create a user
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john', avatar_url=uuid4().hex + '.jpg')
    db.session.add(u)
    db.session.commit()
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
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
        price=23, category=c, image_url='image.jpg')
    db.session.add(item)
    db.session.commit()
    response = self.client.get(url_for('main.item', id=item.id))
    r = response.get_data(as_text=True)
    self.assertTrue('id="item-'+str(item.id) + '"' in r)


class EditItemViewTestCase(ViewTestCase):
  '''Testing: @main.route('/edit/<int:id>', methods=['GET', 'POST'])'''

  def test_edit_item_route(self):
    '''verify you get a 404 for a non existent item and that you can
    access the edit page for a created item if you are the owner
    1. Go to a non existent item edit's page
    2. Assert you get a 404 response
    3. Try to edit another user's item
    4. Go to the edit item's page
    5. Assert you get the correct edit page
    '''
    #users creation
    u = User(fb_id='23', email='john@example.com', name='John Doe',
          username='john', avatar_url=uuid4().hex + '.jpg')
    u1 = User(fb_id='25', email='maggy@example.com', name='Maggy Simpson',
          username='maggy', avatar_url=uuid4().hex + '.jpg')
    db.session.add_all([u, u1])
    db.session.commit()
    #item creation
    c = Category.query.filter_by(name='soccer').one()
    item = Item(name='soccer ball', description='plain ball',
                price=23, category=c, user_id=u.id)
    db.session.add(item)
    db.session.commit()

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u1.id
        sess['_fresh'] = True
      #1. non existent item
      response = self.client.get(url_for('main.edit', id=12))
      self.assertEquals(response.status_code, 404)

      #2. try to edit other user's item
      response = self.client.get(url_for('main.edit', id=item.id),
                                follow_redirects=True)
      self.assertFalse('id="edit-item-'+str(item.id) + '"' in
                      response.get_data(as_text=True))

    #3. edit your item
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      response = self.client.get(url_for('main.edit', id=item.id),
                                follow_redirects=True)
      self.assertTrue('id="edit-item-'+str(item.id) + '"' in
                      response.get_data(as_text=True))

  def test_edit_form(self):
    '''verify that an item can be edit and it's updated correctly'''
    u = User(fb_id='23', email='john@example.com', name='John Doe',
          username='john', avatar_url=uuid4().hex + '.jpg')
    db.session.add(u)
    db.session.commit()
    c = Category.query.filter_by(name='soccer').one()
    item = Item(name='soccer ball', description='plain ball',
                price=23, category=c, user_id=u.id)
    db.session.add(item)
    db.session.commit()
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      resp = self.client.post(url_for('main.edit', id=item.id),
                              data={
                                'name': item.name,
                                'description': item.description,
                                'price': 234,
                                'category': item.category.id
                              }, follow_redirects=True)
      self.assertTrue(b'Your item has been updated.' in resp.data)
      self.assertTrue(b'234$' in resp.data)


class DeleteItemViewTestCase(ViewTestCase):
    '''Testing: @main.route('/delete/<int:id>')'''

    def test_delete_item_route(self):
      '''verify you get a 404 for a non existent item
      and that you can delete a created item if you are the owner
      1. Request to delete a non existent item
      2. Assert you get a 404 response
      3. Try to delete another user's item
      4. Go to the delete route
      5. Assert your item has been deleted
      '''
      #users creation
      u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john', avatar_url=uuid4().hex + '.jpg')
      u1 = User(fb_id='25', email='maggy@example.com', name='Maggy Simpson',
            username='maggy', avatar_url=uuid4().hex + '.jpg')
      db.session.add_all([u, u1])
      db.session.commit()
      #item creation
      c = Category.query.filter_by(name='soccer').one()
      item = Item(name='soccer ball', description='plain ball',
                  price=23, category=c, user_id=u.id,
                  image_url=self.app.config["DEFAULT_ITEM"])
      db.session.add(item)
      db.session.commit()

      with self.client as c:
        with c.session_transaction() as sess:
          sess['user_id'] = u1.id
          sess['_fresh'] = True
        #1. non existent item
        response = self.client.get(url_for('main.delete', id=12))
        self.assertEquals(response.status_code, 404)

        #2. try to delete other user's item
        response = self.client.get(url_for('main.delete', id=item.id),
                                  follow_redirects=True)
        self.assertFalse(b'Your item has been deleted.' in response.data)

      #3. delete your item
      with self.client as c:
        with c.session_transaction() as sess:
          sess['user_id'] = u.id
          sess['_fresh'] = True
        response = self.client.get(url_for('main.delete', id=item.id),
                                  follow_redirects=True)
        self.assertTrue(b'Your item has been deleted.' in response.data)


class SearchResultsTestCase(ViewTestCase):
  '''Testing: @main.route('/search_results/<query>')'''

  def test_search_results(self):
    '''verify that search results are shown as expected
    1. Create 3 items
    2. Make a search with a word in common from 2 of the 3 items
       (independent of uper/lower case)
    3. Check both items appears on the results in the correct order
       (ordered by timestamp)
    '''
    c = Category.query.filter_by(name='soccer').one()
    item = Item(name='soccer ball', description='ball signed by Manchester',
                price=23, category=c,
                image_url=self.app.config["DEFAULT_ITEM"])
    db.session.add(item)
    db.session.commit()
    item1 = Item(name='t-shirt', description='manchester club t-shirt',
                price=56, category=c,
                image_url=self.app.config["DEFAULT_ITEM"])
    item2 = Item(name='tri bycicle', description='scatante bike',
                price=2356, category=c,
                image_url=self.app.config["DEFAULT_ITEM"])
    db.session.add_all([item1, item2])
    db.session.commit()
    response = self.client.get(url_for('main.search_results',
                                      query='manchester'))
    resp = response.get_data(as_text=True)
    self.assertTrue('Search results for "manchester":' in resp)
    soup = BeautifulSoup(resp)
    items = soup.find_all("li", id=re.compile("^item-"))
    self.assertTrue(len(items) == 2)
    self.assertTrue("item-"+str(item1.id) in str(items[0]))

  def test_search_sqlinjection(self):
    '''make sure the search is not vulnerable to an SQL injection'''
    response = self.client.get(url_for('main.search_results',
                              query="foo UNION SELECT id FROM categories"))
    resp = response.get_data(as_text=True)
    soup = BeautifulSoup(resp)
    items = soup.find_all("li", id=re.compile("^item-"))
    self.assertTrue(not items)

