# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from helper import SeleniumTestCase
import page


class SearchTestCase(SeleniumTestCase):

  @classmethod
  def setUpClass(cls):
    # connect to webdriver, create app, launch server in thread
    super(SearchTestCase, cls).setUpClass()

  @classmethod
  def tearDownClass(cls):
    # stop the server, destroy db and remove app context
    super(SearchTestCase, cls).tearDownClass()


  def setUp(self):
    if not self.client:
      self.skipTest('Web browser not available')

  def tearDown(self):
    pass


  def test_search_no_login(self):
    '''Verify a not logged in user see items on a search ordered
    by time creation
    1. Go to home page
    2. Make a search with the word 't-shirt'
    3. Verify you are redirected to the search results page
    4. Verify items are displayed by time creation (last first)
    '''
    self.client.get('http://localhost:5000')

    # home page object
    home_page = page.HomePage(self.client)
    self.assertTrue(home_page.is_title_matches)

    # make a search
    home_page.make_search('t-shirt')

    # assert the items appears in the page ordered by desc time creation
    soup = BeautifulSoup(self.client.page_source)
    items = soup.find_all("div", id=re.compile("^item-"))
    self.assertTrue(len(items) == 2)
    self.assertTrue('Lakers t-shirt' in str(items[0]))


  def test_search_login(self):
    '''Verify a logged in user see items on a search ordered
    by nearby location
    1. Go to home page
    2. Click on Login link
    3. Fill login form and submit
    4. Make a search with the word 'bike'
    5. Verify you are redirected to the search results page
    6. Verify items are displayed by time creation (last first)
    '''
    self.client.get('http://localhost:5000')

    # home page object
    home_page = page.HomePage(self.client)
    self.assertTrue(home_page.is_title_matches)

    # navigate to login page
    home_page.go_to_login()

    login_page = page.LoginPage(self.client)
    self.assertTrue(login_page.is_title_matches)

    # login user US
    login_page.login(self.app.config['FB_TEST_EMAIL'],
                      self.app.config['FB_TEST_PWD'])

    # make a search
    home_page.make_search('t-shirt')

    search_page = page.SearchPage(self.client)
    self.assertTrue(search_page.is_title_matches)

    # assert the items appears in the page ordered by user nearby
    soup = BeautifulSoup(self.client.page_source)
    items = soup.find_all("div", id=re.compile("^item-"))
    self.assertTrue(len(items) == 2)
    self.assertTrue('Soccer t-shirt' in str(items[0]))

    #log out user
    search_page.go_to_log_out()

