# -*- coding: utf-8 -*-
from flask import jsonify, request, url_for
from ..models import Category, Item
from . import public_api


@public_api.route('/items/category/<category>')
def get_items_category(category):
  category = Category.query.filter_by(name=category).first_or_404()
  items = Item.query.filter_by(category_id = category.id).order_by(
                  Item.timestamp.desc()).all()
  return jsonify(items=[item.serialize for item in items])
