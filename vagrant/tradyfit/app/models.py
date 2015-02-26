from . import db
from datetime import datetime
import os


class Category(db.Model):
	__tablename__ = 'categories'
	id    = db.Column(db.Integer, primary_key=True)
	name  = db.Column(db.String, unique=True, index=True)
	items = db.relationship('Item', backref='category') 

	@staticmethod
	def insert_categories():
		path = os.path.dirname(os.path.abspath(__file__))
		f = os.path.join(path,"files/categories.txt")
		with open(f, "r") as categories:
			for category in categories: #read each line
				category = category.rstrip('\n')
				c = Category.query.filter_by(name=category).first()
				if c is None: #not in db yet
					category = Category(name=category)
					db.session.add(category)
		db.session.commit()

	@staticmethod
	def get_category_choices():
		'''return a list with tuples (category_code, name) with 
		all categories for populate form choices'''
		categories = Category.query.all()
		return [(c.id, c.name) for c in categories]


class Item(db.Model):
	__tablename__ = 'items'
	id    = db.Column(db.Integer, primary_key=True)
	name  = db.Column(db.String(80), nullable=False)
	description = db.Column(db.Text)
	price = db.Column(db.Numeric(precision=10, scale=2))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	modified = db.Column(db.DateTime, index=True)
	category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))