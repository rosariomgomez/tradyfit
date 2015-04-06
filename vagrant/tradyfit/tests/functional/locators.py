from selenium.webdriver.common.by import By

class NavBarLocators(object):
  LOGIN = (By.LINK_TEXT, 'Log In with Facebook')
  LIST_ITEM = (By.LINK_TEXT, 'List an item')

class LoginPageLocators(object):
  EMAIL = (By.NAME, 'email')
  PASS = (By.NAME, 'pass')