# -*- coding: utf-8 -*-
import time
from mock import patch
from base import BasicTestCase, UnitTestCase
from app import db
from app.models import Category, User, load_user, Country, State
from app.geolocation import Geolocation


class CategoryModelTestCase(BasicTestCase):

  def setUp(self):
    super(CategoryModelTestCase, self).setUp()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    super(CategoryModelTestCase, self).tearDown()

  def test_insert_categories(self):
    categories = Category.query.all()
    self.assertEqual(categories, [])
    Category.insert_categories()
    c = Category.get_category(name='soccer')
    self.assertEqual(c.name, 'soccer')

  def test_insert_categories_no_dup(self):
    '''make sure that if a category is already in db, it is not
    added again'''
    c = Category(name='soccer')
    db.session.add(c)
    db.session.commit()
    Category.insert_categories()
    self.assertEqual(Category.query.filter_by(name='soccer').count(), 1)


class UserModelTestCase(UnitTestCase):

  def test_username(self):
    u = self.create_user()
    #the username already exists, append the next uid to the name
    self.assertTrue(User.create_username(u.username) == u.username+str(u.id+1))
    #username doesn't exist, so it can be assigned
    self.assertTrue(User.create_username('jacky') == 'jacky')

  def test_ping(self):
    u = self.create_user()
    time.sleep(2)
    last_seen_before = u.last_seen
    u.ping()
    self.assertTrue(u.last_seen > last_seen_before)

  def test_get_user(self):
    u = self.create_user()
    self.assertEqual(User.get_user(u.email), u)
    self.assertEqual(User.get_user('nobody@example.com'), None)

  def test_load_user(self):
    u = self.create_user()
    self.assertEqual(load_user(u.id), u)

  def test_get_avatar(self):
    u = self.create_user()
    avatar = self.app.config['S3_LOCATION'] + "/" + \
                self.app.config['S3_BUCKET'] + \
                self.app.config['S3_UPLOAD_AVATAR_DIR'] + "/" + u.avatar_url
    self.assertEqual(u.avatar(), avatar)

  def test_location_user_with_city(self):
    u = self.create_user()
    u.location('10.0.0.2')
    self.assertTrue(u.latitude == None)

  @patch('app.geolocation.Geolocation', return_value={'key': 'value'})
  @patch('app.geolocation.Geolocation.get_country', return_value=(True, 'US'))
  @patch('app.geolocation.Geolocation.get_state', return_value=(True, 'CA'))
  @patch('app.geolocation.Geolocation.get_city', return_value=(True, 'MV'))
  @patch('app.geolocation.Geolocation.get_latitude', return_value=(True, 123))
  @patch('app.geolocation.Geolocation.get_longitude', return_value=(True, -98))
  def test_location_user_no_city(self, m_geo, m_country, m_state, m_city,
      m_latitude, m_longitude):
    u = self.create_user()
    u.city = ''
    u.location('10.0.0.2')
    self.assertTrue(u.latitude == 123)

  @patch('app.geolocation.Geolocation', return_value={'key': 'value'})
  @patch('app.geolocation.Geolocation.get_country', return_value=(True, ''))
  def test_location_user_no_city_no_country(self, m_geo, m_country):
    u = self.create_user()
    u.city = ''
    u.location('10.0.0.2')
    self.assertTrue(u.latitude == None)


class ItemModelTestCase(UnitTestCase):
  def test_get_image(self):
    user = self.create_user()
    item = self.create_item(user.id)
    image = self.app.config['S3_LOCATION'] + "/" + \
                self.app.config['S3_BUCKET'] + \
                self.app.config['S3_UPLOAD_ITEM_DIR'] + "/" + item.image_url
    self.assertEqual(item.image(), image)


class CountryModelTestCase(UnitTestCase):
  def test_get_countries(self):
    self.assertTrue(type(Country.get_countries()) == dict)

  def test_get_country_name(self):
    self.assertTrue(Country.get_name('US') == 'United States')


class StateModelTestCase(UnitTestCase):
  def test_us_state_name(self):
    self.assertTrue(State.get_us_name('CA') == 'California')
