# -*- coding: utf-8 -*-
import unittest
from app import create_app, db
from app.models import Category


class CategoryModelTestCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def test_insert_categories(self):
    categories = Category.query.all()
    self.assertEqual(categories, [])
    Category.insert_categories()
    c = Category.query.filter_by(name='soccer').one()
    self.assertEqual(c.name, 'soccer')