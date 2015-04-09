# -*- coding: utf-8 -*-
import threading
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from app import create_app, db
from app.models import Category


class SeleniumTestCase(unittest.TestCase):
  client = None
  app = create_app('testing')

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
      # add the application context
      cls.app_context = cls.app.app_context()
      cls.app_context.push()

      # suppress logging to keep unittest output clean
      import logging
      logger = logging.getLogger('werkzeug')
      logger.setLevel("ERROR")

      # create the database and insert categories
      db.create_all()
      Category.insert_categories()

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
      db.session.remove()
      db.drop_all()

      # remove application context
      cls.app_context.pop()

