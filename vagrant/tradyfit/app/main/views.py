from datetime import datetime
from flask import current_app, render_template, flash, redirect, url_for
from . import main
from .. import db
from .forms import ItemForm
from ..models import Item, Category

@main.route('/')
def index():
	items = Item.query.order_by(Item.timestamp.desc()).all()
	return render_template('index.html', items=items)

@main.route('/create/', methods=['GET', 'POST'])
def create():
	form = ItemForm()
	if form.validate_on_submit():
		category = Category.query.get(form.category.data)
		item = Item(name=form.name.data, description=form.description.data,
					price=form.price.data, category=category)
		db.session.add(item)
		flash('Your item has been created.')
		return redirect(url_for('main.index'))
	return render_template('create.html', form=form)

@main.route('/item/<int:id>')
def item(id):
	item = Item.query.get_or_404(id)
	return render_template('item.html', item=item)

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
	item = Item.query.get_or_404(id)
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
def delete(id):
	item = Item.query.get_or_404(id)
	db.session.delete(item)
	flash('Your item has been deleted.')
	return redirect(url_for('main.index'))





