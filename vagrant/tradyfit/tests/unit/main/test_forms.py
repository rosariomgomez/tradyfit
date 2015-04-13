# -*- coding: utf-8 -*-
import os
from werkzeug import FileStorage
from mock import Mock
from base import UnitTestCase
from app.models import Item, Category
from app.main.forms import ItemForm, SearchForm


LONG_TEXT = 'The Believers. The hidden story behind the code that runs our \
lives and control everything by Geoffrey Hinton'

def mock_file(filename):
  mock = Mock(spec=FileStorage())
  mock.filename = filename
  return mock

def create_item_form(name, description, price, category, image=None):
  return ItemForm(data={
                    'name': name,
                    'description': description,
                    'price': price,
                    'category': category,
                    'image': image
                    })


class ItemFormTestCase(UnitTestCase):

  def test_create_item_form(self):
    '''verify an item can be correctly created (happy case)'''
    c = Category.get_category(name='soccer')
    mock = mock_file('image.jpg')
    form = create_item_form('soccer ball', 'plain ball', 234, c.id, mock)
    form.validate()
    self.assertTrue(not form.errors)

  def test_form_name_field(self):
    '''verify that name field only accepts the defined data types
    Test cases created following the category partition method
    Full list of TCs at main/specs/item_creation-spec.tsl
    Name: string(3, 80), required, accept chars, numbers, dots, dashes and
          underscores. Must start with a char
    '''
    c = Category.get_category(name='soccer')

    #1. TC1: Empty name
    form = create_item_form('', 'plain ball', 234, c.id)
    form.validate()
    self.assertEqual(form.errors['name'], [u'This field is required.'])

    #2. TC2: Short (<3 chars)
    form = create_item_form('fo', 'plain ball', 234, c.id)
    form.validate()
    self.assertEqual(form.errors['name'], [u'Field must be between 3 and' +
                                            ' 80 characters long.'])

    #3. TC3: Long (>80 chars)
    form = create_item_form(LONG_TEXT, 'plain ball', 234, c.id)
    form.validate()
    self.assertEqual(form.errors['name'], [u'Field must be between 3 and' +
                                            ' 80 characters long.'])

    #4. TC4: Special characters (accented, asian, EOL...)
    form = create_item_form('use your \n <b>say hi</b>', 'a ball', 234, c.id)
    form.validate()
    self.assertEqual(form.errors['name'],
    ['Product names must have only letters, numbers, dots, dashes or ' +
    'underscores'])

    #5. TC5: Leading spaces
    form = create_item_form(' ball', 'plain ball', 234, c.id)
    form.validate()
    self.assertEqual(form.errors['name'],
    ['Product names must have only letters, numbers, dots, dashes or ' +
    'underscores'])


  def test_form_description_field(self):
    '''verify that description field only accepts the defined data types
    Test cases created following the category partition method
    Full list of TCs at specs/item_creation-spec.tsl
    Description: Text area from 0 to 500 chars
    '''
    c = Category.get_category(name='soccer')

    #1. TC8: Long (>500 chars)
    path = os.path.dirname(os.path.abspath(__file__))
    f = os.path.join(path,"sample_text.txt")
    with open(f, "r") as text:
        desc = text.readlines()

    form = create_item_form('soccer ball', desc[0], 234, c.id)
    form.validate()
    self.assertEqual(form.errors['description'], [u'Field must be ' +
                                'between 0 and 500 characters long.'])


  def test_form_price_field(self):
    '''verify that price field only accepts the defined data types
    Test cases created following the category partition method
    Full list of TCs at specs/item_creation-spec.tsl
    Price: Decimal number. Precision 10, scale 2 (example: 123.34)
    '''
    c = Category.get_category(name='soccer')

    #1. TC9: Chars
    form = create_item_form('soccer ball', 'plain ball', '234', c.id)
    form.validate()
    self.assertEqual(form.errors['price'],
                            [u'Number must be between 0 and 9999999999.'])

    #2. TC10: Long decimal (>10 digits)
    form = create_item_form('soccer ball', 'plain ball', 100000000090.89, c.id)
    form.validate()
    self.assertEqual(form.errors['price'],
                            [u'Number must be between 0 and 9999999999.'])

    #3. TC11: Negative
    form = create_item_form('soccer ball', 'plain ball', -24.3, c.id)
    form.validate()
    self.assertEqual(form.errors['price'],
                            [u'Number must be between 0 and 9999999999.'])


  def test_form_category_field(self):
    '''verify that category field only accepts the defined data types
    Test cases created following the category partition method
    Full list of TCs at specs/item_creation-spec.tsl
    Category: Integer. Id of an existent category
    '''
    #1. TC14: Non existent category
    form = create_item_form('soccer ball', 'plain ball', 24.3, '987')
    form.validate()
    self.assertEqual(form.errors['category'], [u'Not a valid choice'])

    #2. TC15: Empty category
    form = create_item_form('soccer ball', 'plain ball', 24.3, '')
    form.validate()
    self.assertEqual(form.errors['category'], [u'Not a valid choice'])

    #3. TC16: SQL injection
    form = create_item_form('soccer ball', 'plain ball', 24.3, "1' or '1' = '1")
    form.validate()
    self.assertEqual(form.errors['category'], [u'Not a valid choice'])


  def test_form_image_field(self):
    '''verify that image field only accepts the defined data types
    Test cases created following the category partition method
    Full list of TCs at main/specs/item_creation-spec.tsl
    Image: FileStorage type, not required, max size 3MB,
          allowed types: jpg, jpeg, png and gif
    '''
    c = Category.get_category(name='soccer')

    #1. TC1: Not provided
    form = create_item_form('soccer ball', 'plain ball', 24.3, c.id)
    form.validate()
    self.assertTrue(not form.errors)

    #2. TC2: Not FileStorage type provided
    form = create_item_form('soccer ball', 'plain ball', 24.3, '987', 'string')
    form.validate()
    self.assertEqual(form.errors['image'], [u'Image should be a file'])

    #3. TC4: Not allowed file type
    mock = mock_file('image.pdf')
    form = create_item_form('soccer ball', 'plain ball', 24.3, c.id, mock)
    form.validate()
    self.assertEqual(form.errors['image'],
      [u'Only jpg, png and gif files allowed'])


class SearchFormTestCase(UnitTestCase):
  def test_search_form(self):
    '''verify a search can be correctly executed (happy case)'''
    form = SearchForm(data={'search': 't-shirt'})
    form.validate()
    self.assertTrue(not form.errors)

  def test_form_search_field(self):
    '''verify that search field only accepts the defined data types
    Search: string(3, 80), required, accept chars, numbers, dots, dashes and
            underscores. Must start with a char
    '''
    #1. XSS injection
    form = SearchForm(data={'search': "<script>alert('XSS')</script>"})
    form.validate()
    self.assertEqual(form.errors['search'],
    [u'Search must have only letters, numbers, dots, dashes or underscores'])

    #2. Chars (>80)
    form = SearchForm(data={'search': LONG_TEXT})
    form.validate()
    self.assertEqual(form.errors['search'], [u'Field must be between 3 and' +
                                            ' 80 characters long.'])


