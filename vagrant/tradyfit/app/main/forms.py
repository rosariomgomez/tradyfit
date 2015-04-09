# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SelectField, SubmitField, \
TextAreaField, DecimalField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import Required, Length, NumberRange, Regexp
from ..models import Category, Item


class ItemForm(Form):
  name = StringField('Name', validators =
                                [ Required(), Length(3, 80),
                                  Regexp('^[A-Za-z0-9][.\- \w]+$', 0,
                                  'Product names must have only letters,'
                                  ' numbers, dots, dashes or underscores')])
  description = TextAreaField('Description', validators=[Length(0,500)])
  price = DecimalField('Price', default=0, places=2,
                        validators= [NumberRange(0, 10**10-1)])
  category = SelectField('Category', coerce=int)
  image = FileField('Image', validators=[
                    FileAllowed(['jpg', 'jpeg', 'png', 'gif'],
                      'Only jpg, png and gif files allowed')])
  submit = SubmitField('Submit')

  def __init__(self, *args, **kwargs):
    super(ItemForm, self).__init__(*args, **kwargs)
    self.category.choices = Category.get_category_choices()

  def validate_image(self, field):
    '''make sure that if image field contains info it is a file'''
    if field.data:
      fr = FileRequired('Image should be a file')
      fr(self, field)

class SearchForm(Form):
  search = StringField('What are you looking for?',
                        validators=[ Required(), Length(3, 80),
                                Regexp('^[A-Za-z][.\- \w]+$', 0,
                                'Search must have only letters,'
                                ' numbers, dots, dashes or underscores')])
  submit = SubmitField('Search')