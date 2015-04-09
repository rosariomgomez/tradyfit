import requests
from uuid import uuid4
import boto
from boto.s3.key import Key
from flask import current_app
from werkzeug import secure_filename


def make_image_request(url):
  '''Request and download image content'''
  try:
    req = requests.get(url)
    return req.content
  except:
    return None


def get_s3_bucket():
  '''connect to S3 and return the S3 bucket'''
  try:
    # Connect to S3
    conn = boto.connect_s3(current_app.config["S3_KEY"],
        current_app.config["S3_SECRET"])
    return conn.get_bucket(current_app.config["S3_BUCKET"])
  except:
    raise Exception('connection refused')


def upload_s3(s3_directory, filename, data):
  '''upload file to s3'''
  try:
    b = get_s3_bucket()

    # Upload the File
    sml = b.new_key("/".join([current_app.config[s3_directory], filename]))
    sml.set_contents_from_string(data)

    # Set the file's permissions
    sml.set_acl('public-read')
    return True
  except:
    return False


def delete_item_image(filename):
  '''delete item image from S3 if it is not the DEFAULT_ITEM image'''
  if filename != current_app.config["DEFAULT_ITEM"]:
    try:
      b = get_s3_bucket()
      #file route key
      k = b.get_key("/".join(
            [current_app.config["S3_UPLOAD_ITEM_DIR"], filename]))
      #delete the file
      k.delete()
      return True
    except:
      return False
  return True


def save_avatar(avatar):
  '''store user's profile picture and return the file name
     Input: avatar: (str) avatar url
     Output: filename or DEFAULT_AVATAR if something fails
  '''
  image = make_image_request(avatar)

  if image:
    #generate a unique random filename
    filename = uuid4().hex + '.jpg'

    if upload_s3("S3_UPLOAD_AVATAR_DIR", filename, image):
      return filename
    else:
      return current_app.config["DEFAULT_AVATAR"]

  else:
    return current_app.config["DEFAULT_AVATAR"]


def save_item_image(source_file):
  '''store item image and return the file name
     Input: source_file: (FileField)  File Storage object
     Output: (str) filename, (str) DEFAULT_ITEM if not provided,
              None if something fails
  '''
  if source_file:
    source_filename = secure_filename(source_file.data.filename)
    source_extension = source_filename.split('.', 1)[-1]

    dest_filename = uuid4().hex + '.' + source_extension

    if upload_s3("S3_UPLOAD_ITEM_DIR", dest_filename, source_file.data.read()):
      return dest_filename
    else:
      return None

  else:
    return current_app.config["DEFAULT_ITEM"]

