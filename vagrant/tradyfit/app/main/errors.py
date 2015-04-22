# -*- coding: utf-8 -*-
from flask import render_template, request, jsonify
from . import main
# pylint: disable=W0613

@main.app_errorhandler(413)
def request_entity_too_large(e):
  '''redirect to create item form if a user tries to upload
  an image bigger than 3MB'''
  return render_template('413.html'), 413


@main.app_errorhandler(404)
def page_not_found(e):
  if request.accept_mimetypes.accept_json and \
      not request.accept_mimetypes.accept_html:
    response = jsonify({'error': 'not found'})
    response.status_code = 404
    return response
  return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
  if request.accept_mimetypes.accept_json and \
      not request.accept_mimetypes.accept_html:
    response = jsonify({'error': 'internal server error'})
    response.status_code = 500
    return response
  return render_template('500.html'), 500