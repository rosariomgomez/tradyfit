# -*- coding: utf-8 -*-
import threading
import time
import unittest
import re
from uuid import uuid4
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from app import create_app, db
from app.models import Item, Category, User

class SeleniumTestCase(unittest.TestCase):
  client = None

  @classmethod
  def run_server(cls):
    cls.app.run(host="0.0.0.0", port=5000)

  @classmethod
  def setUpClass(cls):
    # start Firefox in remote
    try:
      cls.client = webdriver.Remote(
              command_executor='http://10.0.0.3:4444/wd/hub',
              desired_capabilities=DesiredCapabilities.FIREFOX)
    except:
      print('something went wrong, make sure the remote webdriver server is up')

    # skip these tests if the browser could not be started
    if cls.client:
      # create the application
      cls.app = create_app('testing')
      cls.app_context = cls.app.app_context()
      cls.app_context.push()

      # suppress logging to keep unittest output clean
      import logging
      logger = logging.getLogger('werkzeug')
      logger.setLevel("ERROR")

      # create the database
      db.create_all()

      # start the Flask server in a thread
      td = threading.Thread(target=SeleniumTestCase.run_server)
      td.start()

      # give the server a second to ensure it is up
      time.sleep(1)

  @classmethod
  def tearDownClass(cls):
    if cls.client:
      # stop the flask server and the browser
      cls.client.get('http://localhost:5000/shutdown')
      cls.client.close()

      # destroy database
      db.drop_all()
      db.session.remove()

      # remove application context
      cls.app_context.pop()

  def setUp(self):
    if not self.client:
      self.skipTest('Web browser not available')
    #create the fb test user
    u = User(fb_id='100009532443743',
            email='dfnzpaq_carrierosen_1428278204@tfbnw.net',
            name='Maria Amiecbddcgdc', username='Maria',
            avatar_url=uuid4().hex + '.jpg')
    db.session.add(u)
    db.session.commit()

  def tearDown(self):
    pass

  def test_create_item(self):
    self.client.get('http://localhost:5000')
    self.assertTrue('Welcome to TradyFit' in self.client.page_source)

    # navigate to login page
    self.client.find_element_by_link_text('Log In with Facebook').click()
    self.assertTrue('Facebook Login' in self.client.page_source)

    # login
    self.client.find_element_by_name('email').\
        send_keys('dfnzpaq_carrierosen_1428278204@tfbnw.net')
    password_field = self.client.find_element_by_name('pass')
    password_field.send_keys('tradyfitSecret')
    password_field.submit()

    time.sleep(2)
    self.assertTrue('Maria' in self.client.page_source)

    # navigate to create an item page
    self.client.find_element_by_link_text('List an item').click()
    self.assertTrue('List your item' in self.client.page_source)

    # assert an Image can be added
    self.assertTrue('Upload image' in self.client.page_source)




