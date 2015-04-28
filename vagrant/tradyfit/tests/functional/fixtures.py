# -*- coding: utf-8 -*-
from app import db
from app.models import Category, Item, Message


def create_item(user, name, category, image_url):
  c = Category.get_category(category)
  location = user.get_point_coordinates()
  item = Item(name=name, description='some text', price=23,
              category_id=c.id, image_url=image_url, user_id=user.id,
              location=location, country=user.country, state=user.state,
              city=user.city)
  db.session.add(item)
  db.session.commit()
  return item


def create_message(sender, receiver, item):
  msg = Message(subject='Hi there!', description='some text',
                sender_id=sender, receiver_id=receiver, item_id=item)
  db.session.add(msg)
  db.session.commit()

