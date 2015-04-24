# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SelectField, SubmitField, \
TextAreaField, DecimalField, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import Required, Length, NumberRange, Regexp
from ..models import Category, User, Country, State
# pylint: disable=E1002

class UserForm(Form):
  username = StringField('Username', validators=[
                      Required(), Length(3, 64), Regexp('^[A-Za-z][.\w]+$', 0,
                      'Username must have only letters, numbers, dots or '
                      'underscores')])

  name = StringField('Name', validators=[
                      Required(), Length(3, 64), Regexp('^[A-Za-z][. \w]+$', 0,
                      'Name must have only letters, numbers, dots or '
                      'underscores')])

  country = SelectField('Country')

  state = SelectField('State (only US)')

  city = StringField('City', validators=[
                      Required(), Length(2, 50), Regexp('^[A-Za-z][ A-Za-z]+$',
                      0, 'City must have only letters')])

  submit = SubmitField('Update')

  def __init__(self, user, *args, **kwargs):
    super(UserForm, self).__init__(*args, **kwargs)
    self.country.choices = Country.get_country_choices()
    self.state.choices = [('NU', 'Not US')] + State.get_us_state_choices()
    self.user = user

  def validate_username(self, field):
    if field.data != self.user.username and \
    User.get_user_by_username(field.data):
      raise ValidationError('Username already in use.')


class DeleteUserForm(Form):
  submit = SubmitField('Delete account')


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
  image = FileField('Image (max. size: 3MB)', validators=[
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
                                Regexp('^[A-Za-z0-9][.\- \w]+$', 0,
                                'Search must have only letters,'
                                ' numbers, dots, dashes or underscores')])
  submit = SubmitField('Search')
