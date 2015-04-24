# -*- coding: utf-8 -*-
from flask import url_for
from base import ClientTestCase
import app.main.views


class IndexIntegrationTestCase(ClientTestCase):

  def test_search_form_redirect(self):
    '''verify the search form redirects to results when submit'''
    resp = self.client.post(url_for('main.index'),
                            data={
                                'search': 'soccer ball',
                            }, follow_redirects=True)
    self.assertTrue(b'Search results for "soccer ball":' in resp.data)
