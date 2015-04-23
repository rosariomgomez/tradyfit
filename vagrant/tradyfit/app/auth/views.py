from flask import flash, request, redirect, url_for, session
from flask_oauthlib.client import OAuth, OAuthException
from flask.ext.login import login_user, logout_user, current_user, \
login_required
from datetime import datetime, timedelta
from app.models import User
from app import helpers
from .. import db
from . import auth


@auth.before_app_request
def before_request():
  '''executes in each request and updates last_seen user field
  every 15 minutes (and location information from IP the first time)'''
  if current_user.is_authenticated():
    if session.get('last_seen'):
      if session.get('last_seen') < datetime.utcnow() - timedelta(minutes=15):
        session['last_seen'] = datetime.utcnow()
        current_user.ping()
    else:
      session['last_seen'] = datetime.utcnow()
      current_user.ping()
      ip = get_ip() #extract geolocation info from the user ip
      current_user.location(ip)


oauth = OAuth()

# Facebook login
facebook = oauth.remote_app(
  'facebook',
  app_key='FACEBOOK'
)

@facebook.tokengetter
def get_facebook_oauth_token():
  if current_user.is_authenticated():
    return (current_user.token, current_user.secret)
  else:
    return session.get('fb_oauth')

@auth.route('/fb-login')
def fb_login():
  '''send user to facebook authentication if user is not already
  authenticated in'''
  if current_user.is_authenticated():
    return redirect(url_for('main.index'))
  else:
    callback = url_for('auth.facebook_authorized',
      next=request.args.get('next') or request.referrer or None,
      _external=True
    )
    return facebook.authorize(callback=callback)

@auth.route('/fb-login/authorized')
def facebook_authorized():
  '''verify that user has been fb authenticated,
  retrieve user info from facebook,
  retrieve or create user from db and log user in
  '''
  resp = facebook.authorized_response()
  if resp is None:
    flash('You denied the request to sign in.')
    return redirect(url_for('main.index'))
  if isinstance(resp, OAuthException):
    flash('Something went wrong, please try to sign in later.')
    return redirect(url_for('main.index'))

  session['fb_oauth'] = (resp['access_token'], '')
  uinfo = facebook.get('/me')

  if "error" in uinfo.data.keys():
    flash('Something went wrong, please try to sign in later.')
    return redirect(url_for('main.index'))
  else:
    user = User.get_user(uinfo.data['email'])
    if not user:
      #create unique username from email
      username = User.create_username(uinfo.data['email'].split('@')[0])

      #request facebook user avatar
      uavatar = facebook.get('/me/picture?redirect=0&type=large')
      #save image in s3
      filename = helpers.save_avatar(uavatar.data['data']['url'])

      #check if gender is provided
      gender = 'unknown'
      if 'gender' in uinfo.data:
        gender = uinfo.data['gender']

      #create user and add it to database
      user = User(fb_id=uinfo.data['id'], gender=gender,
                  email=uinfo.data['email'],
                  name=uinfo.data['name'], username=username,
                  avatar_url=filename)
      db.session.add(user)
      db.session.commit()

    login_user(user)
    return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
  '''remove added values to the session cookie and log out'''
  session.pop('fb_oauth', None)
  logout_user()
  return redirect(url_for('main.index'))


def get_ip():
  '''Return user IP: If a forwarded header exists the access_route
  contains a list of all ip addresses from the client ip to the last
  proxy server (this method must be created where a request context exist)'''
  try:
    ip_list = request.access_route
    if type(ip_list) == list:
      return ip_list[0]
    return None
  except ValueError:
    return None
