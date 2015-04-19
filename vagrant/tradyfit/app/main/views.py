# -*- coding: utf-8 -*-
from datetime import datetime
from flask import current_app, render_template, flash, redirect, url_for, \
request, abort
from flask.ext.login import current_user, login_required
from . import main
from .. import db
from .forms import UserForm, DeleteUserForm, ItemForm, SearchForm
from ..models import Item, Category
from ..helpers import save_item_image, delete_item_image
from ..geolocation import Geolocation


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


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
  items = current_user.items
  form = UserForm(user=current_user)

  if form.validate_on_submit():
    #if address has changed update user coordinates (lat,lon)
    address = Geolocation.create_address(form.city.data, form.state.data,
                            form.country.data)
    current_user.modify_geolocation(address)

    current_user.username = form.username.data
    current_user.name = form.name.data
    current_user.country = form.country.data
    current_user.state = form.state.data
    current_user.city = form.city.data
    db.session.add(current_user)
    flash('Your profile has been updated.')
    return redirect(url_for('main.profile'))
  form.username.data = current_user.username
  form.name.data = current_user.name
  form.country.data = current_user.country
  form.state.data = current_user.state
  form.city.data = current_user.city
  return render_template('profile.html', form=form, items=items)


@main.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
  form = DeleteUserForm()
  if form.validate_on_submit():
    try:
      db.session.delete(current_user)
      flash('We are sorry to see you go...')
    except:
      flash('Sorry, there was a problem deleting your account. Try again later')
    return redirect(url_for('main.index'))
  return render_template('delete_account.html', form=form)


@main.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  if not current_user.has_coordinates:
    flash('Before creating an item, you should have a valid location')
    return redirect(url_for('main.profile'))

  form = ItemForm()

  if form.validate_on_submit():
    #if the filename attribute is empty, assign the default image
    if not (hasattr(form.image.data, 'filename') and form.image.data.filename):
      image = current_app.config["DEFAULT_ITEM"]
    else:
      image = save_item_image(form.image)

    if image:
      category = Category.query.get(form.category.data)
      location = current_user.get_point_coordinates()
      item = Item(name=form.name.data, description=form.description.data,
                  price=form.price.data, category=category, image_url=image,
                  user_id=current_user.id, location=location,
                  country=current_user.country, state=current_user.state,
                  city=current_user.city)
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
  try:
    db.session.delete(item)
    flash('Your item has been deleted.')
  except:
    flash('Sorry, there was a problem deleting your item. Try again later.')
    return redirect(url_for('main.item', id=item.id))
  return redirect(url_for('main.index'))


@main.route('/search_results/<query>')
def search_results(query):
  if current_user.is_authenticated() and current_user.has_coordinates():
    user_loc = current_user.get_point_coordinates()
    res = Item.query.search(query).order_by(
                  Item.location.distance_box(user_loc)).limit(50).all()
  else:
    res = Item.query.search(query).order_by(
                  Item.timestamp.desc()).limit(50).all()
  return render_template('search_results.html', query=query, items=res)

