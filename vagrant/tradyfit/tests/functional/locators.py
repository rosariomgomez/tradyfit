# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By


class NavBarLocators(object):
  LOGIN = (By.LINK_TEXT, 'Log In with Facebook')
  LIST_ITEM = (By.LINK_TEXT, 'List an item')
  BROWSE_CATEGORIES = (By.LINK_TEXT, 'Browse categories')
  NOTIFICATIONS = (By.LINK_TEXT, 'Notifications')
  USER_DROPDOWN = (By.ID, 'user-dropdown')
  PROFILE = (By.LINK_TEXT, 'Profile')
  LOGOUT = (By.LINK_TEXT, 'Log Out')

class LoginPageLocators(object):
  EMAIL = (By.NAME, 'email')
  PASS = (By.NAME, 'pass')

class ListItemPageLocators(object):
  NAME = (By.ID, 'name')
  DESCRIPTION = (By.ID, 'description')
  PRICE = (By.ID, 'price')
  CATEGORY = (By.ID, 'category')
  IMAGE = (By.ID, 'image')
  SUBMIT = (By.ID, 'submit')