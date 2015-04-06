# -*- coding: utf-8 -*-
import unittest
from uuid import uuid4
from app import db
from app.models import User, Category
from helper import SeleniumTestCase
import page
from locators import NavBarLocators


class ItemTestCase(SeleniumTestCase):

  @classmethod
  def setUpClass(cls):
    # start webdriver, create app, launch server in thread
    super(ItemTestCase, cls).setUpClass()

    # create the database
    db.create_all()
    Category.insert_categories()


  @classmethod
  def tearDownClass(cls):
    # stop the server, remove app context
    super(ItemTestCase, cls).tearDownClass()

    # destroy database
    db.drop_all()
    db.session.remove()


  def setUp(self):
    if not self.client:
      self.skipTest('Web browser not available')
    #create the fb test user to log in
    u = User(fb_id=self.app.config['FB_TEST_ID'],
            email=self.app.config['FB_TEST_EMAIL'],
            name='Maria Amiecbddcgdc', username='Maria',
            avatar_url=uuid4().hex + '.jpg')
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

    # navigate to item page
    self.client.find_element(*NavBarLocators.LIST_ITEM).click()

    item_page = page.ItemPage(self.client)
    self.assertTrue(item_page.is_title_matches)

    # assert an Image can be added
    self.assertTrue('Upload image' in self.client.page_source)

