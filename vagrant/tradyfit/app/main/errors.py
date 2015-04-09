# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for
from . import main


@main.app_errorhandler(413)
def request_entity_too_large(e):
  '''redirect to create item form if a user tries to upload
  an image bigger than 3MB'''
  flash('Image should be less than 3MB.')
  return redirect(url_for('main.create'))


@main.app_errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
  return render_template('500.html'), 500