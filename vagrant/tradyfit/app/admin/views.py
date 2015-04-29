# -*- coding: utf-8 -*-
from flask import render_template
from . import admin
from .decorators import admin_required
from ..models import User, Item


@admin.route('/')
@admin_required
def index():
  users = User.query.order_by(User.last_seen.desc()).all()
  return render_template('admin/index.html', users=users)


@admin.route('/items')
@admin_required
def items():
  items = Item.query.order_by(Item.modified.desc()).all()
  return render_template('admin/items.html', items=items)
