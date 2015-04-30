# -*- coding: utf-8 -*-
from flask import jsonify, request, current_app
from . import public_api
from .. import opbeat
from app.auth.views import get_ip

def bad_request(message):
  response = jsonify({'error': 'bad request', 'message': message})
  response.status_code = 400
  return response

@public_api.errorhandler(429)
def ratelimit_handler(e):
  #log rate limit with resource path and IP
  if not current_app.testing:
    opbeat.captureMessage(
      "Rate limit: {} from resource {} from IP {}".format(
                          str(e.description), request.path, get_ip() or 'None'))

  response = jsonify({ 'error': 'ratelimit exceeded',
                       'message': str(e.description) })
  response.status_code = 429
  return response