# -*- coding: utf-8 -*-
import unittest
from app import create_app, db


class BasicTestCase(unittest.TestCase):

  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()

  def tearDown(self):
    self.app_context.pop()


class UnitTestCase(BasicTestCase):

  def setUp(self):
    super(UnitTestCase, self).setUp()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    super(UnitTestCase, self).tearDown()