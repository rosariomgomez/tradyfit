# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Required, Length, Regexp


class MessageForm(Form):
  subject = TextAreaField('Subject (*)', validators=[Required(), Length(3,120),
                            Regexp('^[A-Za-z0-9][.\-\:\!\' \w]+$', 0,
                                  'Subject must have only letters,'
                                  ' numbers, dots, dashes or underscores')])
  description = TextAreaField('Description', validators=[Length(0,500)])
  submit = SubmitField('Send')
