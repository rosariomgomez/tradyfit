# -*- coding: utf-8 -*-
import unittest
from mock import Mock, PropertyMock, patch
from flask import current_app, url_for, session
from flask_oauthlib.client import OAuthException
from app import create_app, db
from app.models import User
from app.auth.views import facebook
from app.main import helpers
from datetime import datetime, timedelta
from uuid import uuid4


class AuthViewTestCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()
    self.client = self.app.test_client(use_cookies=True)

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()


class BeforeRequestTestCase(AuthViewTestCase):
  '''Testing: @auth.route('/before_request')'''

  def test_update_last_seen(self):
    '''verify last_seen is updated properly every 15min
    1. Create a user
    2. Log in user and modify last_seen value
    3. Request index view
    4. Assert that last_seen user attribute has been updated
    '''
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john', avatar_url=uuid4().hex + '.jpg')
    db.session.add(u)
    db.session.commit()
    before_last_seen = u.last_seen
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['last_seen'] = datetime.utcnow() - timedelta(minutes=30)
        sess['_fresh'] = True
      response = c.get(url_for('main.index'))
      self.assertTrue(u.last_seen > before_last_seen)


class FBLoginTestCase(AuthViewTestCase):
  '''Testing: @auth.route('/fb-login/authorized')'''

  @staticmethod
  def mock_facebook_auth():
    '''mock Facebook authentication'''
    mock_fb_resp = Mock()
    mock_fb_resp.return_value = {
      'access_token': 'dummy_token',
      'expires': '5183883'
    }
    return mock_fb_resp

  @staticmethod
  def mock_facebook_info():
    '''mock Facebook user information call'''
    mock_fb_info = Mock()
    type(mock_fb_info.return_value).data = PropertyMock(
                              return_value= { 'id': '12908098',
                                              'email': 'john@testing.com',
                                              'name': 'John Doe',
                                              'gender': 'male',
                                              'data': {
                                                'url': 'http://test-image.png' }
                                            })
    return mock_fb_info

  @staticmethod
  def mock_facebook_error_info():
    '''mock Facebook user information call returning an error'''
    mock_fb_info = Mock()
    type(mock_fb_info.return_value).data = PropertyMock(
                              return_value= { 'error': 'User not found'})
    return mock_fb_info


  def test_login_user_fb_auth(self):
    '''verify a new user is created when login with FB for the first time
    1. Create mock objects
    2. Verfiy user does not exist in the DB
    3. Call the login method
    4. Verify the user has been created and it is redirected to index'''

    mock_fb_resp = FBLoginTestCase.mock_facebook_auth()
    mock_fb_info = FBLoginTestCase.mock_facebook_info()

    mock_save_avatar = Mock(name='save_avatar')
    mock_save_avatar.return_value = 'testimage.jpg'

    self.assertTrue(User.get_user('john@testing.com') is None)

    with patch.object(facebook, 'authorized_response', mock_fb_resp):
      with patch.object(facebook, 'get', mock_fb_info):
        with patch.object(helpers, 'save_avatar', mock_save_avatar):
          resp = self.client.get(url_for('auth.facebook_authorized'),
                                  follow_redirects=True)
          self.assertTrue(isinstance(User.get_user('john@testing.com'), User))
          self.assertTrue('john' in resp.get_data(as_text=True))

  def test_already_login_user_fb_auth(self):
    '''if user is already authenticated verify it is redirected
    to index
    1. Create a user
    2. Log in user by adding it to session
    3. Request fb-login view
    4. Assert user is redirected to index
    '''
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john', avatar_url=uuid4().hex + '.jpg')
    db.session.add(u)
    db.session.commit()
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True
      response = c.get(url_for('auth.fb_login'),follow_redirects=True)
      self.assertTrue('Welcome to TradyFit' in response.get_data(as_text=True))

  def test_user_denied_login(self):
    '''user denied login with FB'''
    mock_fb_resp = Mock(return_value=None)
    with patch.object(facebook, 'authorized_response', mock_fb_resp):
      resp = self.client.get(url_for('auth.facebook_authorized'),
                              follow_redirects=True)
      content = resp.get_data(as_text=True)
      self.assertTrue('Log In with Facebook' in content)
      self.assertTrue('You denied the request to sign in.' in content)

  def test_oauth_login_exception(self):
    '''An exception has been raised from FB login API call'''
    mock_fb_resp = Mock(return_value=OAuthException('error'))
    with patch.object(facebook, 'authorized_response', mock_fb_resp):
      resp = self.client.get(url_for('auth.facebook_authorized'),
                              follow_redirects=True)
      content = resp.get_data(as_text=True)
      self.assertTrue('Log In with Facebook' in content)
      self.assertTrue('Something went wrong, please try to sign in later.' in
                      content)

  def test_user_info_error(self):
    '''FB returns an error when asking for user's information'''
    mock_fb_resp = FBLoginTestCase.mock_facebook_auth()
    mock_fb_info = FBLoginTestCase.mock_facebook_error_info()

    with patch.object(facebook, 'authorized_response', mock_fb_resp):
      with patch.object(facebook, 'get', mock_fb_info):
        resp = self.client.get(url_for('auth.facebook_authorized'),
                              follow_redirects=True)
        content = resp.get_data(as_text=True)
        self.assertTrue('Log In with Facebook' in content)
        self.assertTrue('Something went wrong, please try to sign in later.' in
                      content)


class LogoutTestCase(AuthViewTestCase):
  '''Testing: @auth.route('/logout')'''

  def test_fb_cookies_removed(self):
    u = User(fb_id='23', email='john@example.com', name='John Doe',
            username='john')
    db.session.add(u)
    db.session.commit()
    with self.client as c:
      with c.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['fb_oauth'] = ('fake_token', '')
        sess['_fresh'] = True
      response = c.get(url_for('auth.logout'),follow_redirects=True)
      self.assertTrue('fb_oauth' not in session)
      self.assertTrue('Log In with Facebook' in response.get_data(as_text=True))
