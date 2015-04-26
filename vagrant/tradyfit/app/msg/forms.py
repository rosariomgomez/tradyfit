# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Required, Length


class MessageForm(Form):
  subject = TextAreaField('Subject (*)', validators=[Required(), Length(2,120)])
  description = TextAreaField('Description', validators=[Length(0,500)])
  submit = SubmitField('Send')
