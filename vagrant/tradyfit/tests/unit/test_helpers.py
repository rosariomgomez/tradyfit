# -*- coding: utf-8 -*-
import requests
import os
import boto
from mock import Mock, patch
from base import BasicTestCase
from app import helpers

class HelperTestCase(BasicTestCase):

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


class CommonHelperTestCase(HelperTestCase):
  '''common helper methods for upload/delete avatars and images'''

  def test_get_s3_bucket(self):
    '''verify the bucket is returned and non exception is raised'''
    mock_boto_conn = Mock()
    with patch.object(boto, 'connect_s3', mock_boto_conn):
      self.assertTrue(helpers.get_s3_bucket() is not None)

  def test_get_s3_bucket_exception(self):
    '''if the connection with s3 fails, an exception is returned'''
    mock_boto_conn = Mock(side_effect=Exception('boom!'))
    with patch.object(boto, 'connect_s3', mock_boto_conn):
      with self.assertRaises(Exception) as context:
        helpers.get_s3_bucket()
        self.assertTrue('connection refused' in context.exception)

  def test_upload_s3(self):
    '''verify True is returned if an image can be correctly uploaded
    when s3 connection works'''
    mock_get_s3_bucket = Mock()
    with patch.object(helpers, 'get_s3_bucket', mock_get_s3_bucket):
      self.assertTrue(helpers.upload_s3("S3_UPLOAD_AVATAR_DIR", 'file', 'data'))

  def test_upload_s3_fail(self):
    '''verify False is returned if an image cannot be uploaded'''
    mock_get_s3_bucket = Mock()
    with patch.object(helpers, 'get_s3_bucket', mock_get_s3_bucket):
      self.assertFalse(helpers.upload_s3('directory', 'file', 'data'))

  def test_delete_s3(self):
    '''verify True is returned if an image can be deleted'''
    mock_get_s3_bucket = Mock()
    with patch.object(helpers, 'get_s3_bucket', mock_get_s3_bucket):
      self.assertTrue(helpers.delete_s3("S3_UPLOAD_ITEM_DIR", 'file'))

  def test_delete_s3_fail(self):
    '''verify False is returned if an image can't be deleted'''
    mock_get_s3_bucket = Mock(side_effect=Exception('boom!'))
    with patch.object(helpers, 'get_s3_bucket', mock_get_s3_bucket):
      self.assertFalse(helpers.delete_s3("S3_UPLOAD_ITEM_DIR", 'file'))


class AvatarHelperTestCase(HelperTestCase):
  '''Test cases related with saving user avatar helper methods'''

  @patch('requests.get')
  def test_make_avatar_request(self, mock_get):
    '''test helpers.make_image_request with a legit url (aka local file)'''
    url = 'test_avatar.jpg'
    mock_response = Mock()
    mock_response.return_value = HelperTestCase.local_get(url)
    mock_response.content = HelperTestCase.local_content(
                                                  mock_response.return_value)
    # Assign our mock response as the result of our patched function
    mock_get.return_value = mock_response
    self.assertTrue(helpers.make_image_request(url) is not None)

  def test_make_avatar_request_bad_url(self):
    '''test helpers.make_image_request with a non legit url'''
    url = None
    self.assertTrue(helpers.make_image_request(url) is None)

  def test_save_avatar(self):
    '''test filename returned when an image is provided'''
    mock_image_req = Mock(return_value = 'fakeimagecontent')
    mock_upload_s3 = Mock(return_value = True)
    with patch.object(helpers, 'make_image_request', mock_image_req):
      with patch.object(helpers, 'upload_s3', mock_upload_s3):
        self.assertTrue(helpers.save_avatar('avatar.jpg') !=
                        self.app.config["DEFAULT_AVATAR"])

  def test_save_invalid_avatar(self):
    '''test default filename is returned when no image is provided'''
    mock_image_req = Mock(return_value=None)
    with patch.object(helpers, 'make_image_request', mock_image_req):
      self.assertTrue(helpers.save_avatar('something') ==
                      self.app.config["DEFAULT_AVATAR"])

  def test_save_avatar_problem(self):
    '''test default_avatar is returned if upload to s3 fails'''
    mock_image_req = Mock(return_value='fakeimagecontent')
    mock_upload_s3 = Mock(return_value=False)
    with patch.object(helpers, 'make_image_request', mock_image_req):
      with patch.object(helpers, 'upload_s3', mock_upload_s3):
        self.assertTrue(helpers.save_avatar('image.jpg') ==
                        self.app.config["DEFAULT_AVATAR"])

  def test_delete_avatar(self):
    '''verify True is returned if a files was deleted from s3'''
    mock_delete_s3 = Mock(return_value=True)
    with patch.object(helpers, 'delete_s3', mock_delete_s3):
      self.assertTrue(helpers.delete_avatar('image.jpg'))

  def test_delete_default_avatar(self):
    '''verify delete_s3 is not called and True is returned if default avatar
    file is provided to delete'''
    mock_delete_s3 = Mock()
    with patch.object(helpers, 'delete_s3', mock_delete_s3):
      self.assertTrue(helpers.delete_avatar(self.app.config["DEFAULT_AVATAR"]))
      self.assertFalse(mock_delete_s3.called)


class ItemImageHelperTestCase(HelperTestCase):
  '''Test cases related with saving item images helper methods'''

  def test_save_item_image(self):
    '''verify a filename with the same extension of the input file is
    returned if it was stored in s3'''
    mock_source_file = Mock()
    mock_file = Mock(filename='image.jpg')
    mock_source_file.data = mock_file
    mock_upload_s3 = Mock(return_value=True)
    with patch.object(helpers, 'upload_s3', mock_upload_s3):
      self.assertTrue(helpers.save_item_image(mock_source_file).endswith('jpg'))

  def test_save_item_no_image_provided(self):
    '''verify default item image is provided if not source_file passed'''
    self.assertTrue(helpers.save_item_image(None) ==
                    self.app.config["DEFAULT_ITEM"])

  def test_save_item_image_s3_problem(self):
    '''verify None is returned if image was not stored in s3'''
    mock_source_file = Mock()
    mock_file = Mock(filename='image.jpg')
    mock_source_file.data = mock_file
    mock_upload_s3 = Mock(return_value=False)
    with patch.object(helpers, 'upload_s3', mock_upload_s3):
      self.assertTrue(helpers.save_item_image(mock_source_file) is None)

  def test_delete_item_image(self):
    '''verify True is returned if a files was deleted from s3'''
    mock_delete_s3 = Mock(return_value=True)
    with patch.object(helpers, 'delete_s3', mock_delete_s3):
      self.assertTrue(helpers.delete_item_image('image.jpg'))

  def test_delete_item_default_image(self):
    '''verify delete_s3 is not called and True is returned if default item
    file is provided to delete'''
    mock_delete_s3 = Mock()
    with patch.object(helpers, 'delete_s3', mock_delete_s3):
      self.assertTrue(
              helpers.delete_item_image(self.app.config["DEFAULT_ITEM"]))
      self.assertFalse(mock_delete_s3.called)
