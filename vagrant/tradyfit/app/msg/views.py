# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask.ext.login import current_user, login_required
from . import msg
from .. import db
from .forms import MessageForm
from ..models import Item, Message


@msg.route('/msg/create/<int:id>', methods=['GET', 'POST'])
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


@msg.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():

  if request.method == 'POST':
    if request.form.get('type') == 'unread':
      msgs = current_user.msgs_unread
    elif request.form.get('type') == 'sent':
      msgs = current_user.msgs_sent.all()
    else:
      msgs = current_user.msgs_received.all()
    return jsonify(msgs=[msg.serialize for msg in msgs])

  else: #GET request
    msgs = current_user.msgs_unread
    return render_template('msg/notifications.html', msgs=msgs)


@msg.route('/msg/<int:id>', methods=['GET', 'POST'])
@login_required
def message(id):
  msg = Message.query.get_or_404(id)
  if not (current_user == msg.receiver or current_user == msg.sender):
    return redirect(url_for('main.index'))

  #mark message as read if user is the receiver
  if current_user == msg.receiver and msg.unread:
    msg.unread = False

  form = MessageForm()
  #do not reply messages to deleted user accounts, to same user or
  #regarding a product that has been deleted
  if msg.item and msg.sender and current_user != msg.sender:
    if form.validate_on_submit():
      reply = Message(subject=form.subject.data,
                      description=form.description.data,
                      sender_id=current_user.id, receiver_id=msg.sender_id,
                      item_id=msg.item_id)
      db.session.add(reply)
      flash('Your message has been sent.')
      return redirect(url_for('msg.notifications'))
  form.subject.data = "Re: " + msg.subject
  return render_template('msg/message.html', msg=msg, form=form)

