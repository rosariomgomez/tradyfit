# -*- coding: utf-8 -*-
from helper import SeleniumTestCase
import page


class NotificationsTestCase(SeleniumTestCase):

  @classmethod
  def setUpClass(cls):
    # connect to webdriver, create app, launch server in thread
    super(NotificationsTestCase, cls).setUpClass()


  @classmethod
  def tearDownClass(cls):
    # stop the server, destroy db and remove app context
    super(NotificationsTestCase, cls).tearDownClass()


  def setUp(self):
    if not self.client:
      self.skipTest('Web browser not available')

  def tearDown(self):
    pass


  def test_reply_message(self):
    '''Verify user can reply
    1. Go to home page
    2. Log in with user1
    3. Verify user has notification badge
    4. Go to notification page
    5. Click on unread message
    6. Reply
    7. Verify you are redirected to notifications and have 1 sent msg
    8. Log out
    '''
    self.client.get('http://localhost:5000')

    # home page object
    home_page = page.HomePage(self.client)
    self.assertTrue(home_page.is_title_matches)

    # navigate to login page
    home_page.go_to_login()

    login_page = page.LoginPage(self.client)
    self.assertTrue(login_page.is_title_matches)

    # login user ES
    login_page.login(self.app.config['FB_TEST_EMAIL1'],
                      self.app.config['FB_TEST_PWD1'])

    #verify you have the notification badge
    self.assertTrue(home_page.has_notifications)
    #go to notifications
    home_page.go_to_notifications()

    # notifications page object
    notifications_page = page.NotificationsPage(self.client)
    #click on unread message
    notifications_page.go_to_unread_message('Hi there!')

    #verify you are redirected to message page
    msg_page = page.MessagePage(self.client)
    self.assertTrue(msg_page.is_title_matches)

    #reply message
    msg_page.reply_message('I think we have a deal!')

    #verify you are in notifications page
    self.assertTrue(notifications_page.is_title_matches)

    #verify you have 0 unread / 1 received / 1 sent messages
    self.assertTrue(notifications_page.get_num_unread() == '0')
    self.assertTrue(notifications_page.get_num_received() == '1')
    self.assertTrue(notifications_page.get_num_sent() == '1')

    #log out user
    notifications_page.go_to_log_out()
