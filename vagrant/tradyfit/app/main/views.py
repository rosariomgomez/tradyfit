# -*- coding: utf-8 -*-
from datetime import datetime
from flask import current_app, render_template, flash, redirect, url_for, \
request, abort
from flask.ext.login import current_user, login_required
from . import main
from .. import db
from .forms import ItemForm, SearchForm
from .helpers import save_item_image, delete_item_image
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
    #if the filename attribute is empty, assign the default image
    if not (hasattr(form.image.data, 'filename') and form.image.data.filename):
      image = current_app.config["DEFAULT_ITEM"]
    else:
      image = save_item_image(form.image)

    if image:
      category = Category.query.get(form.category.data)
      item = Item(name=form.name.data, description=form.description.data,
                  price=form.price.data, category=category, image_url=image,
                  user_id=current_user.id)
      db.session.add(item)
      flash('Your item has been created.')
      return redirect(url_for('main.index'))
    else:
      flash('Sorry, there was a problem creating your item. Try again later.')
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
    #included new image in form and is a file
    if hasattr(form.image.data, 'filename') and form.image.data.filename:
      image = save_item_image(form.image) #save new image
      if image is None: #problem uploading new image
        flash('Sorry, there was an error updating your item. Try again later.')
        return redirect(url_for('main.item', id=item.id))
      elif not delete_item_image(item.image_url): #delete previous image
        delete_item_image(image) #delete the new image
        flash('Sorry, there was an error updating your item. Try again later.')
        return redirect(url_for('main.item', id=item.id))
    else: #image not modified
      image = item.image_url

    item.name = form.name.data
    item.description = form.description.data
    item.price = form.price.data
    item.image_url = image
    item.category = Category.query.get(form.category.data)
    item.modified = datetime.utcnow()
    db.session.add(item)
    flash('Your item has been updated.')
    return redirect(url_for('main.item', id=item.id))

  form.name.data = item.name
  form.description.data = item.description
  form.price.data = item.price
  form.category.data = item.category.id
  return render_template('edit_item.html', form=form, id=item.id,
                          image=item.image())

@main.route('/delete/<int:id>')
@login_required
def delete(id):
  item = Item.query.get_or_404(id)
  if current_user != item.user:
    return redirect(url_for('main.index'))

  #before deleting the item from DB, remove image from S3
  if delete_item_image(item.image_url):
    db.session.delete(item)
    flash('Your item has been deleted.')
  else:
    flash('Sorry, there was a problem deleting your item. Try again later.')
    return redirect(url_for('main.item', id=item.id))
  return redirect(url_for('main.index'))

@main.route('/search_results/<query>')
def search_results(query):
  res = Item.query.search(query).order_by(Item.timestamp.desc()).limit(50).all()
  return render_template('search_results.html', query=query, items=res)

