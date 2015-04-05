# -*- coding: utf-8 -*-
from datetime import datetime
from flask import current_app, render_template, flash, redirect, url_for, \
request, abort
from flask.ext.login import current_user, login_required
from . import main
from .. import db
from .forms import ItemForm, SearchForm
from ..models import Item, Category


@main.route('/shutdown')
def server_shutdown():
  '''HTTP request to shutdown Werkzeug server running in a background thread
  during functional tests running with Selenium'''
  if not current_app.testing:
    abort(404)
  shutdown = request.environ.get('werkzeug.server.shutdown')
  if not shutdown:
    abort(500)
  shutdown()
  return 'Shutting down...'

@main.route('/', methods=['GET', 'POST'])
def index():
  search_form = SearchForm()
  if search_form.validate_on_submit():
    return redirect(url_for('main.search_results',
                            query=search_form.search.data))
  items = Item.query.order_by(Item.timestamp.desc()).all()
  return render_template('index.html', form=search_form, items=items)

@main.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
  form = ItemForm()
  if form.validate_on_submit():
    category = Category.query.get(form.category.data)
    item = Item(name=form.name.data, description=form.description.data,
                price=form.price.data, category=category,
                user_id=current_user.id)
    db.session.add(item)
    flash('Your item has been created.')
    return redirect(url_for('main.index'))
  return render_template('create.html', form=form)

@main.route('/item/<int:id>')
def item(id):
  item = Item.query.get_or_404(id)
  return render_template('item.html', item=item)

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
  item = Item.query.get_or_404(id)
  if current_user != item.user:
    return redirect(url_for('main.index'))

  form = ItemForm()
  if form.validate_on_submit():
    item.name = form.name.data
    item.description = form.description.data
    item.price = form.price.data
    item.category = Category.query.get(form.category.data)
    item.modified = datetime.utcnow()
    db.session.add(item)
    flash('Your item has been updated.')
    return redirect(url_for('main.item', id=item.id))
  form.name.data = item.name
  form.description.data = item.description
  form.price.data = item.price
  form.category.data = item.category.id
  return render_template('edit_item.html', form=form, id=item.id)

@main.route('/delete/<int:id>')
@login_required
def delete(id):
  item = Item.query.get_or_404(id)
  if current_user != item.user:
    return redirect(url_for('main.index'))

  db.session.delete(item)
  flash('Your item has been deleted.')
  return redirect(url_for('main.index'))

@main.route('/search_results/<query>')
def search_results(query):
  res = Item.query.search(query).order_by(Item.timestamp.desc()).limit(50).all()
  return render_template('search_results.html', query=query, items=res)

