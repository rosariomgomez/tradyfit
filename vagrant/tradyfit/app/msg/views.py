# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for
from flask.ext.login import current_user, login_required
from . import msg
from .. import db
from .forms import MessageForm
from ..models import Item, Message


@msg.route('/create/<int:id>', methods=['GET', 'POST'])
@login_required
def create(id):
  item = Item.query.get_or_404(id)
  form = MessageForm()

  if form.validate_on_submit():
    msg = Message(subject=form.subject.data, description=form.description.data,
                  sender_id=current_user.id, receiver_id=item.user_id,
                  item_id=item.id)
    db.session.add(msg)
    flash('Your message has been sent.')
    return redirect(url_for('main.item', id=item.id))
  return render_template('msg/create.html', form=form, item=item)