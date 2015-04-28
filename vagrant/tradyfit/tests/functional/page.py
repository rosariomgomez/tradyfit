# -*- coding: utf-8 -*-
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
from locators import NavBarLocators, LoginPageLocators, ListItemPageLocators,\
HomePageLocators, ItemPageLocators, CreateMessagePageLocators, \
NotificationsPageLocators, MessagePageLocators


class BasePage(object):

  def __init__(self, client):
    self.client = client

  def is_title_matches(self, title):
    return title in self.client.title

  def go_to_login(self):
    self.client.find_element(*NavBarLocators.LOGIN).click()

  def go_to_home(self):
    self.client.find_element(*NavBarLocators.HOME).click()

  def go_to_create_item(self):
    self.client.find_element(*NavBarLocators.LIST_ITEM).click()

  def go_to_browse_categories(self):
    self.client.find_element(*NavBarLocators.BROWSE_CATEGORIES).click()

  def go_to_notifications(self):
    self.client.find_element(*NavBarLocators.NOTIFICATIONS).click()

  def go_to_profile(self):
    user_dropdown = self.client.find_element(*NavBarLocators.USER_DROPDOWN)
    user_dropdown.click()
    self.client.find_element(*NavBarLocators.PROFILE).click()

  def go_to_log_out(self):
    user_dropdown = self.client.find_element(*NavBarLocators.USER_DROPDOWN)
    user_dropdown.click()
    self.client.find_element(*NavBarLocators.LOGOUT).click()

  def has_notifications(self):
    try:
      self.client.find_element(*NavBarLocators.NOTIFICATIONS_BADGE)
      return True
    except NoSuchElementException:
      return False


class HomePage(BasePage):

  def is_title_matches(self):
    super("TradyFit")

  def make_search(self, text):
    self.client.find_element(*HomePageLocators.SEARCH).send_keys(text)
    self.client.find_element(*HomePageLocators.SUBMIT).click()



class LoginPage(BasePage):

  def is_title_matches(self):
    super("Facebook Login")

  def login(self, user_email, user_pwd):
    self.client.find_element(*LoginPageLocators.EMAIL).send_keys(user_email)
    password_field = self.client.find_element(*LoginPageLocators.PASS)
    password_field.send_keys(user_pwd)
    password_field.submit()


class SearchPage(BasePage):

  def is_title_matches(self):
    super("TradyFit - Search Results")


class BrowsePage(BasePage):

  def is_title_matches(self):
    super("TradyFit - Browse categories")

  def go_to_item_page(self, item_name):
    self.client.find_element_by_link_text(item_name).click()


class ListItemPage(BasePage):

  def is_title_matches(self):
    super("TradyFit - List an item")

  def add_item(self, name, desc, price, category, image):
    self.client.find_element(*ListItemPageLocators.NAME).send_keys(name)
    self.client.find_element(*ListItemPageLocators.DESCRIPTION).send_keys(desc)
    price_element = self.client.find_element(*ListItemPageLocators.PRICE)
    #delete default value (0.00)
    price_element.clear()
    price_element.send_keys(price)
    #select item from dropdown list
    category_dropdown = self.client.find_element(*ListItemPageLocators.CATEGORY)
    category_list = Select(category_dropdown)
    category_list.select_by_visible_text(category)
    #add image to upload
    file_input = self.client.find_element(*ListItemPageLocators.IMAGE)
    file_input.send_keys(image)
    #submit the form
    self.client.find_element(*ListItemPageLocators.SUBMIT).click()


class ItemPage(BasePage):

  def is_title_matches(self):
    super("TradyFit - Item")

  def contact_seller(self):
    self.client.find_element(*ItemPageLocators.CONTACT).click()


class CreateMessagePage(BasePage):

  def is_title_matches(self):
    super("TradyFit - Send message")

  def send_message(self, desc):
    self.client.find_element(
                      *CreateMessagePageLocators.DESCRIPTION).send_keys(desc)
    #submit the form
    self.client.find_element(*CreateMessagePageLocators.SEND).click()


class MessagePage(BasePage):

  def is_title_matches(self):
    super("TradyFit - Message")

  def reply_message(self, desc):
    self.client.find_element(
                      *MessagePageLocators.DESCRIPTION).send_keys(desc)
    #submit
    self.client.find_element(*MessagePageLocators.SEND).click()



class NotificationsPage(BasePage):

  def is_title_matches(self):
    super("TradyFit - Notifications")

  def get_num_sent(self):
    return self.client.find_element(
                            *NotificationsPageLocators.SENT).text.strip()

  def get_num_unread(self):
    return self.client.find_element(
                            *NotificationsPageLocators.UNREAD).text.strip()

  def get_num_received(self):
    return self.client.find_element(
                            *NotificationsPageLocators.RECEIVED).text.strip()

  def go_to_unread_message(self, text):
    self.client.find_element_by_link_text(text).click()


class ProfilePage(BasePage):

  def is_title_matches():
    super("TradyFit - Profile")


