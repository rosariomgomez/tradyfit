# -*- coding: utf-8 -*-
from flask import jsonify
from . import public_api

def bad_request(message):
  response = jsonify({'error': 'bad request', 'message': message})
  response.status_code = 400
  return response

@public_api.errorhandler(429)
def ratelimit_handler(e):
  response = jsonify({ 'error': 'ratelimit exceeded',
                       'message': str(e.description) })
  response.status_code = 429
  return response