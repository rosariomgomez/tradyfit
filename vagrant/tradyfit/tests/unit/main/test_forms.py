import unittest
import re
import os
from bs4 import BeautifulSoup
from flask import current_app, url_for
from app import create_app, db
from app.models import Item, Category
from app.main.forms import ItemForm


class ItemFormTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Category.insert_categories()
        self.client = self.app.test_client()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def test_create_item_form(self):
        '''verify an item can be correctly created (happy case)'''
        c = Category.query.filter_by(name='soccer').one()
        form = ItemForm(data={
                            'name': 'soccer ball',
                            'description': 'plain ball',
                            'price': 234,
                            'category': c.id
                        })
        form.validate()
        self.assertTrue(not form.errors)


    def test_form_name_field(self):
        '''verify that name field only accepts the defined data types
        Test cases created following the category partition method
        Full list of TCs at main/specs/item_creation-spec.tsl
        Name: string(80), required, accept chars, numbers, dots and 
              underscores. Must start with a char
        '''
        c = Category.query.filter_by(name='soccer').one()

        #1. TC1: Empty name
        form = ItemForm(data={
                            'name': '',
                            'description': 'plain ball',
                            'price': 234,
                            'category': c.id
                        })
        form.validate()
        self.assertEqual(form.errors['name'], [u'This field is required.'])

        #2. TC2: Short (<3 chars)
        form = ItemForm(data={
                            'name': 'fo',
                            'description': 'plain ball',
                            'price': 234,
                            'category': c.id
                        })
        form.validate()
        self.assertEqual(form.errors['name'], [u'Field must be between 3 and' +
                                                ' 80 characters long.'])

        #3. TC3: Long (>80 chars)
        form = ItemForm(data={
                            'name': 'The Believers. The hidden story behind ' +
                                    'the code that runs our lives and control' +
                                    ' everything by Geoffrey Hinton',
                            'description': 'plain ball',
                            'price': 234,
                            'category': c.id
                        })
        form.validate()
        self.assertEqual(form.errors['name'], [u'Field must be between 3 and' +
                                                ' 80 characters long.'])

        #4. TC4: Special characters (accented, asian, EOL...)
        form = ItemForm(data={
                            'name': 'use your \n <b>say hi</b>',
                            'description': 'plain ball',
                            'price': 234,
                            'category': c.id
                        })
        form.validate()
        self.assertEqual(form.errors['name'],
        [u'Product names must have only letters, numbers, dots or underscores'])

        #5. TC5: Leading spaces
        form = ItemForm(data={
                            'name': ' baseball cup',
                            'description': 'plain ball',
                            'price': 234,
                            'category': c.id
                        })
        form.validate()
        self.assertEqual(form.errors['name'], 
        [u'Product names must have only letters, numbers, dots or underscores'])


    def test_form_description_field(self):
        '''verify that description field only accepts the defined data types
        Test cases created following the category partition method
        Full list of TCs at specs/item_creation-spec.tsl
        Description: Text area from 0 to 500 chars
        '''
        c = Category.query.filter_by(name='soccer').one()

        #1. TC8: Long (>500 chars)
        path = os.path.dirname(os.path.abspath(__file__))
        f = os.path.join(path,"sample_text.txt")
        with open(f, "r") as text:
            desc = text.readlines()

        form = ItemForm(data={
                            'name': 'soccer ball',
                            'description': desc[0],
                            'price': 234,
                            'category': c.id
                        })
        form.validate()
        self.assertEqual(form.errors['description'], [u'Field must be ' + 
                                    'between 0 and 500 characters long.'])


    def test_form_price_field(self):
        '''verify that price field only accepts the defined data types
        Test cases created following the category partition method
        Full list of TCs at specs/item_creation-spec.tsl
        Price: Decimal number. Precision 10, scale 2 (example: 123.34)
        '''
        c = Category.query.filter_by(name='soccer').one()

        #1. TC9: Chars
        form = ItemForm(data={
                            'name': 'baseball cup',
                            'description': 'plain ball',
                            'price': '23',
                            'category': c.id
                        })
        form.validate()
        self.assertEqual(form.errors['price'],
                                [u'Number must be between 0 and 9999999999.'])

        #2. TC10: Long decimal (>10 digits)
        form = ItemForm(data={
                            'name': 'baseball cup',
                            'description': 'plain ball',
                            'price': 100000000090.89,
                            'category': c.id
                        })
        form.validate()
        self.assertEqual(form.errors['price'], 
                                [u'Number must be between 0 and 9999999999.'])

        #3. TC11: Negative
        form = ItemForm(data={
                            'name': 'baseball cup',
                            'description': 'plain ball',
                            'price': -24.3,
                            'category': c.id
                        })
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
        form = ItemForm(data={
                            'name': 'baseball cup',
                            'description': 'plain ball',
                            'price': 24.3,
                            'category': '987'
                        })
        form.validate()
        self.assertEqual(form.errors['category'], [u'Not a valid choice'])

        #2. TC15: Empty category
        form = ItemForm(data={
                            'name': 'baseball cup',
                            'description': 'plain ball',
                            'price': 24.3,
                            'category': ''
                        })
        form.validate()
        self.assertEqual(form.errors['category'], [u'Not a valid choice'])

        #3. TC16: SQL injection
        form = ItemForm(data={
                            'name': 'baseball cup',
                            'description': 'plain ball',
                            'price': 24.3,
                            'category': "1' or '1' = '1"
                        })
        form.validate()
        self.assertEqual(form.errors['category'], [u'Not a valid choice'])

        













