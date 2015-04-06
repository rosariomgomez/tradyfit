from locators import NavBarLocators, LoginPageLocators

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

class ItemPage(BasePage):

  def is_title_matches(self):
    super("TradyFit - Item")