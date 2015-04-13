# -*- coding: utf-8 -*-
from flask import current_app
from base import UnitTestCase


class BasicsTestCase(UnitTestCase):

  def test_app_exists(self):
    self.assertFalse(current_app is None)

  def test_app_is_testing(self):
    self.assertTrue(current_app.config['TESTING'])