# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask.ext.login import current_user, login_required
from . import msg
from .. import db
from .forms import MessageForm
from ..models import Item, Message


@msg.route('/msg/create/<int:id>', methods=['GET', 'POST'])
@login_required
def create(id): # pylint: disable=W0622
  item = Item.query.get_or_404(id)
  form = MessageForm()

  if form.validate_on_submit():
    msg = Message(subject=form.subject.data, description=form.description.data,
                  sender_id=current_user.id, receiver_id=item.user_id,
                  item_id=item.id)
    db.session.add(msg)
    db.session.commit()
    flash('Your message has been sent.')
    return redirect(url_for('main.item', id=item.id))
  form.subject.data = "Hi! I'm interested on your " + item.name
  return render_template('msg/create.html', form=form, item=item)


@msg.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
  #number of messages of each type
  num_unread = len(current_user.msgs_unread)
  num_sent = current_user.msgs_sent.count()
  num_received = current_user.msgs_received.count()

  if request.method == 'POST':
    if request.form.get('type') == 'unread':
      msgs = current_user.msgs_unread
      n_type = 'Unread'
    elif request.form.get('type') == 'sent':
      msgs = current_user.msgs_sent.order_by(Message.timestamp.desc()).all()
      n_type = 'Sent'
    else:
      msgs = current_user.msgs_received.order_by(Message.timestamp.desc()).all()
      n_type = 'Received'
    return jsonify(type=n_type, msgs=[msg.serialize for msg in msgs],
                    num_unread=num_unread, num_sent=num_sent,
                    num_received=num_received)
  else: #GET request
    msgs = current_user.msgs_unread
    return render_template('msg/notifications.html', msgs=msgs,
                    num_unread=num_unread, num_sent=num_sent,
                    num_received=num_received)


@msg.route('/msg/<int:id>', methods=['GET', 'POST'])
@login_required
def message(id): # pylint: disable=W0622
  msg = Message.query.get_or_404(id)
  if not (current_user == msg.receiver or current_user == msg.sender):
    return redirect(url_for('main.index'))

  #mark message as read if user is the receiver
  if current_user == msg.receiver and msg.unread:
    msg.unread = False
    db.session.add(msg)
    db.session.commit()

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
      db.session.commit()
      flash('Your message has been sent.')
      return redirect(url_for('msg.notifications'))
  form.subject.data = "Re: " + msg.subject
  return render_template('msg/message.html', msg=msg, item=msg.item, form=form)

