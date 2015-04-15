# -*- coding: utf-8 -*-
import os
from base import UnitTestCase
from app.msg.forms import MessageForm

LONG_TEXT = 'The Believers. The hidden story behind the code that runs our \
lives and control everything. Geoffrey Hinton. A believer. A brusque coder \
who had to hide his ideas in obscure language to get them past peer review. \
A guru of the artificial neural network.'

class MessageFormTestCase(UnitTestCase):
  def test_message_form(self):
    '''verify a the form validates with valid inputs'''
    form = MessageForm(data={'subject': 'Hi there!', 'description': 'Nice'})
    form.validate()
    self.assertTrue(not form.errors)

  def test_form_subject_field(self):
    '''verify that subject field only accepts the defined data types'''

    #1. TC1: Empty subject
    form = MessageForm(data={'subject': '', 'description': 'Nice'})
    form.validate()
    self.assertEqual(form.errors['subject'], ['This field is required.'])

    #2. TC2: Short (<2 chars)
    form = MessageForm(data={'subject': 'f', 'description': 'Nice'})
    form.validate()
    self.assertEqual(form.errors['subject'], ['Field must be between 2 and' +
                                            ' 120 characters long.'])

    #3. TC3: Long (>120 chars)
    form = MessageForm(data={'subject': LONG_TEXT, 'description': 'Nice'})
    form.validate()
    self.assertEqual(form.errors['subject'], ['Field must be between 2 and' +
                                            ' 120 characters long.'])

  def test_form_description_field(self):
    '''verify that description field only accepts the defined data types'''

    #1. TC1: Long (>500 chars)
    path = os.path.dirname(os.path.abspath(__file__))
    f = os.path.join(path,"sample_text.txt")
    with open(f, "r") as text:
        desc = text.readlines()

    form = MessageForm(data={'subject': 'hi', 'description': desc[0]})
    form.validate()
    self.assertEqual(form.errors['description'], [u'Field must be ' +
                                'between 0 and 500 characters long.'])
