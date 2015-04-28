# -*- coding: utf-8 -*-
from app.helpers import delete_item_image
from helper import SeleniumTestCase
from app.models import Item
import page
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

  def tearDown(self):
    pass


  def test_create_item(self):
    '''Verify a logged in user can create an item and it is displayed
    on her profile page
    1. Go to home page
    2. Click on Login link
    3. Fill login form and submit
    4. Verify you are successfully logged in and redirected to home page
    5. Go to list an item page
    6. Fill the form and submit
    7. Verify you are redirected to home and a message is displayed verifying
    the item was created
    8. Go to profile page
    9. Check the item is listed in "your listed items" section
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

    #user redirected to Home page
    self.assertTrue('maria' in self.client.page_source)

    # navigate to create item page
    home_page.go_to_create_item()

    list_item_page = page.ListItemPage(self.client)
    self.assertTrue(list_item_page.is_title_matches)

    # create the item
    image_path = os.path.dirname(os.path.abspath(__file__))
    list_item_page.add_item('bike', 'super six', '1245.3', 'cycling',
                            os.path.join(image_path,"files/bike.jpg"))

    # assert an item was successfully created
    self.assertTrue('Your item has been created.' in self.client.page_source)

    # navigate to profile page
    home_page.go_to_profile()

    profile_page = page.ProfilePage(self.client)
    self.assertTrue(profile_page.is_title_matches)

    # assert the created item appears in the page
    self.assertTrue('super six' in self.client.page_source)

    # logout user
    profile_page.go_to_log_out()


  def test_item_send_message(self):
    '''Verify user can send a message
    1. Go to home page
    2. Click on Login link
    3. Go to browse categories
    4. Go to 'Lakers t-shirt' item page
    5. Click on send a message
    6. Fill the form
    7. Verify you are redirected to item page
    8. Go to notifications
    9. Verify you have 2 sent messages
    '''
    self.client.get('http://localhost:5000')

    # home page object
    home_page = page.HomePage(self.client)
    self.assertTrue(home_page.is_title_matches)
    # navigate to login page
    home_page.go_to_login()

    login_page = page.LoginPage(self.client)
    self.assertTrue(login_page.is_title_matches)

    # go to browse categories
    home_page.go_to_browse_categories()

    browse_page = page.BrowsePage(self.client)
    self.assertTrue(browse_page.is_title_matches)

    # go to item page
    browse_page.go_to_item_page('Lakers t-shirt')

    # item page object
    item_page = page.ItemPage(self.client)
    item_page.contact_seller()

    # create_message page object
    create_msg_page = page.CreateMessagePage(self.client)
    self.assertTrue(create_msg_page.is_title_matches)

    # send message
    create_msg_page.send_message('I think your item is cool!')

    # verify you are redirected to item page
    self.assertTrue(item_page.is_title_matches)

    # go to notifications
    item_page.go_to_notifications()

    # notifications page object
    notifications_page = page.NotificationsPage(self.client)

    #verify you have 2 sent messages
    self.assertTrue(notifications_page.get_num_sent() == '2')

    # logout user
    notifications_page.go_to_log_out()
