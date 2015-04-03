# -*- coding: utf-8 -*-
import unittest
import requests
import os
import boto
from mock import Mock, PropertyMock, patch
from app import create_app
from app.main import helpers

class HelperTestCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()

  def tearDown(self):
    self.app_context.pop()

  @staticmethod
  def local_get(url):
    '''mock requests.get: get local path to a file'''
    path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(path,url)
    return image_path

  @staticmethod
  def local_content(image_path):
    '''mock content of request: fetch a resource from a local file'''
    image = None
    try:
      with open(image_path, 'r') as f:
        image = f.read()
      return str(image)
    except:
      return image

  @patch('requests.get')
  def test_make_image_request(self, mock_get):
    '''test helpers.make_image_request with a legit url (aka local file)'''
    url = 'test_avatar.jpg'
    mock_response = Mock()
    mock_response.return_value = HelperTestCase.local_get(url)
    mock_response.content = HelperTestCase.local_content(
                                                  mock_response.return_value)
    # Assign our mock response as the result of our patched function
    mock_get.return_value = mock_response
    self.assertTrue(helpers.make_image_request(url) is not None)

  def test_make_image_request_bad_url(self):
    '''test helpers.make_image_request with a non legit url'''
    url = None
    self.assertTrue(helpers.make_image_request(url) is None)

  @patch('boto.connect_s3')
  def test_save_avatar(self, mock_boto_conn):
    '''test filename returned when an image is provided'''
    mock_image_req = Mock(return_value = 'fakeimagecontent')
    mock_boto = Mock()
    with patch.object(helpers, 'make_image_request', mock_image_req):
      self.assertTrue(
        helpers.save_avatar('avatar.jpg') is not 'default_avatar.jpg')

  def test_save_invalid_avatar(self):
    '''test default filename is returned when no image is provided'''
    mock_image_req = Mock(return_value=None)
    with patch.object(helpers, 'make_image_request', mock_image_req):
      self.assertTrue(helpers.save_avatar('something') == 'default_avatar.jpg')

  def test_invalid_connection(self):
    '''test default_avatar is returned if connection raise an error'''
    mock_image_req = Mock(return_value = 'fakeimagecontent')
    mock_boto_conn = Mock(side_effect=Exception('Boom!'))
    with patch.object(helpers, 'make_image_request', mock_image_req):
      with patch.object(boto, 'connect_s3', mock_boto_conn):
        self.assertTrue(helpers.save_avatar('image.jpg') == 'default_avatar.jpg')

