from flask import redirect, url_for
from functools import wraps
from flask.ext.login import current_user


def admin_required(f):
  @wraps(f)
  def wrapped(*args, **kwargs):
    if not (current_user.is_authenticated() and current_user.is_admin):
      return redirect(url_for('main.index'))
    return f(*args, **kwargs)
  return wrapped