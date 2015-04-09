from selenium.webdriver.support.select import Select
from locators import NavBarLocators, LoginPageLocators, ListItemPageLocators

class BasePage(object):

  def __init__(self, client):
    self.client = client

  def is_title_matches(self, title):
    return title in self.client.title

class HomePage(BasePage):

  def is_title_matches(self):
    super("TradyFit")

  def go_to_login(self):
    self.client.find_element(*NavBarLocators.LOGIN).click()


class LoginPage(BasePage):

  def is_title_matches(self):
    super("Facebook Login")

  def login(self, user_email, user_pwd):
    self.client.find_element(*LoginPageLocators.EMAIL).send_keys(user_email)
    password_field = self.client.find_element(*LoginPageLocators.PASS)
    password_field.send_keys(user_pwd)
    password_field.submit()

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