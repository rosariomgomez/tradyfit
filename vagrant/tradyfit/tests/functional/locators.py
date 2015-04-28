# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By


class NavBarLocators(object):
  HOME = (By.LINK_TEXT, 'TradyFit')
  LOGIN = (By.LINK_TEXT, 'Log In with Facebook')
  LIST_ITEM = (By.LINK_TEXT, 'List an item')
  BROWSE_CATEGORIES = (By.LINK_TEXT, 'Browse categories')
  NOTIFICATIONS = (By.ID, 'notif-link')
  NOTIFICATIONS_BADGE = (By.CLASS_NAME, 'badge')
  USER_DROPDOWN = (By.ID, 'user-dropdown')
  PROFILE = (By.LINK_TEXT, 'Profile')
  LOGOUT = (By.LINK_TEXT, 'Log Out')


class LoginPageLocators(object):
  EMAIL = (By.NAME, 'email')
  PASS = (By.NAME, 'pass')


class HomePageLocators(object):
  SEARCH = (By.ID, 'search')
  SUBMIT = (By.ID, 'submit-search')


class ItemPageLocators(object):
  CONTACT = (By.LINK_TEXT, 'Contact seller')


class ListItemPageLocators(object):
  NAME = (By.ID, 'name')
  DESCRIPTION = (By.ID, 'description')
  PRICE = (By.ID, 'price')
  CATEGORY = (By.ID, 'category')
  IMAGE = (By.ID, 'image')
  SUBMIT = (By.ID, 'submit')


class CreateMessagePageLocators(object):
  DESCRIPTION = (By.ID, 'description')
  SEND = (By.ID, 'submit')


class MessagePageLocators(object):
  DESCRIPTION = (By.ID, 'description')
  SEND = (By.ID, 'submit')


class NotificationsPageLocators(object):
  UNREAD = (By.CLASS_NAME, 'num-unread')
  SENT = (By.CLASS_NAME, 'num-sent')
  RECEIVED = (By.CLASS_NAME, 'num-sent')

