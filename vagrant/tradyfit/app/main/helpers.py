import requests
from uuid import uuid4
import boto
from flask import current_app


def make_image_request(url):
  '''Request and download image content'''
  try:
    req = requests.get(url)
    return req.content
  except:
    return None


def save_avatar(avatar):
  '''store user's profile picture and return the file name
     Input: avatar: (str) avatar url
     Output: filename or default_avatar if something fails
  '''
  image = make_image_request(avatar)

  if image:
    #generate a unique random filename
    filename = uuid4().hex + '.jpg'

    # Connect to S3 and upload file
    try:
      conn = boto.connect_s3(current_app.config["S3_KEY"],
          current_app.config["S3_SECRET"])
      b = conn.get_bucket(current_app.config["S3_BUCKET"])

      sml = b.new_key("/".join(
          [current_app.config["S3_UPLOAD_AVATAR_DIR"],
          filename]))
      sml.set_contents_from_string(image)
      sml.set_acl('public-read')
      return filename
    except:
      print('boto connection not working')
      return 'default_avatar.jpg'
  else:
    return 'default_avatar.jpg'