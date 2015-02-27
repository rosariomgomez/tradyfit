# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SelectField, SubmitField, \
TextAreaField, DecimalField, ValidationError
from wtforms.validators import Required, Length, NumberRange, Regexp
from ..models import Category, Item


class ItemForm(Form):
  name = StringField('Name', validators = 
                                [ Required(), Length(3, 80), 
                                  Regexp('^[A-Za-z][. \w]+$', 0,
                                  'Product names must have only letters,'
                                  ' numbers, dots or underscores')])
  description = TextAreaField('Description', validators=[Length(0,500)])
  price = DecimalField('Price', default=0, places=2, 
                        validators= [NumberRange(0, 10**10-1)])
  category = SelectField('Category', coerce=int)
  submit = SubmitField('Submit')

  def __init__(self, *args, **kwargs):
    super(ItemForm, self).__init__(*args, **kwargs)
    self.category.choices = Category.get_category_choices()