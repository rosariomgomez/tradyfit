# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from StringIO import StringIO
from mock import patch
from flask import url_for
from app.models import Category, Item
from base import ClientTestCase
import app.main.views


class IndexViewTestCase(ClientTestCase):
  '''Testing: @main.route('/')'''

  def test_index_route(self):
    response = self.client.get('/')
    self.assertEquals(response.status_code, 200)

  def test_index(self):
    '''verify you are in the index page'''
    response = self.client.get(url_for('main.index'))
    r = response.get_data(as_text=True)
    self.assertTrue('id="search-form"' in r)

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
    u = self.create_user()
    resp = self.make_get_request(u, 'main.index')
    self.assertTrue(b'List an item' in resp.data)
    self.assertTrue(u.username in resp.get_data(as_text=True))

  def test_item_displayed(self):
    '''verify you can see an item listed in the index page
    1. Create item
    2. Go to index page
    3. Assert the item is there
    '''
    u = self.create_user()
    item = self.create_item(u.id)
    response = self.client.get(url_for('main.index'))
    r = response.get_data(as_text=True)
    self.assertTrue("item-"+str(item.id) in r)

  def test_items_displayed_correct_order(self):
    '''verify you can see the items listed ordered by timestamp at the
    index page
    1. Create two items
    2. Go to index page
    3. Assert the second item created appears before
    '''
    u = self.create_user()
    item = self.create_item(u.id)
    item2 = self.create_item(u.id)
    response = self.client.get(url_for('main.index'))
    soup = BeautifulSoup(response.get_data(as_text=True))
    items = soup.find_all("div", {"class": "thumbnail"})
    self.assertTrue("item-"+str(item2.id) in str(items[0]))

  def test_search_form(self):
    '''verify the search form is displayed'''
    response = self.client.get(url_for('main.index'))
    self.assertTrue(b'id="search-form"' in response.data)



class CategoriesViewTestCase(ClientTestCase):
  '''Testing: @main.route('/items/categories')'''

  def test_categories_route(self):
    '''verify you can go to the categories page
    and see all categories listed'''
    num_cat = Category.query.count()
    response = self.client.get(url_for('main.categories'))
    soup = BeautifulSoup(response.get_data(as_text=True))
    categories = soup.find_all("li", {"class": "list-group-item"})
    self.assertTrue(num_cat == len(categories))



class CategoryViewTestCase(ClientTestCase):
  '''Testing: @main.route('/items/category/<int:id>')'''

  def test_category_route(self):
    '''verify you get a list of items of the requested category'''
    u = self.create_user()
    item = self.create_item(u.id)
    item2 = self.create_item(u.id, 'bike', 'fast', 'cycling')
    c = Category.get_category('cycling')
    response = self.client.get(url_for('main.category', id=c.id))
    self.assertTrue('id="item-'+str(item2.id) in response.data)
    self.assertFalse('id="item-'+str(item.id) in response.data)


  def test_category_route_404(self):
    '''verfiy you get a 404 page if the category is not valid'''
    response = self.client.get(url_for('main.category', id=999))
    self.assertTrue(response.status_code, 404)



class ProfileViewTestCase(ClientTestCase):
  '''Testing: @main.route('/profile', methods=['GET','POST'])'''

  def test_profile_route(self):
    '''verify you can go to profile page
    1. Go to the profile page
    2. Assert you get the correct page
    '''
    u = self.create_user()
    response = self.make_get_request(u, 'main.profile')
    self.assertEquals(response.status_code, 200)
    self.assertTrue('id="user-form"' in response.get_data(as_text=True))

  def test_profile_form(self):
    '''verify all fields for editing a user are present
    1. Go to the profile page
    2. Check all fields in the form are present
    '''
    u = self.create_user()
    response = self.make_get_request(u, 'main.profile')
    r = response.get_data(as_text=True)
    fields = ['username', 'name', 'country', 'state', 'city']
    for field in fields:
        self.assertTrue('id="' + field + '"' in r)


class DeleteAccountViewTestCase(ClientTestCase):
  '''Testing: @main.route('/delete_account', methods=['GET','POST'])'''

  def test_delete_account_route(self):
    '''verify you can go to delete account page
    1. Go to the delete account page
    2. Assert you get the correct page
    '''
    u = self.create_user()
    response = self.make_get_request(u, 'main.delete_account')
    self.assertEquals(response.status_code, 200)
    r = response.get_data(as_text=True)
    self.assertTrue('id="delete-account"' in r)


class CreateItemViewTestCase(ClientTestCase):
  '''Testing: @main.route('/create', methods=['GET', 'POST'])'''

  def test_create_item_route_user_nolocation(self):
    '''verify you are redirected to the profile page
    if the user has not location information
    1. Go to create an item's page
    2. Assert you are redirected to profile page
    '''
    u = self.create_user_no_location()
    response = self.make_get_request(u, 'main.create')
    r = response.get_data(as_text=True)
    self.assertTrue('Before creating an item, you should have a valid location'
                    in r)


  def test_create_item_route_user_location(self):
    '''verify you can go to create an item page if the user has location
    information (latitude/longitude)
    1. Go to the create an item's page
    2. Assert you get the correct page
    '''
    u = self.create_user()
    response = self.make_get_request(u, 'main.create')
    self.assertEquals(response.status_code, 200)
    r = response.get_data(as_text=True)
    self.assertTrue('id="item-creation"' in r)


  def test_create_item_form(self):
    '''verify all fields for creating an item are present
    1. Go to the create an item's page
    2. Check all fields in the form are present
    '''
    u = self.create_user()
    response = self.make_get_request(u, 'main.create')
    r = response.get_data(as_text=True)
    fields = ['name', 'description', 'price', 'category', 'image']
    for field in fields:
        self.assertTrue('id="' + field + '"' in r)


