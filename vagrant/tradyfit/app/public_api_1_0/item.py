# -*- coding: utf-8 -*-
import re
from flask import jsonify, request, url_for
from ..models import Category, Item
from . import public_api
from .errors import bad_request

MIN_QUERY = 3
MAX_QUERY = 80

def valid_query(query):
  '''query should be between (3,80) start with letter or numbers and only 
  include letters, numbers, spaces, "." or "-" '''
  return MIN_QUERY < len(query) < MAX_QUERY and \
          bool(re.match("^[A-Za-z0-9][.\- \w]+$", query))


@public_api.route('/items/category/<category>')
def get_items_category(category):
  category = Category.query.filter_by(name=category).first_or_404()
  items = Item.query.filter_by(category_id = category.id).order_by(
                  Item.timestamp.desc()).all()
  return jsonify(items=[item.serialize for item in items])


@public_api.route('/items/search/<query>')
def get_items_search(query):
  '''return items containing the query text on name or description'''
  if valid_query(query):
    items = Item.query.search(query).order_by(
                    Item.timestamp.desc()).all()
    return jsonify(items=[item.serialize for item in items])
  else:
    return bad_request('Not a valid search')
