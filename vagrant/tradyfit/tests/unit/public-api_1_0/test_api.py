# -*- coding: utf-8 -*-
import json
from flask import url_for
from base import ClientTestCase


class APITestCase(ClientTestCase):
  
  def get_api_headers(self):
    return {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }

  def test_404(self):
    response = self.client.get('/wrong/url',
        headers=self.get_api_headers())
    self.assertTrue(response.status_code == 404)
    json_response = json.loads(response.data.decode('utf-8'))
    self.assertTrue(json_response['error'] == 'not found')

