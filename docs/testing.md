# Testing strategy

This section contains all the information about the tools, packages and strategy followed for testing the application.

## Behavior Driven Development
The idea of following BDD is to focus the test suite on the behavior of the application as a whole.
Writing first a test describing the feature's functionality before coding it, helps to understand on a higher level what are the expectations from a user point of view.

![BDD cycle](img/bdd_cycle.jpg)

- I chose to write the acceptance tests at a browser level. For doing this I created a testing framework by using the [Selenium WebDriver API](http://selenium.googlecode.com/git/docs/api/py/api.html) in conjunction with the unittest library.
- After writing the acceptance test, I write the integration/unit test to test the code at a granular level.  
__Note:__ In the future, I'm planning to include the [behave](https://pythonhosted.org/behave) testing framework to write the __feature behaviors__ making use of the Gherkin Syntax (Scenario: Given-When-Then), and finally link those behaviors a __steps file__ where the acceptance test is written.

## Unit tests
Test methods in isolation. Mock any external call to other methods.

__Some notes on making mocks work:__  
- When mocking an imported method inside the function in test, we must ensure that we patch the name used by the system under test. __The basic principle is that you patch where an object is looked up, which is not necessarily the same place as where it is defined.__ There are two scenarios:   

- When the import is common:  

    In the ``facebook_authorized()`` method from the view ``app/auth/views.py``, there's a call to the method ``helpers.save_avatar()``. The import is made by calling ``from app.main import helpers``.  
    Then, in the test function ``test_login_user_fb_auth(self)`` inside the file ``tests/unit/auth/test_auth_views.py``, the import is made in the same way and we can patch the save_avatar method by doing: ``with patch.object(helpers, 'save_avatar', mock_save_avatar)``  

  
- When there is already a reference to the method we want to patch:  

    In the ``create()`` method from the view ``app/main/views.py``, there's a call to the method ``save_item_image()``. The import is made by calling ``from .helpers import save_item_image``.  
    Then, in the test function we need to make the import of the view where we have the method we want to test and patch the call to save_item_image by writing ``@patch('app.main.views.save_item_image'):``  

- To ensure a mock is being called, you can make use of the built in instance method from the Mock class ``assert_called_with()``. Example: ``mock_save_avatar.assert_called_with('http://test-image.png')``  
  
- More info in the [patch documentation](http://mock.readthedocs.org/en/latest/patch.html#where-to-patch).  


<h3> Continuous integration with drone.io</h3>
Any new changes to my source code (every time I push code to Github) will trigger a build. It creates a new virtual machine with the set up specified: environment variables, databases and the build commands, and then it runs the tests (unit and integration).

- [Builds history](https://drone.io/github.com/rosariomgomez/tradyfit)

## Integration tests  
Test feature functionality without browser interaction.

## Acceptance tests
Test feature functionality with browser interaction by using Selenium Webdriver with unittest framework.  
In order to not DRY, I created the following files:  
- ```functional/helper.py``` contains the necessary code to connect with the RemoteWebdriver server and launch our application in a thread.  
- ```functional/page.py``` defines page objects. A page object represents an area in the web application UI that the test is interacting with (home page, item page...).  
- ```functional/locators.py``` define all the elements (and their locators) that the tests will be interacting with, so if we change the locator of an element, this is the only place where the change is needed.  

__Some notes:__  
  - Try to use id (#) and class (.) attributes for locators whenever is possible  
  - Use explicit waits to meet all browser requirements

<h3>Running the tests in the cloud with Sauce Labs</h3>

## Notes
__Mocking:__  
- In order to unit test form validation for file uploading, I had to mock a file, by using the specifications from the FileStorage class. That was the only way I was able to pass the FileRequired validation (``test_create_item_form``)  

__Remove connection on tearDown:__  

If the connection is not removed, it stays idle. After running several tests (the error occurs to me when adding the 117 test case), sqlalchemy is using all the connections and an Operational error occur.  
I solved it by adding: ``db.get_engine(self.app).dispose()``  
Found solution [here](http://stackoverflow.com/questions/18291180/flask-unittest-and-sqlalchemy-using-all-connections)  
I confirmed it by checking the process running during test execution, and found several open connections in idle status:  
``ps aux | grep tradyfit_test``  
``postgres 31101  [..]  postgres: vagrant tradyfit_test [local] idle``