class ItemViewTestCase(ClientTestCase):
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
    u = self.create_user()
    item = self.create_item(u.id)
    response = self.client.get(url_for('main.item', id=item.id))
    r = response.get_data(as_text=True)
    self.assertTrue('id="item-'+str(item.id) + '"' in r)


def form_data(item, image=None):
  if image:
    image = (StringIO('contents'), image)
  return {
          'name': item.name,
          'description': item.description,
          'price': 234,
          'category': item.category.id,
          'image': image
          }


class EditItemViewTestCase(ClientTestCase):
  '''Testing: @main.route('/edit/<int:id>', methods=['GET', 'POST'])'''

  def test_edit_item_route(self):
    '''verify you get a 404 for a non existent item and that you can
    access the edit page for a created item if you are the owner
    1. Go to a non existent item edit's page
    2. Assert you get a 404 response
    3. Try to go to edit page from another user's
    4. Go to the edit item's page
    5. Assert you get the correct edit page
    '''
    u = self.create_user()
    u1 = self.create_user('25', 'maggy@example.com', 'maggy')
    item = self.create_item(u.id)

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u1.id
        sess['_fresh'] = True
      #1. non existent item
      response = self.client.get(url_for('main.edit', id=12))
      self.assertEquals(response.status_code, 404)

      #2. try to go to edit page from other user
      response = self.client.get(url_for('main.edit', id=item.id),
                                follow_redirects=True)
      self.assertFalse('id="edit-item-'+str(item.id) + '"' in
                      response.get_data(as_text=True))

    #3. edit your item page
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      response = self.client.get(url_for('main.edit', id=item.id),
                                follow_redirects=True)
      self.assertTrue('id="edit-item-'+str(item.id) + '"' in
                      response.get_data(as_text=True))

  def test_edit_form_no_image_change(self):
    '''verify that an item can be edit and it's updated correctly
    without image change'''

    u = self.create_user()
    item = self.create_item(u.id)

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      resp = self.client.post(url_for('main.edit', id=item.id),
                              data=form_data(item), follow_redirects=True)
      self.assertTrue(b'Your item has been updated.' in resp.data)
      self.assertTrue(item.description in resp.data)

  @patch('app.main.views.save_item_image', return_value='new_s3_img.jpg')
  @patch('app.main.views.delete_item_image', return_value=True)
  def test_edit_form_image_change(self, mock_save_image, mock_delete_image):
    '''verify that an item can be edit and it's updated correctly
    with new image'''

    u = self.create_user()
    item = self.create_item(u.id)

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      resp = self.client.post(url_for('main.edit', id=item.id),
                                data=form_data(item, 'new_image.jpg'),
                                follow_redirects=True)
      self.assertTrue(b'Your item has been updated.' in resp.data)
      self.assertTrue(item.description in resp.data)
      self.assertTrue(mock_delete_image.called_with('image.jpg'))

  @patch('app.main.views.save_item_image', return_value=None)
  def test_edit_form_image_change_fail(self, mock_save_image):
    '''verify that an item can be edit and it is not updated if there
    is a problem uploading the new image'''

    u = self.create_user()
    item = self.create_item(u.id)

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      resp = self.client.post(url_for('main.edit', id=item.id),
                              data=form_data(item, 'new_image.jpg'),
                              follow_redirects=True)
      self.assertTrue(b'Sorry, there was an error updating your item.'
                      in resp.data)
      self.assertTrue(item.image_url in resp.data) #old image still in item

  @patch('app.main.views.save_item_image', return_value='new_s3_img.jpg')
  @patch('app.main.views.delete_item_image', return_value=False)
  def test_edit_form_image_delete_fail(self, mock_save_item, mock_delete_image):
    '''verify that an item can be edit and it's not updated if
    there is an error deleting the images'''

    u = self.create_user()
    item = self.create_item(u.id)

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      resp = self.client.post(url_for('main.edit', id=item.id),
                              data=form_data(item, 'new_image.jpg'),
                              follow_redirects=True)
      self.assertTrue(b'Sorry, there was an error updating your item.' in
                      resp.data)
      self.assertTrue(item.image_url in resp.data) #old image still in item


class DeleteItemViewTestCase(ClientTestCase):
  '''Testing: @main.route('/delete/<int:id>')'''

  def test_delete_item_route(self):
    '''verify you get a 404 for a non existent item
    and that you get the delete page of an item if you are the owner
    1. Request to delete a non existent item
    2. Assert you get a 404 response
    3. Try to delete another user's item
    4. Go to the delete route of an item you are the owner
    5. Assert you get the correct item for deletion
    '''
    u = self.create_user()
    u1 = self.create_user('25', 'maggy@example.com', 'maggy')
    item = self.create_item(u.id)

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

      response = self.client.get(url_for('main.delete', id=item.id))
      self.assertTrue(item.name.capitalize() in response.data)

  def test_delete_item(self):
    '''verify you can delete an item
    1. Go to the delete route of an item you are the owner
    2. Click on delete item button
    3. Assert you are redirected home and the item has been deleted
    '''
    u = self.create_user()
    item = self.create_item(u.id)
    item_id = item.id

    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True

      resp = self.client.post(url_for('main.delete', id=item.id),
                              follow_redirects=True)
      self.assertTrue('Your item has been deleted' in resp.data)
      self.assertTrue(Item.query.get(item_id) is None)
