# -*- coding: utf-8 -*-
from uuid import uuid4
from app import db
from app.models import User, Item
from app.helpers import delete_item_image
from helper import SeleniumTestCase
import page
from locators import NavBarLocators
import time
import os


class ItemTestCase(SeleniumTestCase):

  @classmethod
  def setUpClass(cls):
    # connect to webdriver, create app, launch server in thread
    super(ItemTestCase, cls).setUpClass()


  @classmethod
  def tearDownClass(cls):
    #remote webdriver was launch
    if cls.client:
      #delete item images from S3 if any
      items = Item.query.all()
      for item in items:
        delete_item_image(item.image_url)

    # stop the server, destroy db and remove app context
    super(ItemTestCase, cls).tearDownClass()


  def setUp(self):
    if not self.client:
      self.skipTest('Web browser not available')

    #create the fb test user to log in
    u = User(fb_id=self.app.config['FB_TEST_ID'],
            email=self.app.config['FB_TEST_EMAIL'],
            name='Maria Amiecbddcgdc', username='Maria',
            avatar_url=uuid4().hex + '.jpg',
            city='Mountain View', country='US', state='CA')
    db.session.add(u)
    db.session.commit()

  def tearDown(self):
    pass


  def test_create_item(self):
    self.client.get('http://localhost:5000')

    # home page object
    home_page = page.HomePage(self.client)
    self.assertTrue(home_page.is_title_matches)
    # navigate to login page
    home_page.go_to_login()

    login_page = page.LoginPage(self.client)
    self.assertTrue(login_page.is_title_matches)

    # login user
    login_page.login(self.app.config['FB_TEST_EMAIL'],
                    self.app.config['FB_TEST_PWD'])

    #user redirected to Home page
    self.assertTrue('Maria' in self.client.page_source)

    # navigate to create item page
    self.client.find_element(*NavBarLocators.LIST_ITEM).click()

    list_item_page = page.ListItemPage(self.client)
    self.assertTrue(list_item_page.is_title_matches)

    # assert an item was successfully created
    image_path = os.path.dirname(os.path.abspath(__file__))
    list_item_page.add_item('bike', 'super six', '1245.3', 'cycling',
                            os.path.join(image_path,"files/bike.jpg"))
    self.assertTrue('Your item has been created.' in self.client.page_source)

